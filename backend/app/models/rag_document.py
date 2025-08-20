"""
RAG Document Models
Pydantic models for document management in the RAG system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from beanie import Document, Indexed
from pydantic import BaseModel, Field
import pymongo


class DocumentStatus(str, Enum):
    """Document processing status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class DocumentType(str, Enum):
    """Document type enum."""
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    MARKDOWN = "md"
    OTHER = "other"


class DocumentMetadata(BaseModel):
    """Document metadata schema."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    # language field removed to avoid MongoDB text index conflicts
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    # AI-generated metadata
    ai_summary: Optional[str] = None  # Short description
    ai_detailed_description: Optional[str] = None  # Detailed description
    ai_topics: List[str] = Field(default_factory=list)  # Key topics
    ai_metadata_generated_at: Optional[datetime] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ProcessingMetrics(BaseModel):
    """Document processing metrics."""
    chunks_created: int = 0
    processing_time_seconds: float = 0.0
    embedding_time_seconds: float = 0.0
    upload_time_seconds: float = 0.0
    total_processing_time: float = 0.0
    errors_encountered: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class RAGDocument(Document):
    """
    Main document model for RAG system.
    Stores document metadata and processing information.
    """
    
    # Core fields
    user_id: Indexed(str)  # User who uploaded the document
    filename: str
    original_filename: str
    file_type: DocumentType
    file_size: int
    file_hash: str  # SHA256 hash for deduplication
    
    # Storage information
    gcs_path: Optional[str] = None  # Google Cloud Storage path
    local_path: Optional[str] = None  # Local file path (if applicable)
    
    # Processing status
    status: DocumentStatus = DocumentStatus.PENDING
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_job_id: Optional[str] = None  # Background job ID
    
    # Document content and metadata
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    processing_metrics: ProcessingMetrics = Field(default_factory=ProcessingMetrics)
    
    # RAG-specific information
    chunks_count: int = 0
    embeddings_created: bool = False
    qdrant_collection: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Tags and categorization
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    
    class Settings:
        name = "rag_documents"
        indexes = [
            [
                ("user_id", pymongo.ASCENDING),
                ("status", pymongo.ASCENDING),
                ("created_at", pymongo.DESCENDING)
            ],
            [("file_hash", pymongo.ASCENDING)],  # For deduplication
            [("processing_job_id", pymongo.ASCENDING)],
            [("gcs_path", pymongo.ASCENDING)],
            [
                ("user_id", pymongo.ASCENDING),
                ("file_type", pymongo.ASCENDING)
            ],
            # Text search index for filename and metadata - removed due to language field conflict
            # [("filename", pymongo.TEXT), ("metadata.title", pymongo.TEXT)],
        ]

    async def mark_processing_started(self, job_id: str = None):
        """Mark document as processing started."""
        self.status = DocumentStatus.PROCESSING
        self.processing_started_at = datetime.utcnow()
        if job_id:
            self.processing_job_id = job_id
        self.updated_at = datetime.utcnow()
        await self.save()

    async def mark_processing_completed(self, chunks_count: int, metrics: ProcessingMetrics):
        """Mark document as processing completed."""
        self.status = DocumentStatus.COMPLETED
        self.processing_completed_at = datetime.utcnow()
        self.chunks_count = chunks_count
        self.processing_metrics = metrics
        self.embeddings_created = True
        self.updated_at = datetime.utcnow()
        await self.save()

    async def mark_processing_failed(self, error_message: str):
        """Mark document as processing failed."""
        self.status = DocumentStatus.FAILED
        self.processing_completed_at = datetime.utcnow()
        if not self.processing_metrics.errors_encountered:
            self.processing_metrics.errors_encountered = []
        self.processing_metrics.errors_encountered.append(error_message)
        self.updated_at = datetime.utcnow()
        await self.save()

    @classmethod
    async def find_by_user_and_status(cls, user_id: str, status: DocumentStatus):
        """Find documents by user and status."""
        return await cls.find(cls.user_id == user_id, cls.status == status).to_list()

    @classmethod
    async def find_by_hash(cls, file_hash: str):
        """Find document by file hash (for deduplication)."""
        return await cls.find_one(cls.file_hash == file_hash)

    @classmethod
    async def find_user_documents(cls, user_id: str, limit: int = 50, skip: int = 0):
        """Find user documents with pagination."""
        return await cls.find(
            cls.user_id == user_id
        ).sort(-cls.created_at).limit(limit).skip(skip).to_list()

    def get_processing_duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.processing_started_at and self.processing_completed_at:
            return (self.processing_completed_at - self.processing_started_at).total_seconds()
        return None

    def is_processing_complete(self) -> bool:
        """Check if document processing is complete."""
        return self.status == DocumentStatus.COMPLETED and self.embeddings_created