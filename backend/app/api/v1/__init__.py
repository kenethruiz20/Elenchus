"""API v1 package."""
from fastapi import APIRouter
from .research import router as research_router
from .messages import router as messages_router
from .sources import router as sources_router
from .notes import router as notes_router
from .models import router as models_router
from .auth import router as auth_router
# from .rag import router as rag_router  # Disabled until ML dependencies installed
from .rag_upload import router as rag_upload_router

api_v1_router = APIRouter(prefix="/api/v1")

# Include all routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(research_router)
api_v1_router.include_router(messages_router)
api_v1_router.include_router(sources_router)
api_v1_router.include_router(notes_router)
api_v1_router.include_router(models_router)
# api_v1_router.include_router(rag_router)  # Disabled until ML dependencies installed
api_v1_router.include_router(rag_upload_router)