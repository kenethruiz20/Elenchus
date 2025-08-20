"""
RAG (Retrieval Augmented Generation) API endpoints.
Provides secure, user-scoped document management and chat functionality.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
from datetime import datetime

from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.rag_document import RAGDocument, DocumentStatus
from app.models.rag_session import RAGSession, SessionType
from app.models.rag_chunk import RAGChunk
from app.services.rag_service import rag_service
from app.services.document_processor import DocumentProcessor
from app.schemas.rag_schemas import (
    DocumentUploadRequest, DocumentResponse, DocumentListResponse, DocumentProcessingStatus,
    SearchRequest, SearchResponse, SearchResult,
    SessionCreateRequest, SessionResponse, SessionListResponse,
    ChatRequest, ChatResponse, MessageResponse,
    UserStorageStats, SystemHealthResponse, ResponseMetadata,
    BatchDocumentRequest, BatchOperationResponse,
    ErrorResponse
)

router = APIRouter(prefix="/rag", tags=["rag"])


# Document Management Endpoints
@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tags: str = Form("[]"),
    category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a document for RAG processing.
    Requires authenticated user. Starts background processing automatically.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {max_size // 1024 // 1024}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file provided"
        )
    
    # Reset file position for processing
    await file.seek(0)
    
    try:
        # Parse tags from JSON string
        import json
        parsed_tags = json.loads(tags) if tags and tags != "[]" else []
        
        # Upload document and start processing
        document = await rag_service.upload_document(
            user_id=str(current_user.id),
            file=file,
            tags=parsed_tags,
            category=category,
            background_tasks=background_tasks
        )
        
        return DocumentResponse(
            id=str(document.id),
            user_id=document.user_id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            status=document.status,
            chunks_count=document.chunks_count,
            embeddings_created=document.embeddings_created,
            created_at=document.created_at,
            updated_at=document.updated_at,
            tags=document.tags,
            category=document.category,
            processing_progress=0.0 if document.status == DocumentStatus.PENDING else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_user_documents(
    limit: int = 50,
    offset: int = 0,
    status: Optional[DocumentStatus] = None,
    file_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    List user's documents with filtering and pagination.
    Multi-tenant: Only returns documents owned by the current user.
    """
    try:
        # Build filters
        filters = {"user_id": str(current_user.id)}
        if status:
            filters["status"] = status
        if file_type:
            filters["file_type"] = file_type
        if category:
            filters["category"] = category
        
        # Get documents
        documents = await RAGDocument.find_user_documents(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
            filters=filters,
            search_query=search
        )
        
        # Count total for pagination
        total_count = await RAGDocument.count_user_documents(
            user_id=str(current_user.id),
            filters=filters,
            search_query=search
        )
        
        # Convert to response format
        document_responses = []
        for doc in documents:
            document_responses.append(DocumentResponse(
                id=str(doc.id),
                user_id=doc.user_id,
                filename=doc.filename,
                original_filename=doc.original_filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                status=doc.status,
                chunks_count=doc.chunks_count,
                embeddings_created=doc.embeddings_created,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                tags=doc.tags,
                category=doc.category
            ))
        
        return DocumentListResponse(
            documents=document_responses,
            metadata=ResponseMetadata(
                total_count=total_count,
                page=offset // limit + 1,
                per_page=limit,
                has_next=offset + limit < total_count,
                has_prev=offset > 0
            )
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/documents/{document_id}/status", response_model=DocumentProcessingStatus)
async def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get processing status of a specific document.
    Multi-tenant: Only accessible by document owner.
    """
    # Verify document ownership
    document = await RAGDocument.find_one(
        RAGDocument.id == document_id,
        RAGDocument.user_id == str(current_user.id)
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Calculate progress based on status
    progress = 0.0
    if document.status == DocumentStatus.PROCESSING:
        progress = 0.5  # Processing chunks
    elif document.status == DocumentStatus.COMPLETED:
        progress = 1.0
    elif document.status == DocumentStatus.FAILED:
        progress = 0.0
    
    return DocumentProcessingStatus(
        document_id=str(document.id),
        status=document.status,
        progress=progress,
        chunks_created=document.chunks_count,
        processing_time_seconds=getattr(document.processing_metrics, 'processing_time_seconds', 0.0) if document.processing_metrics else 0.0,
        error_message=document.processing_error
    )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a document and all its chunks/embeddings.
    Multi-tenant: Only accessible by document owner.
    """
    # Verify document ownership
    document = await RAGDocument.find_one(
        RAGDocument.id == document_id,
        RAGDocument.user_id == str(current_user.id)
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        await rag_service.delete_document(document_id, str(current_user.id))
        return {"message": "Document deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


# Search Endpoints
@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform semantic search across user's documents.
    Multi-tenant: Only searches within user's document collection.
    """
    try:
        # Ensure document_ids are user's documents if specified
        if request.document_ids:
            user_docs = await RAGDocument.find(
                RAGDocument.id.in_(request.document_ids),
                RAGDocument.user_id == str(current_user.id)
            ).to_list()
            
            if len(user_docs) != len(request.document_ids):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to some specified documents"
                )
        
        # Perform search
        start_time = datetime.utcnow()
        results = await rag_service.search_similar_chunks(
            query=request.query,
            user_id=str(current_user.id),
            document_ids=request.document_ids,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            filters=request.filters
        )
        end_time = datetime.utcnow()
        search_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Convert to response format
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                chunk_id=result["chunk_id"],
                document_id=result["document_id"],
                document_name=result["document_name"],
                score=result["score"],
                text=result["text"],
                page_number=result.get("page_number"),
                chunk_index=result["chunk_index"],
                metadata=result.get("metadata", {})
            ))
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=search_time_ms,
            metadata={
                "user_id": str(current_user.id),
                "filters_applied": request.filters
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# Session Management Endpoints
@router.post("/sessions", response_model=SessionResponse)
async def create_chat_session(
    request: SessionCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new RAG chat session.
    Multi-tenant: Session belongs to the current user.
    """
    try:
        # Verify document access if specified
        if request.document_ids:
            user_docs = await RAGDocument.find(
                RAGDocument.id.in_(request.document_ids),
                RAGDocument.user_id == str(current_user.id)
            ).to_list()
            
            if len(user_docs) != len(request.document_ids):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to some specified documents"
                )
        
        # Create session
        session = RAGSession(
            user_id=str(current_user.id),
            session_title=request.title,
            session_type=request.session_type,
            active_document_ids=request.document_ids,
            referenced_document_ids=request.document_ids.copy(),
            settings=request.settings,
            tags=request.tags
        )
        
        await session.insert()
        
        return SessionResponse(
            id=str(session.id),
            user_id=session.user_id,
            session_title=session.session_title,
            session_type=session.session_type,
            message_count=0,
            active_document_ids=session.active_document_ids,
            referenced_document_ids=session.referenced_document_ids,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_activity=session.last_activity,
            tags=session.tags
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions", response_model=SessionListResponse)
async def list_user_sessions(
    limit: int = 20,
    offset: int = 0,
    session_type: Optional[SessionType] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    List user's chat sessions.
    Multi-tenant: Only returns sessions owned by the current user.
    """
    try:
        sessions = await RAGSession.find_user_sessions(
            user_id=str(current_user.id),
            session_type=session_type,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        # Count total for pagination
        filters = {"user_id": str(current_user.id)}
        if session_type:
            filters["session_type"] = session_type
        if is_active is not None:
            filters["is_active"] = is_active
        
        total_count = await RAGSession.find(filters).count()
        
        # Convert to response format
        session_responses = []
        for session in sessions:
            session_responses.append(SessionResponse(
                id=str(session.id),
                user_id=session.user_id,
                session_title=session.session_title,
                session_type=session.session_type,
                message_count=len(session.messages),
                active_document_ids=session.active_document_ids,
                referenced_document_ids=session.referenced_document_ids,
                is_active=session.is_active,
                created_at=session.created_at,
                updated_at=session.updated_at,
                last_activity=session.last_activity,
                tags=session.tags
            ))
        
        return SessionListResponse(
            sessions=session_responses,
            metadata=ResponseMetadata(
                total_count=total_count,
                page=offset // limit + 1,
                per_page=limit,
                has_next=offset + limit < total_count,
                has_prev=offset > 0
            )
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


# Chat Endpoint
@router.post("/chat", response_model=ChatResponse)
async def rag_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform RAG-enhanced chat.
    Multi-tenant: Only accesses user's documents and sessions.
    """
    try:
        # Verify session ownership
        session = await RAGSession.find_one(
            RAGSession.id == request.session_id,
            RAGSession.user_id == str(current_user.id)
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Perform RAG chat
        start_time = datetime.utcnow()
        response = await rag_service.generate_rag_response(
            session_id=request.session_id,
            user_id=str(current_user.id),
            message=request.message,
            search_params=request.search_params,
            generation_params=request.generation_params,
            include_context=request.include_context
        )
        end_time = datetime.utcnow()
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return ChatResponse(
            message_id=response["assistant_message_id"],
            session_id=request.session_id,
            user_message=response["user_message"],
            assistant_message=response["assistant_message"],
            search_results=response.get("search_results"),
            context_used=response.get("context_chunk_ids", []),
            total_processing_time_ms=total_time_ms
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


# Analytics & Health Endpoints
@router.get("/user/stats", response_model=UserStorageStats)
async def get_user_storage_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's storage and usage statistics.
    Multi-tenant: Only returns stats for the current user.
    """
    try:
        stats = await rag_service.get_user_statistics(str(current_user.id))
        return UserStorageStats(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )


@router.get("/health", response_model=SystemHealthResponse)
async def rag_system_health():
    """
    Check RAG system health (public endpoint).
    Returns status of all RAG components.
    """
    try:
        health = await rag_service.get_system_health()
        return SystemHealthResponse(**health)
    
    except Exception as e:
        return SystemHealthResponse(
            status="unhealthy",
            alerts=[f"Health check failed: {str(e)}"]
        )


# Batch Operations (Admin/Power User Features)
@router.post("/documents/batch", response_model=BatchOperationResponse)
async def batch_document_operation(
    request: BatchDocumentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform batch operations on multiple documents.
    Multi-tenant: Only operates on user's documents.
    """
    try:
        # Verify all documents belong to user
        user_docs = await RAGDocument.find(
            RAGDocument.id.in_(request.document_ids),
            RAGDocument.user_id == str(current_user.id)
        ).to_list()
        
        if len(user_docs) != len(request.document_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to some specified documents"
            )
        
        # Perform batch operation
        start_time = datetime.utcnow()
        result = await rag_service.batch_document_operation(
            user_id=str(current_user.id),
            document_ids=request.document_ids,
            operation=request.operation,
            parameters=request.parameters
        )
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return BatchOperationResponse(
            operation_id=result["operation_id"],
            operation=request.operation,
            total_items=len(request.document_ids),
            successful=result["successful"],
            failed=result["failed"],
            errors=result.get("errors", []),
            processing_time_ms=processing_time_ms
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch operation failed: {str(e)}"
        )