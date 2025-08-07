"""Notes API endpoints for managing research notes and annotations."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from beanie import PydanticObjectId

from app.models import Note
from app.schemas.note import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteListResponse,
    NoteLinkUpdate,
    NoteSearchRequest
)

router = APIRouter(prefix="/notes", tags=["notes"])

# Mock user dependency - replace with actual auth
async def get_current_user_id() -> str:
    """Mock user ID - replace with actual authentication."""
    return "user_123"  # TODO: Implement actual authentication


def calculate_reading_time(content: str) -> int:
    """Calculate estimated reading time in minutes (250 words per minute)."""
    word_count = len(content.split())
    return max(1, round(word_count / 250))


@router.post("/", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    user_id: str = Depends(get_current_user_id)
) -> NoteResponse:
    """Create a new note."""
    try:
        # Calculate word count and reading time
        word_count = len(note_data.content.split())
        reading_time = calculate_reading_time(note_data.content)
        
        # Create note document
        note = Note(
            title=note_data.title,
            content=note_data.content,
            user_id=user_id,
            research_id=note_data.research_id,
            source_id=note_data.source_id,
            source_page=note_data.source_page,
            source_quote=note_data.source_quote,
            note_type=note_data.note_type,
            category=note_data.category,
            tags=note_data.tags,
            is_pinned=note_data.is_pinned,
            parent_note_id=note_data.parent_note_id,
            word_count=word_count,
            reading_time_minutes=reading_time
        )
        
        await note.create()
        
        return NoteResponse(
            id=str(note.id),
            title=note.title,
            content=note.content,
            user_id=note.user_id,
            research_id=note.research_id,
            source_id=note.source_id,
            source_page=note.source_page,
            source_quote=note.source_quote,
            note_type=note.note_type,
            category=note.category,
            tags=note.tags,
            is_pinned=note.is_pinned,
            is_private=note.is_private,
            status=note.status,
            parent_note_id=note.parent_note_id,
            linked_note_ids=note.linked_note_ids,
            word_count=note.word_count,
            reading_time_minutes=note.reading_time_minutes,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")


@router.get("/", response_model=NoteListResponse)
async def list_notes(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    note_type: Optional[str] = Query(None, description="Filter by note type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    research_id: Optional[str] = Query(None, description="Filter by research"),
    source_id: Optional[str] = Query(None, description="Filter by source"),
    is_pinned: Optional[bool] = Query(None, description="Filter by pinned status"),
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: str = Depends(get_current_user_id)
) -> NoteListResponse:
    """List user's notes with pagination."""
    try:
        # Build query
        query = {"user_id": user_id}
        if note_type:
            query["note_type"] = note_type
        if category:
            query["category"] = category
        if research_id:
            query["research_id"] = research_id
        if source_id:
            query["source_id"] = source_id
        if is_pinned is not None:
            query["is_pinned"] = is_pinned
        if status:
            query["status"] = status
        
        # Get total count
        total = await Note.find(query).count()
        
        # Get paginated results (pinned first, then by update time)
        skip = (page - 1) * per_page
        notes = await Note.find(query).skip(skip).limit(per_page).sort([("is_pinned", -1), ("updated_at", -1)]).to_list()
        
        # Convert to response format
        note_responses = [
            NoteResponse(
                id=str(note.id),
                title=note.title,
                content=note.content,
                user_id=note.user_id,
                research_id=note.research_id,
                source_id=note.source_id,
                source_page=note.source_page,
                source_quote=note.source_quote,
                note_type=note.note_type,
                category=note.category,
                tags=note.tags,
                is_pinned=note.is_pinned,
                is_private=note.is_private,
                status=note.status,
                parent_note_id=note.parent_note_id,
                linked_note_ids=note.linked_note_ids,
                word_count=note.word_count,
                reading_time_minutes=note.reading_time_minutes,
                created_at=note.created_at,
                updated_at=note.updated_at
            )
            for note in notes
        ]
        
        return NoteListResponse(
            notes=note_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=skip + per_page < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list notes: {str(e)}")


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id)
) -> NoteResponse:
    """Get a specific note by ID."""
    try:
        note = await Note.get(PydanticObjectId(note_id))
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Check ownership
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return NoteResponse(
            id=str(note.id),
            title=note.title,
            content=note.content,
            user_id=note.user_id,
            research_id=note.research_id,
            source_id=note.source_id,
            source_page=note.source_page,
            source_quote=note.source_quote,
            note_type=note.note_type,
            category=note.category,
            tags=note.tags,
            is_pinned=note.is_pinned,
            is_private=note.is_private,
            status=note.status,
            parent_note_id=note.parent_note_id,
            linked_note_ids=note.linked_note_ids,
            word_count=note.word_count,
            reading_time_minutes=note.reading_time_minutes,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get note: {str(e)}")


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    update_data: NoteUpdate,
    user_id: str = Depends(get_current_user_id)
) -> NoteResponse:
    """Update a note."""
    try:
        note = await Note.get(PydanticObjectId(note_id))
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Check ownership
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            # Recalculate word count and reading time if content changed
            if "content" in update_dict:
                update_dict["word_count"] = len(update_dict["content"].split())
                update_dict["reading_time_minutes"] = calculate_reading_time(update_dict["content"])
            
            update_dict["updated_at"] = datetime.utcnow()
            await note.update({"$set": update_dict})
            
            # Refresh the document
            note = await Note.get(PydanticObjectId(note_id))
        
        return NoteResponse(
            id=str(note.id),
            title=note.title,
            content=note.content,
            user_id=note.user_id,
            research_id=note.research_id,
            source_id=note.source_id,
            source_page=note.source_page,
            source_quote=note.source_quote,
            note_type=note.note_type,
            category=note.category,
            tags=note.tags,
            is_pinned=note.is_pinned,
            is_private=note.is_private,
            status=note.status,
            parent_note_id=note.parent_note_id,
            linked_note_ids=note.linked_note_ids,
            word_count=note.word_count,
            reading_time_minutes=note.reading_time_minutes,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update note: {str(e)}")


@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a note."""
    try:
        note = await Note.get(PydanticObjectId(note_id))
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Check ownership
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await note.delete()
        
        return {"message": "Note deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete note: {str(e)}")


@router.put("/{note_id}/links", response_model=NoteResponse)
async def update_note_links(
    note_id: str,
    links_data: NoteLinkUpdate,
    user_id: str = Depends(get_current_user_id)
) -> NoteResponse:
    """Update note relationships/links."""
    try:
        note = await Note.get(PydanticObjectId(note_id))
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Check ownership
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Verify all linked notes exist and belong to user
        for linked_id in links_data.linked_note_ids:
            try:
                linked_note = await Note.get(PydanticObjectId(linked_id))
                if not linked_note or linked_note.user_id != user_id:
                    raise HTTPException(status_code=400, detail=f"Invalid linked note ID: {linked_id}")
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid linked note ID: {linked_id}")
        
        # Update links
        await note.update({
            "$set": {
                "linked_note_ids": links_data.linked_note_ids,
                "updated_at": datetime.utcnow()
            }
        })
        
        # Refresh and return
        note = await Note.get(PydanticObjectId(note_id))
        return NoteResponse(
            id=str(note.id),
            title=note.title,
            content=note.content,
            user_id=note.user_id,
            research_id=note.research_id,
            source_id=note.source_id,
            source_page=note.source_page,
            source_quote=note.source_quote,
            note_type=note.note_type,
            category=note.category,
            tags=note.tags,
            is_pinned=note.is_pinned,
            is_private=note.is_private,
            status=note.status,
            parent_note_id=note.parent_note_id,
            linked_note_ids=note.linked_note_ids,
            word_count=note.word_count,
            reading_time_minutes=note.reading_time_minutes,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update note links: {str(e)}")


@router.post("/search", response_model=NoteListResponse)
async def search_notes(
    search_request: NoteSearchRequest,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user_id)
) -> NoteListResponse:
    """Search notes by content and filters."""
    try:
        # Build query
        query = {"user_id": user_id}
        
        # Add text search
        if search_request.query:
            query["$text"] = {"$search": search_request.query}
        
        # Add filters
        if search_request.note_type:
            query["note_type"] = search_request.note_type
        if search_request.category:
            query["category"] = search_request.category
        if search_request.tags:
            query["tags"] = {"$in": search_request.tags}
        if search_request.research_id:
            query["research_id"] = search_request.research_id
        if search_request.source_id:
            query["source_id"] = search_request.source_id
        
        # Get total count
        total = await Note.find(query).count()
        
        # Get paginated results
        skip = (page - 1) * per_page
        notes = await Note.find(query).skip(skip).limit(per_page).sort([("updated_at", -1)]).to_list()
        
        # Convert to response format
        note_responses = [
            NoteResponse(
                id=str(note.id),
                title=note.title,
                content=note.content,
                user_id=note.user_id,
                research_id=note.research_id,
                source_id=note.source_id,
                source_page=note.source_page,
                source_quote=note.source_quote,
                note_type=note.note_type,
                category=note.category,
                tags=note.tags,
                is_pinned=note.is_pinned,
                is_private=note.is_private,
                status=note.status,
                parent_note_id=note.parent_note_id,
                linked_note_ids=note.linked_note_ids,
                word_count=note.word_count,
                reading_time_minutes=note.reading_time_minutes,
                created_at=note.created_at,
                updated_at=note.updated_at
            )
            for note in notes
        ]
        
        return NoteListResponse(
            notes=note_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=skip + per_page < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search notes: {str(e)}")