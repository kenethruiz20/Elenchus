"""Research/Conversation model for MongoDB using Beanie ODM."""
from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed, Link
from pydantic import Field, BaseModel


class Research(Document):
    """Research/Conversation document model.
    
    Represents an LLM chat session with associated sources and notes.
    """
    
    # Core fields
    title: Indexed(str) = Field(..., description="Title of the research/conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # User relationship
    user_id: Indexed(str) = Field(..., description="ID of the user who owns this research")
    
    # Related documents (referenced by ObjectId)
    source_ids: List[str] = Field(default_factory=list, description="List of source document IDs")
    note_ids: List[str] = Field(default_factory=list, description="List of note document IDs")
    
    # LLM Configuration
    model: str = Field(default="gemini-1.5-flash", description="Model ID being used for the conversation")
    
    # Metadata
    status: str = Field(default="active", description="Status: active, archived, deleted")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    # Settings
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=32000)
    
    class Settings:
        name = "research"
        indexes = [
            [("user_id", 1), ("created_at", -1)],  # For user's research list
            [("status", 1), ("updated_at", -1)],    # For filtering by status
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Smith v. Johnson Appeal Research",
                "user_id": "user_123",
                "source_ids": ["source_1", "source_2"],
                "note_ids": ["note_1"],
                "model": "gemini-1.5-pro",
                "status": "active",
                "tags": ["litigation", "appeal", "contract-law"]
            }
        }