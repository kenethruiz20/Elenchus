"""Research/Conversation API schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ResearchCreate(BaseModel):
    """Schema for creating a new research/conversation."""
    title: str = Field(..., min_length=1, max_length=200, description="Title of the research")
    model: str = Field(default="gemini-1.5-flash", description="Model ID for the conversation")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=32000, description="Max tokens per response")


class ResearchUpdate(BaseModel):
    """Schema for updating research/conversation."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    model: Optional[str] = Field(None, description="Model ID for the conversation")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=32000, description="Max tokens per response")
    status: Optional[str] = Field(None, description="Status: active, archived, deleted")


class ResearchResponse(BaseModel):
    """Schema for research/conversation responses."""
    id: str = Field(..., description="Research ID")
    title: str = Field(..., description="Title of the research")
    user_id: str = Field(..., description="User ID who owns this research")
    model: str = Field(..., description="Model ID being used")
    status: str = Field(..., description="Research status")
    tags: List[str] = Field(..., description="Tags")
    
    # Related IDs
    source_ids: List[str] = Field(..., description="Associated source IDs")
    note_ids: List[str] = Field(..., description="Associated note IDs")
    
    # Settings
    temperature: float = Field(..., description="Model temperature")
    max_tokens: Optional[int] = Field(..., description="Max tokens")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Statistics (computed fields)
    message_count: Optional[int] = Field(None, description="Number of messages in conversation")
    last_activity: Optional[datetime] = Field(None, description="Last message timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "research_123",
                "title": "Contract Interpretation Analysis",
                "user_id": "user_123",
                "model": "gemini-1.5-pro",
                "status": "active",
                "tags": ["contract-law", "interpretation"],
                "source_ids": ["source_1", "source_2"],
                "note_ids": ["note_1"],
                "temperature": 0.7,
                "max_tokens": 4000,
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T15:30:00Z",
                "message_count": 12,
                "last_activity": "2024-01-15T15:25:00Z"
            }
        }


class ResearchListResponse(BaseModel):
    """Schema for paginated research list responses."""
    research: List[ResearchResponse] = Field(..., description="List of research items")
    total: int = Field(..., description="Total number of research items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class ResearchSourceUpdate(BaseModel):
    """Schema for updating research sources."""
    source_ids: List[str] = Field(..., description="List of source IDs to associate with research")


class ResearchNoteUpdate(BaseModel):
    """Schema for updating research notes."""
    note_ids: List[str] = Field(..., description="List of note IDs to associate with research")