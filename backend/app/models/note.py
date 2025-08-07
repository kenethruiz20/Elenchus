"""Note model for storing user notes and annotations in MongoDB using Beanie ODM."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field


class Note(Document):
    """Note document model for user annotations and research notes."""
    
    # Core note data
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Note content (supports markdown)")
    
    # User context
    user_id: Indexed(str) = Field(..., description="User who created this note")
    
    # Research context
    research_id: Optional[str] = Field(default=None, description="Associated research/conversation ID")
    
    # Source context
    source_id: Optional[str] = Field(default=None, description="Associated source document ID")
    source_page: Optional[int] = Field(default=None, description="Specific page reference (if applicable)")
    source_quote: Optional[str] = Field(default=None, description="Quoted text from source")
    
    # Note type and categorization
    note_type: str = Field(default="general", description="Type: general, annotation, summary, analysis, todo")
    category: Optional[str] = Field(default=None, description="User-defined category")
    
    # Organization
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    is_pinned: bool = Field(default=False, description="Whether note is pinned for quick access")
    is_private: bool = Field(default=True, description="Whether note is private to user")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Content metadata
    word_count: Optional[int] = Field(default=None, description="Word count of content")
    reading_time_minutes: Optional[int] = Field(default=None, description="Estimated reading time")
    
    # Relationships and references
    parent_note_id: Optional[str] = Field(default=None, description="Parent note ID (for hierarchical notes)")
    linked_note_ids: List[str] = Field(default_factory=list, description="IDs of linked/related notes")
    
    # Status
    status: str = Field(default="draft", description="Status: draft, published, archived")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional note metadata")
    
    class Settings:
        name = "notes"
        indexes = [
            [("user_id", 1), ("created_at", -1)],        # User's notes chronologically
            [("research_id", 1), ("created_at", 1)],     # Notes for specific research
            [("source_id", 1), ("source_page", 1)],      # Notes for specific source/page
            [("note_type", 1), ("category", 1)],         # Categorized notes
            [("is_pinned", -1), ("updated_at", -1)],     # Pinned notes first
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Key Precedent Analysis",
                "content": "The court's reasoning in this case establishes a new precedent for contract interpretation...",
                "user_id": "user_123",
                "research_id": "research_123",
                "source_id": "source_456",
                "source_page": 12,
                "source_quote": "The contract must be interpreted in light of the surrounding circumstances...",
                "note_type": "analysis",
                "category": "contract-law",
                "tags": ["precedent", "interpretation", "key-case"],
                "is_pinned": True,
                "status": "published"
            }
        }