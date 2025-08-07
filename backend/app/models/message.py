"""Message model for storing chat messages in MongoDB using Beanie ODM."""
from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import Field


class Message(Document):
    """Message document model for chat conversations."""
    
    # Core message data
    research_id: Indexed(str) = Field(..., description="ID of the research/conversation this message belongs to")
    content: str = Field(..., description="The actual message content")
    role: str = Field(..., description="Role: 'user', 'assistant', 'system'")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # User context
    user_id: Indexed(str) = Field(..., description="ID of the user who sent/received this message")
    
    # LLM response metadata (when role='assistant')
    model: Optional[str] = Field(default=None, description="Model used to generate response")
    tokens_used: Optional[int] = Field(default=None, description="Number of tokens consumed")
    response_time_ms: Optional[float] = Field(default=None, description="Time taken to generate response")
    
    # Additional context
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")
    
    # Message ordering
    sequence_number: int = Field(..., description="Order of message in conversation")
    
    # Status and flags
    is_hidden: bool = Field(default=False, description="Whether message is hidden from UI")
    is_error: bool = Field(default=False, description="Whether this is an error message")
    error_code: Optional[str] = Field(default=None, description="Error code if this is an error message")
    
    class Settings:
        name = "messages"
        indexes = [
            [("research_id", 1), ("sequence_number", 1)],  # For conversation ordering
            [("user_id", 1), ("created_at", -1)],          # For user's message history
            [("created_at", -1)],                           # For global chronological ordering
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "research_id": "research_123",
                "content": "What are the key precedents for contract interpretation in this jurisdiction?",
                "role": "user",
                "user_id": "user_123",
                "sequence_number": 1,
                "metadata": {"source_context": ["document_1", "document_2"]}
            }
        }