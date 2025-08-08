"""
RAG Chat Session Models
Pydantic models for chat sessions and conversations in the RAG system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from beanie import Document, Indexed
from pydantic import BaseModel, Field
import pymongo


class SessionType(str, Enum):
    """Chat session type enum."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SUMMARY = "summary"
    QA = "qa"
    GENERAL = "general"


class MessageRole(str, Enum):
    """Message role enum."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Message type enum."""
    TEXT = "text"
    FILE_UPLOAD = "file_upload"
    SEARCH_RESULT = "search_result"
    ERROR = "error"
    SYSTEM_INFO = "system_info"


class Citation(BaseModel):
    """Citation information for RAG responses."""
    document_id: str
    document_name: str
    chunk_id: str
    page_number: Optional[int] = None
    relevance_score: float
    text_snippet: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None


class SearchContext(BaseModel):
    """Search context used for generating response."""
    query_embedding: Optional[List[float]] = None
    search_query: str
    top_k: int
    search_filters: Dict[str, Any] = Field(default_factory=dict)
    total_results: int = 0
    search_time_ms: float = 0.0
    rerank_time_ms: float = 0.0


class MessageMetadata(BaseModel):
    """Message metadata."""
    tokens_used: Optional[int] = None
    processing_time_ms: float = 0.0
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    search_context: Optional[SearchContext] = None
    citations: List[Citation] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class RAGMessage(BaseModel):
    """Individual message in a chat session."""
    message_id: str
    role: MessageRole
    message_type: MessageType = MessageType.TEXT
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # File attachments
    attached_files: List[str] = Field(default_factory=list)  # File IDs
    
    # RAG-specific metadata
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)
    
    # Response quality
    user_feedback: Optional[int] = None  # 1-5 rating
    user_feedback_text: Optional[str] = None
    
    # Processing information
    is_regenerated: bool = False
    parent_message_id: Optional[str] = None  # For regenerated messages


class SessionSettings(BaseModel):
    """Session-specific settings."""
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    search_top_k: int = 8
    max_context_length: int = 4000
    include_citations: bool = True
    search_filters: Dict[str, Any] = Field(default_factory=dict)
    custom_instructions: Optional[str] = None


class SessionMetrics(BaseModel):
    """Session metrics and analytics."""
    total_messages: int = 0
    total_user_messages: int = 0
    total_assistant_messages: int = 0
    total_tokens_used: int = 0
    total_processing_time_ms: float = 0.0
    total_search_time_ms: float = 0.0
    average_response_time_ms: float = 0.0
    unique_documents_referenced: int = 0
    total_citations: int = 0
    average_confidence_score: Optional[float] = None
    user_satisfaction_scores: List[int] = Field(default_factory=list)


