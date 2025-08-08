from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.config.settings import settings
from app.config.database import init_database, close_database
from app.database import mongodb_manager, qdrant_manager
# from app.services.rag_service import rag_service  # Disabled until ML dependencies installed
from app.services.gcp_service import gcp_service
from app.services.rag_upload_service import rag_upload_service
from app.api import api_v1_router
from app.services.model_router import model_router, ModelMessage, ModelRole
from app.services.context_manager import context_manager, MessagePriority
from app.services.langfuse_service import langfuse_service
from app.middleware.rag_middleware import RAGSecurityMiddleware, RAGRequestLoggingMiddleware, RAGContextMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        # Initialize existing database
        await init_database()
        print("✅ Legacy database initialization completed")
        
        # Initialize RAG system databases
        await mongodb_manager.initialize()
        print("✅ RAG MongoDB initialization completed")
        
        await qdrant_manager.initialize()
        print("✅ RAG Qdrant initialization completed")
        
        # Initialize RAG upload service
        upload_success = await rag_upload_service.initialize()
        if upload_success:
            print("✅ RAG upload service initialization completed")
        else:
            print("⚠️  RAG upload service initialization failed")
        
        # Initialize RAG service (disabled until ML dependencies installed)
        # await rag_service.initialize()
        # print("✅ RAG service initialization completed")
        print("⚠️  RAG full service disabled until ML dependencies installed")
        
        # Initialize GCP service (optional)
        try:
            gcp_initialized = await gcp_service.initialize()
            if gcp_initialized:
                print("✅ GCP service initialization completed")
            else:
                print("⚠️  GCP service not configured (optional)")
        except Exception as e:
            print(f"⚠️  GCP service initialization failed: {e}")
        
        print("🚀 All systems initialized successfully")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_database()
    await mongodb_manager.close()
    await qdrant_manager.close()
    print("✅ All connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add RAG security middlewares
app.add_middleware(RAGSecurityMiddleware)
app.add_middleware(RAGRequestLoggingMiddleware)
app.add_middleware(RAGContextMiddleware)

# Include API routers
app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


class ChatRequest(BaseModel):
    content: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    content: str
    session_id: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Context-aware chat endpoint with conversation history and tracing."""
    session_id = None
    try:
        # Get or create session
        session_id = request.session_id or context_manager.create_session(
            metadata={"user_id": request.user_id} if request.user_id else None
        )
        
        # Add user message to context
        context_manager.add_message(
            session_id=session_id,
            content=request.content,
            role=ModelRole.USER,
            priority=MessagePriority.CRITICAL,
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()}
        )
        
        # Get conversation context for LLM
        conversation_messages = context_manager.get_context_for_llm(session_id)
        
        # Generate response using Gemini with full context
        llm_response = await model_router.generate_response(
            messages=conversation_messages,
            model="gemini-1.5-flash"
        )
        
        if llm_response.error:
            error_content = "I apologize, but I encountered an error while processing your request."
            return ChatResponse(
                content=error_content,
                session_id=session_id,
                error=llm_response.error
            )
        
        # Add assistant response to context
        context_manager.add_message(
            session_id=session_id,
            content=llm_response.content,
            role=ModelRole.ASSISTANT,
            priority=MessagePriority.HIGH,
            metadata={
                "model": "gemini-1.5-flash",
                "tokens_used": llm_response.tokens_used,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Trace conversation with Langfuse
        await langfuse_service.trace_conversation(
            session_id=session_id,
            messages=conversation_messages,
            model_response=llm_response.content,
            model_name="gemini-1.5-flash",
            metadata={
                "user_id": request.user_id,
                "tokens_used": llm_response.tokens_used,
                "response_time_ms": getattr(llm_response, 'response_time_ms', None)
            },
            tags=["legal-ai", "chat", "gemini"]
        )
        
        # Get session info for response metadata
        session_info = context_manager.get_session_info(session_id)
        
        return ChatResponse(
            content=llm_response.content,
            session_id=session_id,
            metadata={
                "message_count": session_info["message_count"] if session_info else 0,
                "tokens_used": llm_response.tokens_used,
                "model": "gemini-1.5-flash"
            }
        )
        
    except Exception as e:
        error_msg = "I'm sorry, but I'm having trouble processing your request right now."
        return ChatResponse(
            content=error_msg,
            session_id=session_id or "error",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )