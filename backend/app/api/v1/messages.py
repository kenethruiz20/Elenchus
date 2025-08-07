"""Messages API endpoints for chat conversations."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from beanie import PydanticObjectId

from app.models import Research, Message
from app.schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageListResponse,
    ConversationResponse,
    MessageSendRequest,
    MessageSendResponse
)

router = APIRouter(prefix="/messages", tags=["messages"])

# Mock user dependency - replace with actual auth
async def get_current_user_id() -> str:
    """Mock user ID - replace with actual authentication."""
    return "user_123"  # TODO: Implement actual authentication


@router.get("/research/{research_id}", response_model=ConversationResponse)
async def get_conversation(
    research_id: str,
    user_id: str = Depends(get_current_user_id)
) -> ConversationResponse:
    """Get complete conversation for a research."""
    try:
        # Verify research exists and user has access
        research = await Research.get(PydanticObjectId(research_id))
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        if research.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all messages for the conversation
        messages = await Message.find({"research_id": research_id}).sort([("sequence_number", 1)]).to_list()
        
        # Convert to response format
        message_responses = [
            MessageResponse(
                id=str(msg.id),
                research_id=msg.research_id,
                content=msg.content,
                role=msg.role,
                user_id=msg.user_id,
                created_at=msg.created_at,
                model=msg.model,
                tokens_used=msg.tokens_used,
                response_time_ms=msg.response_time_ms,
                sequence_number=msg.sequence_number,
                is_hidden=msg.is_hidden,
                is_error=msg.is_error,
                error_code=msg.error_code,
                metadata=msg.metadata
            )
            for msg in messages
        ]
        
        return ConversationResponse(
            research_id=research_id,
            research_title=research.title,
            messages=message_responses,
            total_messages=len(message_responses),
            model=research.model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.post("/research/{research_id}/send", response_model=MessageSendResponse)
async def send_message(
    research_id: str,
    message_request: MessageSendRequest,
    user_id: str = Depends(get_current_user_id)
) -> MessageSendResponse:
    """Send a message to the AI and get response."""
    try:
        # Verify research exists and user has access
        research = await Research.get(PydanticObjectId(research_id))
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        if research.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get next sequence number
        last_message = await Message.find({"research_id": research_id}).sort([("sequence_number", -1)]).first_or_none()
        next_seq = (last_message.sequence_number + 1) if last_message else 1
        
        # Create user message
        user_message = Message(
            research_id=research_id,
            content=message_request.message,
            role="user",
            user_id=user_id,
            sequence_number=next_seq
        )
        await user_message.create()
        
        # TODO: Integrate with actual LLM (Google Gemini)
        # For now, create a mock assistant response
        assistant_response = f"This is a mock response to: '{message_request.message}'. Integration with Google Gemini will be implemented in the next phase."
        
        # Create assistant message
        assistant_message = Message(
            research_id=research_id,
            content=assistant_response,
            role="assistant",
            user_id=user_id,
            sequence_number=next_seq + 1,
            model=research.model,
            tokens_used=50,  # Mock value
            response_time_ms=1000.0  # Mock value
        )
        await assistant_message.create()
        
        # Update research timestamp
        await research.update({"$set": {"updated_at": datetime.utcnow()}})
        
        # Get total message count
        total_messages = await Message.find({"research_id": research_id}).count()
        
        return MessageSendResponse(
            user_message=MessageResponse(
                id=str(user_message.id),
                research_id=user_message.research_id,
                content=user_message.content,
                role=user_message.role,
                user_id=user_message.user_id,
                created_at=user_message.created_at,
                model=user_message.model,
                tokens_used=user_message.tokens_used,
                response_time_ms=user_message.response_time_ms,
                sequence_number=user_message.sequence_number,
                is_hidden=user_message.is_hidden,
                is_error=user_message.is_error,
                error_code=user_message.error_code,
                metadata=user_message.metadata
            ),
            assistant_message=MessageResponse(
                id=str(assistant_message.id),
                research_id=assistant_message.research_id,
                content=assistant_message.content,
                role=assistant_message.role,
                user_id=assistant_message.user_id,
                created_at=assistant_message.created_at,
                model=assistant_message.model,
                tokens_used=assistant_message.tokens_used,
                response_time_ms=assistant_message.response_time_ms,
                sequence_number=assistant_message.sequence_number,
                is_hidden=assistant_message.is_hidden,
                is_error=assistant_message.is_error,
                error_code=assistant_message.error_code,
                metadata=assistant_message.metadata
            ),
            research_id=research_id,
            total_messages=total_messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    user_id: str = Depends(get_current_user_id)
) -> MessageResponse:
    """Get a specific message by ID."""
    try:
        message = await Message.get(PydanticObjectId(message_id))
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check ownership
        if message.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return MessageResponse(
            id=str(message.id),
            research_id=message.research_id,
            content=message.content,
            role=message.role,
            user_id=message.user_id,
            created_at=message.created_at,
            model=message.model,
            tokens_used=message.tokens_used,
            response_time_ms=message.response_time_ms,
            sequence_number=message.sequence_number,
            is_hidden=message.is_hidden,
            is_error=message.is_error,
            error_code=message.error_code,
            metadata=message.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get message: {str(e)}")


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    update_data: MessageUpdate,
    user_id: str = Depends(get_current_user_id)
) -> MessageResponse:
    """Update a message (limited to user messages)."""
    try:
        message = await Message.get(PydanticObjectId(message_id))
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check ownership
        if message.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Only allow updating user messages (not assistant messages)
        if message.role != "user":
            raise HTTPException(status_code=400, detail="Can only update user messages")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            await message.update({"$set": update_dict})
            
            # Refresh the document
            message = await Message.get(PydanticObjectId(message_id))
        
        return MessageResponse(
            id=str(message.id),
            research_id=message.research_id,
            content=message.content,
            role=message.role,
            user_id=message.user_id,
            created_at=message.created_at,
            model=message.model,
            tokens_used=message.tokens_used,
            response_time_ms=message.response_time_ms,
            sequence_number=message.sequence_number,
            is_hidden=message.is_hidden,
            is_error=message.is_error,
            error_code=message.error_code,
            metadata=message.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update message: {str(e)}")


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a message (soft delete by hiding)."""
    try:
        message = await Message.get(PydanticObjectId(message_id))
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Check ownership
        if message.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Only allow deleting user messages
        if message.role != "user":
            raise HTTPException(status_code=400, detail="Can only delete user messages")
        
        # Soft delete by hiding
        await message.update({"$set": {"is_hidden": True}})
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")