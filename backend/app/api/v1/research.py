"""Research/Conversation API endpoints."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.models import Research, Message
from app.schemas.research import (
    ResearchCreate,
    ResearchUpdate,
    ResearchResponse,
    ResearchListResponse,
    ResearchSourceUpdate,
    ResearchNoteUpdate
)
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/research", tags=["research"])

async def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
    """Get current authenticated user ID."""
    return str(current_user.id)


@router.post("/", response_model=ResearchResponse)
async def create_research(
    research_data: ResearchCreate,
    user_id: str = Depends(get_current_user_id)
) -> ResearchResponse:
    """Create a new research/conversation."""
    try:
        # Create research document
        research = Research(
            title=research_data.title,
            user_id=user_id,
            model=research_data.model,
            tags=research_data.tags,
            temperature=research_data.temperature,
            max_tokens=research_data.max_tokens
        )
        
        await research.create()
        
        # Convert to response format
        return ResearchResponse(
            id=str(research.id),
            title=research.title,
            user_id=research.user_id,
            model=research.model,
            status=research.status,
            tags=research.tags,
            source_ids=research.source_ids,
            note_ids=research.note_ids,
            temperature=research.temperature,
            max_tokens=research.max_tokens,
            created_at=research.created_at,
            updated_at=research.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create research: {str(e)}")


@router.get("/", response_model=ResearchListResponse)
async def list_research(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    user_id: str = Depends(get_current_user_id)
) -> ResearchListResponse:
    """List user's research/conversations with pagination."""
    try:
        # Build query
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        if tag:
            query["tags"] = {"$in": [tag]}
        
        # Get total count
        total = await Research.find(query).count()
        
        # Get paginated results
        skip = (page - 1) * per_page
        research_docs = await Research.find(query).skip(skip).limit(per_page).sort([("updated_at", -1)]).to_list()
        
        # Convert to response format with message counts
        research_responses = []
        for research in research_docs:
            # Get message count and last activity
            message_count = await Message.find({"research_id": str(research.id)}).count()
            last_message = await Message.find({"research_id": str(research.id)}).sort([("created_at", -1)]).first_or_none()
            
            response = ResearchResponse(
                id=str(research.id),
                title=research.title,
                user_id=research.user_id,
                model=research.model,
                status=research.status,
                tags=research.tags,
                source_ids=research.source_ids,
                note_ids=research.note_ids,
                temperature=research.temperature,
                max_tokens=research.max_tokens,
                created_at=research.created_at,
                updated_at=research.updated_at,
                message_count=message_count,
                last_activity=last_message.created_at if last_message else research.updated_at
            )
            research_responses.append(response)
        
        return ResearchListResponse(
            research=research_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=skip + per_page < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list research: {str(e)}")


@router.get("/{research_id}", response_model=ResearchResponse)
async def get_research(
    research_id: str,
    user_id: str = Depends(get_current_user_id)
) -> ResearchResponse:
    """Get a specific research/conversation by ID."""
    try:
        research = await Research.get(PydanticObjectId(research_id))
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Check ownership
        if research.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get additional stats
        message_count = await Message.find({"research_id": research_id}).count()
        last_message = await Message.find({"research_id": research_id}).sort([("created_at", -1)]).first_or_none()
        
        return ResearchResponse(
            id=str(research.id),
            title=research.title,
            user_id=research.user_id,
            model=research.model,
            status=research.status,
            tags=research.tags,
            source_ids=research.source_ids,
            note_ids=research.note_ids,
            temperature=research.temperature,
            max_tokens=research.max_tokens,
            created_at=research.created_at,
            updated_at=research.updated_at,
            message_count=message_count,
            last_activity=last_message.created_at if last_message else research.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get research: {str(e)}")


@router.put("/{research_id}", response_model=ResearchResponse)
async def update_research(
    research_id: str,
    update_data: ResearchUpdate,
    user_id: str = Depends(get_current_user_id)
) -> ResearchResponse:
    """Update a research/conversation."""
    try:
        research = await Research.get(PydanticObjectId(research_id))
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Check ownership
        if research.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            await research.update({"$set": update_dict})
            
            # Refresh the document
            research = await Research.get(PydanticObjectId(research_id))
        
        return ResearchResponse(
            id=str(research.id),
            title=research.title,
            user_id=research.user_id,
            model=research.model,
            status=research.status,
            tags=research.tags,
            source_ids=research.source_ids,
            note_ids=research.note_ids,
            temperature=research.temperature,
            max_tokens=research.max_tokens,
            created_at=research.created_at,
            updated_at=research.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update research: {str(e)}")


@router.delete("/{research_id}")
async def delete_research(
    research_id: str,
    hard_delete: bool = Query(False, description="Permanently delete (default: soft delete)"),
    user_id: str = Depends(get_current_user_id)
):
    """Delete a research/conversation."""
    try:
        research = await Research.get(PydanticObjectId(research_id))
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Check ownership
        if research.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if hard_delete:
            # Hard delete: remove research and all associated messages
            await Message.find({"research_id": research_id}).delete_many()
            await research.delete()
        else:
            # Soft delete: mark as deleted
            await research.update({"$set": {"status": "deleted", "updated_at": datetime.utcnow()}})
        
        return {"message": "Research deleted successfully", "hard_delete": hard_delete}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete research: {str(e)}")


@router.put("/{research_id}/sources", response_model=ResearchResponse)
async def update_research_sources(
    research_id: str,
    sources_data: ResearchSourceUpdate,
    user_id: str = Depends(get_current_user_id)
) -> ResearchResponse:
    """Update the sources associated with a research."""
    try:
        research = await Research.get(PydanticObjectId(research_id))
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Check ownership
        if research.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update sources
        await research.update({
            "$set": {
                "source_ids": sources_data.source_ids,
                "updated_at": datetime.utcnow()
            }
        })
        
        # Refresh and return
        research = await Research.get(PydanticObjectId(research_id))
        return ResearchResponse(
            id=str(research.id),
            title=research.title,
            user_id=research.user_id,
            model=research.model,
            status=research.status,
            tags=research.tags,
            source_ids=research.source_ids,
            note_ids=research.note_ids,
            temperature=research.temperature,
            max_tokens=research.max_tokens,
            created_at=research.created_at,
            updated_at=research.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update research sources: {str(e)}")


@router.put("/{research_id}/notes", response_model=ResearchResponse)
async def update_research_notes(
    research_id: str,
    notes_data: ResearchNoteUpdate,
    user_id: str = Depends(get_current_user_id)
) -> ResearchResponse:
    """Update the notes associated with a research."""
    try:
        research = await Research.get(PydanticObjectId(research_id))
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Check ownership
        if research.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update notes
        await research.update({
            "$set": {
                "note_ids": notes_data.note_ids,
                "updated_at": datetime.utcnow()
            }
        })
        
        # Refresh and return
        research = await Research.get(PydanticObjectId(research_id))
        return ResearchResponse(
            id=str(research.id),
            title=research.title,
            user_id=research.user_id,
            model=research.model,
            status=research.status,
            tags=research.tags,
            source_ids=research.source_ids,
            note_ids=research.note_ids,
            temperature=research.temperature,
            max_tokens=research.max_tokens,
            created_at=research.created_at,
            updated_at=research.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update research notes: {str(e)}")