class RAGSession(Document):
    """
    RAG chat session model.
    Stores conversation history and context for RAG-based interactions.
    """
    
    # Core identification
    user_id: Indexed(str)  # User who owns this session
    session_title: str
    session_type: SessionType = SessionType.GENERAL
    
    # Session configuration
    settings: SessionSettings = Field(default_factory=SessionSettings)
    
    # Messages and conversation
    messages: List[RAGMessage] = Field(default_factory=list)
    
    # Document context
    active_document_ids: List[str] = Field(default_factory=list)  # Currently active documents
    referenced_document_ids: List[str] = Field(default_factory=list)  # All referenced documents
    
    # Session state
    is_active: bool = True
    is_archived: bool = False
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Metrics and analytics
    metrics: SessionMetrics = Field(default_factory=SessionMetrics)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Tags and organization
    tags: List[str] = Field(default_factory=list)
    folder: Optional[str] = None
    is_favorite: bool = False
    
    # Sharing and collaboration
    is_shared: bool = False
    shared_with: List[str] = Field(default_factory=list)  # User IDs
    shared_permissions: Dict[str, str] = Field(default_factory=dict)  # User ID -> permission level
    
    class Settings:
        name = "rag_sessions"
        indexes = [
            [
                ("user_id", pymongo.ASCENDING),
                ("is_active", pymongo.ASCENDING),
                ("last_activity", pymongo.DESCENDING)
            ],
            [
                ("user_id", pymongo.ASCENDING),
                ("session_type", pymongo.ASCENDING),
                ("created_at", pymongo.DESCENDING)
            ],
            [("is_shared", pymongo.ASCENDING)],
            [("tags", pymongo.ASCENDING)],
            [("folder", pymongo.ASCENDING)],
            [("referenced_document_ids", pymongo.ASCENDING)],
            # Text search index
            [("session_title", pymongo.TEXT), ("messages.content", pymongo.TEXT)],
        ]

    async def add_message(
        self, 
        role: MessageRole, 
        content: str, 
        message_type: MessageType = MessageType.TEXT,
        metadata: MessageMetadata = None,
        attached_files: List[str] = None
    ) -> str:
        """Add a new message to the session."""
        import uuid
        
        message_id = str(uuid.uuid4())
        message = RAGMessage(
            message_id=message_id,
            role=role,
            message_type=message_type,
            content=content,
            metadata=metadata or MessageMetadata(),
            attached_files=attached_files or []
        )
        
        self.messages.append(message)
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Update metrics
        self.metrics.total_messages += 1
        if role == MessageRole.USER:
            self.metrics.total_user_messages += 1
        elif role == MessageRole.ASSISTANT:
            self.metrics.total_assistant_messages += 1
        
        if metadata:
            if metadata.tokens_used:
                self.metrics.total_tokens_used += metadata.tokens_used
            if metadata.processing_time_ms:
                self.metrics.total_processing_time_ms += metadata.processing_time_ms
            if metadata.search_context and metadata.search_context.search_time_ms:
                self.metrics.total_search_time_ms += metadata.search_context.search_time_ms
        
        # Recalculate averages
        self._update_average_metrics()
        
        await self.save()
        return message_id

    async def add_document_reference(self, document_id: str):
        """Add a document reference to the session."""
        if document_id not in self.referenced_document_ids:
            self.referenced_document_ids.append(document_id)
        if document_id not in self.active_document_ids:
            self.active_document_ids.append(document_id)
        
        self.metrics.unique_documents_referenced = len(self.referenced_document_ids)
        self.updated_at = datetime.utcnow()
        await self.save()

    async def remove_active_document(self, document_id: str):
        """Remove a document from active context."""
        if document_id in self.active_document_ids:
            self.active_document_ids.remove(document_id)
        self.updated_at = datetime.utcnow()
        await self.save()

    async def update_message_feedback(self, message_id: str, rating: int, feedback_text: str = None):
        """Update user feedback for a specific message."""
        for message in self.messages:
            if message.message_id == message_id:
                message.user_feedback = rating
                message.user_feedback_text = feedback_text
                
                # Update session metrics
                if rating not in self.metrics.user_satisfaction_scores:
                    self.metrics.user_satisfaction_scores.append(rating)
                
                self.updated_at = datetime.utcnow()
                await self.save()
                break

    async def archive_session(self):
        """Archive the session."""
        self.is_active = False
        self.is_archived = True
        self.updated_at = datetime.utcnow()
        await self.save()

    def _update_average_metrics(self):
        """Update average metrics."""
        if self.metrics.total_assistant_messages > 0:
            self.metrics.average_response_time_ms = (
                self.metrics.total_processing_time_ms / self.metrics.total_assistant_messages
            )
        
        if self.metrics.user_satisfaction_scores:
            avg_satisfaction = sum(self.metrics.user_satisfaction_scores) / len(self.metrics.user_satisfaction_scores)
            self.metrics.average_confidence_score = avg_satisfaction / 5.0  # Normalize to 0-1

    def get_context_messages(self, max_messages: int = 10) -> List[RAGMessage]:
        """Get recent messages for context."""
        return self.messages[-max_messages:] if self.messages else []

    def get_conversation_summary(self) -> str:
        """Get a brief summary of the conversation."""
        if not self.messages:
            return "Empty conversation"
        
        user_messages = [m for m in self.messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in self.messages if m.role == MessageRole.ASSISTANT]
        
        summary = f"Session with {len(user_messages)} user messages and {len(assistant_messages)} responses"
        
        if self.active_document_ids:
            summary += f", referencing {len(self.active_document_ids)} active documents"
        
        return summary

    @classmethod
    async def find_user_sessions(
        cls, 
        user_id: str, 
        session_type: SessionType = None,
        is_active: bool = None,
        limit: int = 50, 
        skip: int = 0
    ):
        """Find sessions for a specific user."""
        query = cls.user_id == user_id
        
        if session_type:
            query = query & (cls.session_type == session_type)
        if is_active is not None:
            query = query & (cls.is_active == is_active)
        
        return await cls.find(query).sort(-cls.last_activity).limit(limit).skip(skip).to_list()

    @classmethod
    async def find_sessions_with_document(cls, document_id: str, user_id: str = None):
        """Find sessions that reference a specific document."""
        query = cls.referenced_document_ids == document_id
        
        if user_id:
            query = query & (cls.user_id == user_id)
        
        return await cls.find(query).sort(-cls.last_activity).to_list()