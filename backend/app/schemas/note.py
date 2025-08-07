"""Note API schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """Schema for creating a new note."""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content (supports markdown)")
    research_id: Optional[str] = Field(None, description="Associated research ID")
    source_id: Optional[str] = Field(None, description="Associated source ID")
    source_page: Optional[int] = Field(None, ge=1, description="Source page number")
    source_quote: Optional[str] = Field(None, description="Quoted text from source")
    note_type: str = Field(default="general", description="Note type")
    category: Optional[str] = Field(None, description="Note category")
    tags: List[str] = Field(default_factory=list, description="Note tags")
    is_pinned: bool = Field(default=False, description="Whether note is pinned")
    parent_note_id: Optional[str] = Field(None, description="Parent note ID")


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    source_id: Optional[str] = Field(None)
    source_page: Optional[int] = Field(None, ge=1)
    source_quote: Optional[str] = Field(None)
    note_type: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(None)
    is_pinned: Optional[bool] = Field(None)
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")


class NoteResponse(BaseModel):
    """Schema for note responses."""
    id: str = Field(..., description="Note ID")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    user_id: str = Field(..., description="Owner user ID")
    
    # Associations
    research_id: Optional[str] = Field(None, description="Associated research ID")
    source_id: Optional[str] = Field(None, description="Associated source ID")
    source_page: Optional[int] = Field(None, description="Source page reference")
    source_quote: Optional[str] = Field(None, description="Quoted source text")
    
    # Classification
    note_type: str = Field(..., description="Note type")
    category: Optional[str] = Field(None, description="Note category")
    tags: List[str] = Field(..., description="Note tags")
    
    # Organization
    is_pinned: bool = Field(..., description="Whether note is pinned")
    is_private: bool = Field(..., description="Whether note is private")
    status: str = Field(..., description="Note status")
    
    # Hierarchy
    parent_note_id: Optional[str] = Field(None, description="Parent note ID")
    linked_note_ids: List[str] = Field(..., description="Linked note IDs")
    
    # Metadata
    word_count: Optional[int] = Field(None, description="Word count")
    reading_time_minutes: Optional[int] = Field(None, description="Reading time")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "note_123",
                "title": "Contract Interpretation Key Points",
                "content": "The court emphasized that contracts must be interpreted...",
                "user_id": "user_123",
                "research_id": "research_123",
                "source_id": "source_456",
                "source_page": 15,
                "note_type": "analysis",
                "category": "contract-law",
                "tags": ["interpretation", "precedent"],
                "is_pinned": True,
                "status": "published",
                "created_at": "2024-01-15T10:00:00Z"
            }
        }


class NoteListResponse(BaseModel):
    """Schema for paginated note list responses."""
    notes: List[NoteResponse] = Field(..., description="List of notes")
    total: int = Field(..., description="Total number of notes")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class NoteLinkUpdate(BaseModel):
    """Schema for updating note relationships."""
    linked_note_ids: List[str] = Field(..., description="IDs of notes to link")


class NoteSearchRequest(BaseModel):
    """Schema for note search requests."""
    query: str = Field(..., min_length=1, description="Search query")
    note_type: Optional[str] = Field(None, description="Filter by note type")
    category: Optional[str] = Field(None, description="Filter by category")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    research_id: Optional[str] = Field(None, description="Filter by research")
    source_id: Optional[str] = Field(None, description="Filter by source")