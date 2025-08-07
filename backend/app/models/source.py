"""Source document model for MongoDB using Beanie ODM."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, HttpUrl


class Source(Document):
    """Source document model for legal documents and references."""
    
    # Core document info
    title: str = Field(..., description="Title of the source document")
    filename: Optional[str] = Field(default=None, description="Original filename")
    file_type: str = Field(..., description="File type: pdf, docx, txt, url, etc.")
    
    # File storage
    file_path: Optional[str] = Field(default=None, description="Path to stored file")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    file_hash: Optional[str] = Field(default=None, description="SHA-256 hash of file content")
    
    # URL sources
    url: Optional[HttpUrl] = Field(default=None, description="URL if this is a web source")
    
    # Content
    content: Optional[str] = Field(default=None, description="Extracted text content")
    content_preview: Optional[str] = Field(default=None, description="First 500 chars for preview")
    page_count: Optional[int] = Field(default=None, description="Number of pages (for PDFs)")
    
    # Metadata
    author: Optional[str] = Field(default=None, description="Document author")
    publication_date: Optional[datetime] = Field(default=None, description="When document was published")
    source_type: str = Field(default="document", description="Type: document, case_law, statute, regulation, etc.")
    
    # User context
    user_id: Indexed(str) = Field(..., description="User who uploaded/added this source")
    
    # Processing status
    processing_status: str = Field(default="pending", description="Status: pending, processing, completed, error")
    processing_error: Optional[str] = Field(default=None, description="Error message if processing failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Classification and tags
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    category: Optional[str] = Field(default=None, description="Document category")
    jurisdiction: Optional[str] = Field(default=None, description="Legal jurisdiction")
    
    # Search and indexing
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords for search")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional document metadata")
    
    class Settings:
        name = "sources"
        indexes = [
            [("user_id", 1), ("created_at", -1)],    # User's sources
            [("file_hash", 1)],                       # Deduplication
            [("processing_status", 1)],               # Processing queue
            [("source_type", 1), ("jurisdiction", 1)], # Legal categorization
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Smith v. Johnson - Supreme Court Decision",
                "filename": "smith_v_johnson_2024.pdf",
                "file_type": "pdf",
                "file_size": 1024000,
                "content_preview": "In the matter of Smith v. Johnson, the court finds...",
                "page_count": 25,
                "author": "Supreme Court of Appeals",
                "source_type": "case_law",
                "jurisdiction": "New York",
                "user_id": "user_123",
                "processing_status": "completed",
                "tags": ["contract-law", "appeal", "precedent"]
            }
        }