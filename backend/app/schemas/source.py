"""Source document API schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class SourceCreate(BaseModel):
    """Schema for creating a new source document."""
    title: str = Field(..., min_length=1, max_length=300, description="Document title")
    file_type: str = Field(..., description="File type: pdf, docx, txt, url, etc.")
    url: Optional[HttpUrl] = Field(None, description="URL if this is a web source")
    source_type: str = Field(default="document", description="Type: document, case_law, statute, etc.")
    author: Optional[str] = Field(None, max_length=200, description="Document author")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    category: Optional[str] = Field(None, description="Document category")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction")
    tags: List[str] = Field(default_factory=list, description="Document tags")


class SourceUpdate(BaseModel):
    """Schema for updating source document metadata."""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    author: Optional[str] = Field(None, max_length=200)
    publication_date: Optional[datetime] = Field(None)
    category: Optional[str] = Field(None)
    jurisdiction: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(None)
    source_type: Optional[str] = Field(None)


class SourceResponse(BaseModel):
    """Schema for source document responses."""
    id: str = Field(..., description="Source ID")
    title: str = Field(..., description="Document title")
    filename: Optional[str] = Field(None, description="Original filename")
    file_type: str = Field(..., description="File type")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    url: Optional[HttpUrl] = Field(None, description="URL if web source")
    
    # Content
    content_preview: Optional[str] = Field(None, description="Content preview")
    page_count: Optional[int] = Field(None, description="Number of pages")
    
    # Metadata
    author: Optional[str] = Field(None, description="Document author")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    source_type: str = Field(..., description="Source type")
    category: Optional[str] = Field(None, description="Category")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    
    # User and processing
    user_id: str = Field(..., description="Owner user ID")
    processing_status: str = Field(..., description="Processing status")
    processing_error: Optional[str] = Field(None, description="Processing error")
    
    # Organization
    tags: List[str] = Field(..., description="Tags")
    keywords: List[str] = Field(..., description="Keywords")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "source_123",
                "title": "Smith v. Johnson - Court Decision",
                "filename": "smith_v_johnson.pdf",
                "file_type": "pdf",
                "file_size": 1024000,
                "content_preview": "In the matter of Smith v. Johnson...",
                "page_count": 25,
                "author": "Supreme Court",
                "source_type": "case_law",
                "jurisdiction": "New York",
                "user_id": "user_123",
                "processing_status": "completed",
                "tags": ["contract", "precedent"],
                "created_at": "2024-01-15T10:00:00Z"
            }
        }


class SourceListResponse(BaseModel):
    """Schema for paginated source list responses."""
    sources: List[SourceResponse] = Field(..., description="List of sources")
    total: int = Field(..., description="Total number of sources")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")