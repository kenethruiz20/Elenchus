"""Message API schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str = Field(..., min_length=1, description="Message content")
    role: str = Field(..., pattern="^(user|assistant|system)$", description="Message role")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    content: Optional[str] = Field(None, min_length=1, description="Updated message content")
    is_hidden: Optional[bool] = Field(None, description="Hide/show message in UI")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class MessageResponse(BaseModel):
    """Schema for message responses."""
    id: str = Field(..., description="Message ID")
    research_id: str = Field(..., description="Associated research ID")
    content: str = Field(..., description="Message content")
    role: str = Field(..., description="Message role: user, assistant, system")
    user_id: str = Field(..., description="User ID")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    
    # LLM metadata (for assistant messages)
    model: Optional[str] = Field(None, description="Model used for response")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    response_time_ms: Optional[float] = Field(None, description="Response generation time")
    
    # Ordering and status
    sequence_number: int = Field(..., description="Message order in conversation")
    is_hidden: bool = Field(..., description="Whether message is hidden")
    is_error: bool = Field(..., description="Whether this is an error message")
    error_code: Optional[str] = Field(None, description="Error code if applicable")
    
    # Additional context
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "message_123",
                "research_id": "research_123",
                "content": "Based on the documents provided, the key precedent is...",
                "role": "assistant",
                "user_id": "user_123",
                "created_at": "2024-01-15T10:30:00Z",
                "model": "gemini-1.5-pro",
                "tokens_used": 250,
                "response_time_ms": 1500.0,
                "sequence_number": 2,
                "is_hidden": False,
                "is_error": False,
                "metadata": {"confidence_score": 0.95}
            }
        }


class MessageListResponse(BaseModel):
    """Schema for paginated message list responses."""
    messages: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class ConversationResponse(BaseModel):
    """Schema for complete conversation responses."""
    research_id: str = Field(..., description="Research/conversation ID")
    research_title: str = Field(..., description="Research title")
    messages: List[MessageResponse] = Field(..., description="All messages in conversation")
    total_messages: int = Field(..., description="Total message count")
    model: str = Field(..., description="Current model being used")


class MessageSendRequest(BaseModel):
    """Schema for sending a message to the AI."""
    message: str = Field(..., min_length=1, max_length=10000, description="User message content")
    stream: bool = Field(default=False, description="Whether to stream the response")
    include_sources: bool = Field(default=True, description="Whether to include source context")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Override model temperature")


class MessageSendResponse(BaseModel):
    """Schema for message send response."""
    user_message: MessageResponse = Field(..., description="The user's message")
    assistant_message: MessageResponse = Field(..., description="The AI's response")
    research_id: str = Field(..., description="Research ID")
    total_messages: int = Field(..., description="Total messages in conversation")