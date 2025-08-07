"""Sources API endpoints for managing legal documents and references."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from beanie import PydanticObjectId

from app.models import Source
from app.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceListResponse
)

router = APIRouter(prefix="/sources", tags=["sources"])

# Mock user dependency - replace with actual auth
async def get_current_user_id() -> str:
    """Mock user ID - replace with actual authentication."""
    return "user_123"  # TODO: Implement actual authentication


@router.post("/", response_model=SourceResponse)
async def create_source(
    source_data: SourceCreate,
    user_id: str = Depends(get_current_user_id)
) -> SourceResponse:
    """Create a new source document (metadata only)."""
    try:
        # Create source document
        source = Source(
            title=source_data.title,
            file_type=source_data.file_type,
            url=source_data.url,
            source_type=source_data.source_type,
            author=source_data.author,
            publication_date=source_data.publication_date,
            category=source_data.category,
            jurisdiction=source_data.jurisdiction,
            tags=source_data.tags,
            user_id=user_id
        )
        
        await source.create()
        
        return SourceResponse(
            id=str(source.id),
            title=source.title,
            filename=source.filename,
            file_type=source.file_type,
            file_size=source.file_size,
            url=source.url,
            content_preview=source.content_preview,
            page_count=source.page_count,
            author=source.author,
            publication_date=source.publication_date,
            source_type=source.source_type,
            category=source.category,
            jurisdiction=source.jurisdiction,
            user_id=source.user_id,
            processing_status=source.processing_status,
            processing_error=source.processing_error,
            tags=source.tags,
            keywords=source.keywords,
            created_at=source.created_at,
            updated_at=source.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create source: {str(e)}")


@router.post("/upload", response_model=SourceResponse)
async def upload_source(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    source_type: str = "document",
    category: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
) -> SourceResponse:
    """Upload a source document file."""
    try:
        # TODO: Implement file upload, storage, and processing
        # This is a placeholder implementation
        
        # Basic file validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Extract file info
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown'
        document_title = title or file.filename
        
        # Create source document
        source = Source(
            title=document_title,
            filename=file.filename,
            file_type=file_extension,
            file_size=file.size if hasattr(file, 'size') else None,
            source_type=source_type,
            category=category,
            jurisdiction=jurisdiction,
            user_id=user_id,
            processing_status="pending"
        )
        
        await source.create()
        
        # TODO: 
        # 1. Save file to storage (local/S3)
        # 2. Extract text content
        # 3. Generate preview
        # 4. Extract keywords
        # 5. Update processing status
        
        return SourceResponse(
            id=str(source.id),
            title=source.title,
            filename=source.filename,
            file_type=source.file_type,
            file_size=source.file_size,
            url=source.url,
            content_preview=source.content_preview,
            page_count=source.page_count,
            author=source.author,
            publication_date=source.publication_date,
            source_type=source.source_type,
            category=source.category,
            jurisdiction=source.jurisdiction,
            user_id=source.user_id,
            processing_status=source.processing_status,
            processing_error=source.processing_error,
            tags=source.tags,
            keywords=source.keywords,
            created_at=source.created_at,
            updated_at=source.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload source: {str(e)}")


@router.get("/", response_model=SourceListResponse)
async def list_sources(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    user_id: str = Depends(get_current_user_id)
) -> SourceListResponse:
    """List user's source documents with pagination."""
    try:
        # Build query
        query = {"user_id": user_id}
        if source_type:
            query["source_type"] = source_type
        if category:
            query["category"] = category
        if jurisdiction:
            query["jurisdiction"] = jurisdiction
        if status:
            query["processing_status"] = status
        
        # Get total count
        total = await Source.find(query).count()
        
        # Get paginated results
        skip = (page - 1) * per_page
        sources = await Source.find(query).skip(skip).limit(per_page).sort([("created_at", -1)]).to_list()
        
        # Convert to response format
        source_responses = [
            SourceResponse(
                id=str(source.id),
                title=source.title,
                filename=source.filename,
                file_type=source.file_type,
                file_size=source.file_size,
                url=source.url,
                content_preview=source.content_preview,
                page_count=source.page_count,
                author=source.author,
                publication_date=source.publication_date,
                source_type=source.source_type,
                category=source.category,
                jurisdiction=source.jurisdiction,
                user_id=source.user_id,
                processing_status=source.processing_status,
                processing_error=source.processing_error,
                tags=source.tags,
                keywords=source.keywords,
                created_at=source.created_at,
                updated_at=source.updated_at
            )
            for source in sources
        ]
        
        return SourceListResponse(
            sources=source_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=skip + per_page < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sources: {str(e)}")


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id)
) -> SourceResponse:
    """Get a specific source document by ID."""
    try:
        source = await Source.get(PydanticObjectId(source_id))
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Check ownership
        if source.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return SourceResponse(
            id=str(source.id),
            title=source.title,
            filename=source.filename,
            file_type=source.file_type,
            file_size=source.file_size,
            url=source.url,
            content_preview=source.content_preview,
            page_count=source.page_count,
            author=source.author,
            publication_date=source.publication_date,
            source_type=source.source_type,
            category=source.category,
            jurisdiction=source.jurisdiction,
            user_id=source.user_id,
            processing_status=source.processing_status,
            processing_error=source.processing_error,
            tags=source.tags,
            keywords=source.keywords,
            created_at=source.created_at,
            updated_at=source.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get source: {str(e)}")


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: str,
    update_data: SourceUpdate,
    user_id: str = Depends(get_current_user_id)
) -> SourceResponse:
    """Update source document metadata."""
    try:
        source = await Source.get(PydanticObjectId(source_id))
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Check ownership
        if source.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            await source.update({"$set": update_dict})
            
            # Refresh the document
            source = await Source.get(PydanticObjectId(source_id))
        
        return SourceResponse(
            id=str(source.id),
            title=source.title,
            filename=source.filename,
            file_type=source.file_type,
            file_size=source.file_size,
            url=source.url,
            content_preview=source.content_preview,
            page_count=source.page_count,
            author=source.author,
            publication_date=source.publication_date,
            source_type=source.source_type,
            category=source.category,
            jurisdiction=source.jurisdiction,
            user_id=source.user_id,
            processing_status=source.processing_status,
            processing_error=source.processing_error,
            tags=source.tags,
            keywords=source.keywords,
            created_at=source.created_at,
            updated_at=source.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update source: {str(e)}")


@router.delete("/{source_id}")
async def delete_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a source document."""
    try:
        source = await Source.get(PydanticObjectId(source_id))
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Check ownership
        if source.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # TODO: Also delete the actual file from storage
        await source.delete()
        
        return {"message": "Source deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete source: {str(e)}")


@router.get("/{source_id}/content")
async def get_source_content(
    source_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get the full content of a source document."""
    try:
        source = await Source.get(PydanticObjectId(source_id))
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Check ownership
        if source.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if source.processing_status != "completed":
            raise HTTPException(status_code=400, detail="Source not yet processed")
        
        return {
            "id": str(source.id),
            "title": source.title,
            "content": source.content,
            "page_count": source.page_count,
            "file_type": source.file_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get source content: {str(e)}")