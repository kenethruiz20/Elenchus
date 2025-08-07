"""API v1 package."""
from fastapi import APIRouter
from .research import router as research_router
from .messages import router as messages_router
from .sources import router as sources_router
from .notes import router as notes_router

api_v1_router = APIRouter(prefix="/api/v1")

# Include all routers
api_v1_router.include_router(research_router)
api_v1_router.include_router(messages_router)
api_v1_router.include_router(sources_router)
api_v1_router.include_router(notes_router)