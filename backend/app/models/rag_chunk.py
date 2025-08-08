"""
RAG Document Chunk Models
Pydantic models for document chunks in the RAG system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from beanie import Document, Indexed
from pydantic import BaseModel, Field
import pymongo


class ChunkType(str, Enum):
    """Chunk type enum."""
    TEXT = "text"
    TABLE = "table"
    HEADER = "header"
    FOOTER = "footer"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    OTHER = "other"


class ChunkMetadata(BaseModel):
    """Chunk-specific metadata."""
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    paragraph_index: Optional[int] = None
    sentence_count: int = 0
    word_count: int = 0
    char_count: int = 0
    language: Optional[str] = None
    confidence_score: Optional[float] = None  # OCR or extraction confidence
    extraction_method: Optional[str] = None  # How the text was extracted
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class RAGChunk(Document):
    """
    Document chunk model for RAG system.
    Stores individual text chunks with metadata for vector search.
    """
    
    # Core relationships
    document_id: Indexed(str)  # Reference to parent RAGDocument
    user_id: Indexed(str)  # User who owns this chunk (for isolation)
    
    # Chunk identification
    chunk_index: int  # Order within the document
    chunk_id: str  # Unique identifier: f"{document_id}_{chunk_index}"
    
    # Content
    text: str  # The actual text content
    text_hash: str  # SHA256 hash of the text for deduplication
    chunk_type: ChunkType = ChunkType.TEXT
    
    # Chunking information
    start_char_index: Optional[int] = None
    end_char_index: Optional[int] = None
    overlap_with_previous: int = 0  # Characters overlapping with previous chunk
    overlap_with_next: int = 0  # Characters overlapping with next chunk
    
    # Metadata
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata)
    
    # Vector information
    embedding_vector: Optional[List[float]] = None  # Stored only if needed
    qdrant_point_id: Optional[str] = None  # ID in Qdrant vector DB
    embedding_model: Optional[str] = None
    embedding_created_at: Optional[datetime] = None
    
    # Quality metrics
    processing_quality_score: Optional[float] = None
    readability_score: Optional[float] = None
    completeness_score: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Processing information
    processed_by_version: Optional[str] = None  # Version of processing pipeline
    reprocessing_needed: bool = False
    
    class Settings:
        name = "rag_chunks"
        indexes = [
            [
                ("document_id", pymongo.ASCENDING),
                ("chunk_index", pymongo.ASCENDING)
            ],
            [
                ("user_id", pymongo.ASCENDING),
                ("document_id", pymongo.ASCENDING)
            ],
            [("text_hash", pymongo.ASCENDING)],  # For deduplication
            [("qdrant_point_id", pymongo.ASCENDING)],
            [
                ("user_id", pymongo.ASCENDING),
                ("chunk_type", pymongo.ASCENDING)
            ],
            [("created_at", pymongo.DESCENDING)],
            # Compound index for search
            [
                ("user_id", pymongo.ASCENDING),
                ("metadata.page_number", pymongo.ASCENDING),
                ("chunk_index", pymongo.ASCENDING)
            ],
            # Text search index
            [("text", pymongo.TEXT), ("metadata.section_title", pymongo.TEXT)],
        ]

    @classmethod
    async def find_by_document(cls, document_id: str, user_id: str = None):
        """Find all chunks for a specific document."""
        query = cls.document_id == document_id
        if user_id:
            query = query & (cls.user_id == user_id)
        return await cls.find(query).sort(cls.chunk_index).to_list()

    @classmethod
    async def find_by_text_hash(cls, text_hash: str):
        """Find chunk by text hash (for deduplication)."""
        return await cls.find_one(cls.text_hash == text_hash)

    @classmethod
    async def find_user_chunks(cls, user_id: str, limit: int = 100, skip: int = 0):
        """Find chunks for a specific user with pagination."""
        return await cls.find(
            cls.user_id == user_id
        ).sort(-cls.created_at).limit(limit).skip(skip).to_list()

    @classmethod
    async def find_chunks_by_page(cls, document_id: str, page_number: int, user_id: str = None):
        """Find chunks from a specific page."""
        query = (cls.document_id == document_id) & (cls.metadata.page_number == page_number)
        if user_id:
            query = query & (cls.user_id == user_id)
        return await cls.find(query).sort(cls.chunk_index).to_list()

    @classmethod
    async def count_by_document(cls, document_id: str, user_id: str = None):
        """Count chunks for a specific document."""
        query = cls.document_id == document_id
        if user_id:
            query = query & (cls.user_id == user_id)
        return await cls.find(query).count()

    @classmethod
    async def delete_by_document(cls, document_id: str, user_id: str = None):
        """Delete all chunks for a specific document."""
        query = cls.document_id == document_id
        if user_id:
            query = query & (cls.user_id == user_id)
        return await cls.find(query).delete()

    async def mark_embedding_created(self, qdrant_point_id: str, embedding_model: str):
        """Mark chunk as having embeddings created."""
        self.qdrant_point_id = qdrant_point_id
        self.embedding_model = embedding_model
        self.embedding_created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    def get_word_count(self) -> int:
        """Get word count from text."""
        if self.metadata.word_count > 0:
            return self.metadata.word_count
        return len(self.text.split())

    def get_char_count(self) -> int:
        """Get character count from text."""
        if self.metadata.char_count > 0:
            return self.metadata.char_count
        return len(self.text)

    def calculate_quality_metrics(self):
        """Calculate basic quality metrics for the chunk."""
        # Simple readability based on sentence and word length
        sentences = self.text.split('.')
        words = self.text.split()
        
        if len(words) > 0:
            avg_words_per_sentence = len(words) / max(len(sentences), 1)
            avg_chars_per_word = len(self.text.replace(' ', '')) / len(words)
            
            # Simple readability score (higher is more readable)
            self.readability_score = min(1.0, 1.0 / (1.0 + abs(avg_words_per_sentence - 15) / 10.0))
            
            # Completeness based on presence of sentence endings
            complete_sentences = len([s for s in sentences if s.strip()])
            self.completeness_score = complete_sentences / max(len(sentences), 1)
        
        # Overall processing quality (can be enhanced)
        quality_factors = [
            1.0 if self.text.strip() else 0.0,  # Has content
            1.0 if len(self.text.split()) >= 5 else 0.5,  # Minimum word count
            self.readability_score or 0.5,
            self.completeness_score or 0.5,
        ]
        
        self.processing_quality_score = sum(quality_factors) / len(quality_factors)

    def should_reprocess(self, current_version: str) -> bool:
        """Check if chunk should be reprocessed."""
        return (
            self.reprocessing_needed or 
            self.processed_by_version != current_version or
            self.processing_quality_score is None or
            self.processing_quality_score < 0.5
        )