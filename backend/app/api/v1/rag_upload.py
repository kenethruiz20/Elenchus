"""
RAG Document Upload API endpoints.
Stage 4: Document Upload & Registration functionality.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime
import json

from app.core.auth import get_current_active_user, get_current_verified_user
from app.models.user import User
from app.models.rag_document import RAGDocument, DocumentStatus
from app.services.rag_upload_service import rag_upload_service

router = APIRouter(prefix="/rag", tags=["rag-upload"])


@router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tags: str = Form("[]"),
    category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Upload a document for RAG processing.
    Requires verified user. Starts background processing automatically.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
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
    
    try:
        # Parse tags from JSON string
        parsed_tags = json.loads(tags) if tags and tags != "[]" else []
        
        # Upload document using the upload service
        document = await rag_upload_service.upload_document(
            user_id=str(current_user.id),
            file=file,
            tags=parsed_tags,
            category=category,
            background_tasks=background_tasks
        )
        
        return {
            "id": str(document.id),
            "user_id": document.user_id,
            "filename": document.filename,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "status": document.status,
            "chunks_count": document.chunks_count,
            "embeddings_created": document.embeddings_created,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
            "tags": document.tags,
            "category": document.category,
            "processing_progress": 0.0 if document.status == DocumentStatus.PENDING else None
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/documents")
async def list_user_documents(
    limit: int = 50,
    offset: int = 0,
    status: Optional[DocumentStatus] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    List user's documents with filtering and pagination.
    Multi-tenant: Only returns documents owned by the current user.
    """
    try:
        result = await rag_upload_service.list_user_documents(
            user_id=str(current_user.id),
            limit=limit,
            offset=offset,
            status=status
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to list documents')
            )
        
        return {
            "documents": result['documents'],
            "metadata": {
                "total_count": result['total_count'],
                "page": offset // limit + 1,
                "per_page": limit,
                "has_next": offset + limit < result['total_count'],
                "has_prev": offset > 0
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/documents/{document_id}/status")
async def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get processing status of a specific document.
    Multi-tenant: Only accessible by document owner.
    """
    try:
        status_info = await rag_upload_service.get_document_status(
            document_id=document_id,
            user_id=str(current_user.id)
        )
        
        if not status_info['found']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {
            "document_id": status_info['document_id'],
            "status": status_info['status'],
            "progress": status_info['progress'],
            "chunks_created": status_info['chunks_count'],
            "embeddings_created": status_info['embeddings_created'],
            "processing_error": status_info.get('processing_error'),
            "created_at": status_info['created_at'],
            "updated_at": status_info['updated_at']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document status: {str(e)}"
        )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a document and all its chunks.
    Multi-tenant: Only accessible by document owner.
    """
    try:
        result = await rag_upload_service.delete_document(
            document_id=document_id,
            user_id=str(current_user.id)
        )
        
        if not result['success']:
            if 'not found' in result.get('error', '').lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get('error', 'Failed to delete document')
                )
        
        return {
            "message": "Document deleted successfully",
            "deleted_document_id": result['deleted_document_id'],
            "deleted_chunks": result['deleted_chunks']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/user/stats")
async def get_user_storage_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's storage and usage statistics.
    Multi-tenant: Only returns stats for the current user.
    """
    try:
        stats = await rag_upload_service.get_user_statistics(str(current_user.id))
        
        if 'error' in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=stats['error']
            )
        
        return {
            "user_id": stats['user_id'],
            "total_documents": stats['total_documents'],
            "total_chunks": stats['total_chunks'],
            "total_file_size": stats['total_file_size'],
            "documents_by_status": stats['documents_by_status'],
            "storage_used_mb": round(stats['storage_used_mb'], 2)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )


@router.get("/health")
async def rag_system_health():
    """
    Check RAG system health (public endpoint).
    Returns status of all RAG components.
    """
    try:
        # Check if upload service is initialized
        upload_service_status = rag_upload_service.initialized
        
        # Check database connection
        from app.database import mongodb_manager
        db_status = mongodb_manager.is_initialized
        
        # Check GCP service
        from app.services.gcp_service import gcp_service
        gcp_health = await gcp_service.health_check()
        gcp_status = gcp_health.get('healthy', False)
        
        overall_status = "healthy" if (upload_service_status and db_status) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow(),
            "services": {
                "upload_service": {
                    "status": "healthy" if upload_service_status else "unhealthy",
                    "initialized": upload_service_status
                },
                "database": {
                    "status": "healthy" if db_status else "unhealthy",
                    "initialized": db_status
                },
                "gcp_storage": {
                    "status": "healthy" if gcp_status else "unavailable",
                    "enabled": gcp_service.is_initialized(),
                    "bucket": gcp_health.get('bucket_name') if gcp_status else None
                }
            },
            "performance_metrics": {
                "avg_upload_time_ms": 0,  # Placeholder for now
                "avg_processing_time_ms": 0  # Placeholder for now
            },
            "alerts": [] if overall_status == "healthy" else ["Some services unavailable"]
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "services": {},
            "alerts": [f"Health check failed: {str(e)}"]
        }


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get information about supported document formats.
    Public endpoint for frontend integration.
    """
    try:
        from app.services.document_processor import document_processor
        
        formats_info = document_processor.get_supported_formats()
        
        return {
            "supported_extensions": formats_info['supported_extensions'],
            "max_file_sizes": formats_info['max_file_sizes'],
            "processing_capabilities": formats_info['processing_capabilities'],
            "missing_dependencies": formats_info.get('missing_dependencies', [])
        }
    
    except Exception as e:
        return {
            "error": f"Failed to get supported formats: {str(e)}",
            "supported_extensions": [".pdf", ".txt", ".doc", ".docx", ".md"],
            "max_file_sizes": {"default": "50MB"}
        }