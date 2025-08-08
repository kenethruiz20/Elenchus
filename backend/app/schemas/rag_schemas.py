"""
RAG System Pydantic Schemas
Input/output schemas for RAG API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID

from ..models.rag_document import DocumentType, DocumentStatus
from ..models.rag_session import SessionType, MessageRole, MessageType
from ..models.rag_chunk import ChunkType


# Base schemas
class PaginationParams(BaseModel):
    """Pagination parameters."""
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")


class ResponseMetadata(BaseModel):
    """Response metadata for API responses."""
    total_count: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    has_next: bool = False
    has_prev: bool = False


# Document schemas
class DocumentUploadRequest(BaseModel):
    """Document upload request schema."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: DocumentType
    tags: List[str] = Field(default_factory=list, max_items=20)
    category: Optional[str] = Field(None, max_length=100)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Clean up tags
            cleaned = [tag.strip().lower() for tag in v if tag.strip()]
            return list(set(cleaned))  # Remove duplicates
        return v


class DocumentResponse(BaseModel):
    """Document response schema."""
    id: str
    user_id: str
    filename: str
    original_filename: str
    file_type: DocumentType
    file_size: int
    status: DocumentStatus
    chunks_count: int
    embeddings_created: bool
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    category: Optional[str]
    processing_progress: Optional[float] = None  # 0.0 to 1.0
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    documents: List[DocumentResponse]
    metadata: ResponseMetadata


class DocumentProcessingStatus(BaseModel):
    """Document processing status schema."""
    document_id: str
    status: DocumentStatus
    progress: float = Field(ge=0.0, le=1.0)
    chunks_created: int = 0
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None
    estimated_completion: Optional[datetime] = None


# Search schemas
class SearchRequest(BaseModel):
    """Vector search request schema."""
    query: str = Field(..., min_length=1, max_length=1000)
    document_ids: Optional[List[str]] = Field(None, max_items=50)
    filters: Dict[str, Any] = Field(default_factory=dict)
    top_k: int = Field(default=8, ge=1, le=50)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    include_metadata: bool = True
    
    @validator('document_ids')
    def validate_document_ids(cls, v):
        if v and len(v) == 0:
            return None
        return v


class SearchResult(BaseModel):
    """Single search result schema."""
    chunk_id: str
    document_id: str
    document_name: str
    score: float
    text: str
    page_number: Optional[int]
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search results response schema."""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Session schemas
class SessionCreateRequest(BaseModel):
    """Chat session creation request."""
    title: str = Field(..., min_length=1, max_length=200)
    session_type: SessionType = SessionType.GENERAL
    document_ids: List[str] = Field(default_factory=list, max_items=20)
    settings: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            cleaned = [tag.strip().lower() for tag in v if tag.strip()]
            return list(set(cleaned))[:10]  # Limit to 10 unique tags
        return v


class SessionResponse(BaseModel):
    """Chat session response schema."""
    id: str
    user_id: str
    session_title: str
    session_type: SessionType
    message_count: int
    active_document_ids: List[str]
    referenced_document_ids: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    tags: List[str]
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Session list response schema."""
    sessions: List[SessionResponse]
    metadata: ResponseMetadata


# Message schemas
class MessageCreateRequest(BaseModel):
    """Message creation request schema."""
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: MessageType = MessageType.TEXT
    attached_files: List[str] = Field(default_factory=list, max_items=5)
    context: Dict[str, Any] = Field(default_factory=dict)


class CitationInfo(BaseModel):
    """Citation information schema."""
    document_id: str
    document_name: str
    chunk_id: str
    page_number: Optional[int]
    relevance_score: float
    text_snippet: str = Field(max_length=500)


class MessageResponse(BaseModel):
    """Message response schema."""
    message_id: str
    session_id: str
    role: MessageRole
    message_type: MessageType
    content: str
    timestamp: datetime
    citations: List[CitationInfo] = Field(default_factory=list)
    tokens_used: Optional[int]
    processing_time_ms: float
    confidence_score: Optional[float]
    attached_files: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """RAG chat request schema."""
    session_id: str
    message: str = Field(..., min_length=1, max_length=10000)
    search_params: Optional[SearchRequest] = None
    generation_params: Dict[str, Any] = Field(default_factory=dict)
    include_context: bool = True


class ChatResponse(BaseModel):
    """RAG chat response schema."""
    message_id: str
    session_id: str
    user_message: MessageResponse
    assistant_message: MessageResponse
    search_results: Optional[SearchResponse] = None
    context_used: List[str] = Field(default_factory=list)  # Chunk IDs used in context
    total_processing_time_ms: float


# Analytics schemas
class UserStorageStats(BaseModel):
    """User storage statistics schema."""
    user_id: str
    total_documents: int
    total_file_size: int
    total_chunks: int
    total_sessions: int
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    storage_used_mb: float
    
    @validator('storage_used_mb', pre=True)
    def calculate_storage_mb(cls, v, values):
        if 'total_file_size' in values:
            return round(values['total_file_size'] / (1024 * 1024), 2)
        return v


class SystemHealthResponse(BaseModel):
    """System health response schema."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    alerts: List[str] = Field(default_factory=list)


# Batch operation schemas
class BatchDocumentRequest(BaseModel):
    """Batch document operation request."""
    document_ids: List[str] = Field(..., min_items=1, max_items=100)
    operation: str = Field(..., regex="^(delete|reprocess|update_tags)$")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class BatchOperationResponse(BaseModel):
    """Batch operation response schema."""
    operation_id: str
    operation: str
    total_items: int
    successful: int
    failed: int
    errors: List[str] = Field(default_factory=list)
    processing_time_ms: float


# Error schemas
class ErrorDetail(BaseModel):
    """Error detail schema."""
    code: str
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    details: List[ErrorDetail] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


# Export schemas
class ExportRequest(BaseModel):
    """Data export request schema."""
    export_type: str = Field(..., regex="^(documents|sessions|analytics)$")
    format: str = Field(default="json", regex="^(json|csv|markdown)$")
    filters: Dict[str, Any] = Field(default_factory=dict)
    include_content: bool = True
    date_range: Optional[Dict[str, datetime]] = None


class ExportResponse(BaseModel):
    """Export response schema."""
    export_id: str
    status: str  # "processing", "completed", "failed"
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)