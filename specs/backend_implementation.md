# FastAPI Backend Implementation Specification
## Elenchus Legal AI - Robust Backend Architecture

### Executive Summary
This document outlines the complete implementation of a robust FastAPI backend to replace the current minimal Chainlit implementation. The new backend will provide comprehensive authentication, security, conversation management, workflow execution, and Langfuse observability integration.

---

## 🚀 Implementation Status

### ✅ Phase 1: Project Foundation - **COMPLETED**
- **Status**: Fully implemented and tested
- **Completion Date**: January 2025
- **Server Running**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### ✅ MongoDB Integration & Docker Stack - **COMPLETED** 
- **Status**: Full stack deployment with MongoDB and Docker
- **Completion Date**: August 2025
- **MongoDB**: Running on port 27017
- **Backend**: FastAPI with MongoDB/Beanie ODM 
- **Frontend**: Next.js 14 with standalone output
- **Redis**: Caching layer on port 6379
- **Docker Compose**: Full orchestration ready

### Current Implementation
```
backend/
├── app/
│   ├── __init__.py                ✅ Created
│   ├── main.py                    ✅ FastAPI app with CORS & lifespan
│   └── config/
│       ├── __init__.py            ✅ Created
│       ├── settings.py            ✅ MongoDB configuration
│       └── database.py            ✅ Motor/Beanie setup
├── docker/
│   ├── Dockerfile.backend         ✅ FastAPI container
│   ├── Dockerfile.mongodb         ✅ MongoDB container
│   └── mongo-init/
│       └── 01-init-db.js         ✅ Database initialization
├── requirements/
│   ├── base.txt                   ✅ Full dependencies
│   ├── dev.txt                    ✅ Development tools
│   ├── minimal.txt               ✅ Phase 1 essentials
│   └── mongodb.txt               ✅ MongoDB dependencies
├── venv/                         ✅ Python virtual environment
├── .env                          ✅ MongoDB configuration
└── server.log                    ✅ Server logs
```

### 🐳 Docker Stack (NEW)
```
/
├── docker-compose.yml            ✅ Full stack orchestration
├── Dockerfile.frontend           ✅ Next.js container
└── public/                       ✅ Static assets
    └── .gitkeep
```

### 🚀 Running the Stack
```bash
# Full Docker Stack
docker-compose up -d

# Individual services
docker-compose up mongodb        # Database only
docker-compose up backend        # API only  
docker-compose up frontend       # UI only
docker-compose up redis          # Cache only

# Check status
docker-compose ps

# View logs
docker logs elenchus-backend
docker logs elenchus-frontend
docker logs elenchus-mongodb
```

### 🌐 Service URLs
- **Frontend**: http://localhost:3000 (Next.js)
- **Backend API**: http://localhost:8000 (FastAPI)
- **API Docs**: http://localhost:8000/docs (Swagger)
- **MongoDB**: mongodb://localhost:27017
- **Redis**: redis://localhost:6379

### 📦 Installed Dependencies (Updated)
```
# Core FastAPI
fastapi==0.105.0                 # Web framework
uvicorn[standard]==0.24.0        # ASGI server
pydantic==2.5.0                  # Data validation
pydantic-settings==2.1.0         # Settings management

# MongoDB Stack  
motor==3.3.2                     # Async MongoDB driver
pymongo==4.6.1                   # MongoDB driver
beanie==1.26.0                   # Async ODM with Pydantic
dnspython==2.4.2                 # DNS resolution for MongoDB
```

### 🎯 Next Phases Ready
✅ **Database**: MongoDB with Beanie ODM integrated  
⏳ **Auth & Security**: JWT, OAuth, RBAC implementation  
⏳ **API Endpoints**: CRUD operations and business logic  
⏳ **File Storage**: Document upload and processing  
⏳ **Background Tasks**: Celery with Redis  
⏳ **Langfuse Integration**: LLM observability and analytics

### 📊 Implementation Progress
| Phase | Status | Completion | Features |
|-------|--------|------------|----------|
| **Phase 1** | ✅ **COMPLETED** | 100% | Foundation, FastAPI setup, basic endpoints |
| **Phase 2** | 🔄 Ready | 0% | Database models, PostgreSQL, migrations |
| **Phase 3** | 📋 Planned | 0% | Authentication, JWT, security |
| **Phase 4** | 📋 Planned | 0% | Core APIs, chat, conversations |
| **Phase 5** | 📋 Planned | 0% | Services, document processing |
| **Phase 6** | 📋 Planned | 0% | Langfuse integration |
| **Phase 7** | 📋 Planned | 0% | Docker deployment |

### 🔧 Technical Details - Phase 1
**Created Files:**
- `app/main.py` - FastAPI application with lifespan management
- `app/config/settings.py` - Pydantic settings with environment support
- `requirements/minimal.txt` - Essential dependencies for Phase 1
- `.env` - Environment configuration
- `venv/` - Isolated Python environment

**Features Implemented:**
- ✅ FastAPI application with automatic OpenAPI docs
- ✅ CORS middleware for frontend integration
- ✅ Pydantic settings with environment variable support
- ✅ Health check endpoint
- ✅ Application lifespan management
- ✅ Development server with hot reload

**Server Verification:**
```bash
# Server is running on PID 98040
curl http://localhost:8000/          # Returns API info
curl http://localhost:8000/health    # Returns {"status":"ok","service":"Elenchus Legal AI"}
curl http://localhost:8000/openapi.json  # Returns OpenAPI specification
```

---

## 1. Architecture Overview

### 1.1 Current State Analysis
Based on the frontend analysis, the application requires backend support for:
- **Dashboard Analytics** (`/dashboard`) - Usage statistics, token consumption, activity logs
- **Research Interface** (`/research`) - Three-panel NotebookLM-style interface with chat
- **Workflow Management** (`/workflows`) - Legal workflow execution and management
- **Settings Management** (`/settings`) - User preferences and configuration
- **Authentication** - User sessions and security
- **Document Processing** - PDF/DOC parsing and analysis

### 1.2 Target Architecture
```
┌─────────────────────────────────────────────────┐
│                Next.js Frontend                  │
│  ┌─────────────────────────────────────────┐   │
│  │  Dashboard | Research | Workflows       │   │
│  │  Settings  | Auth     | Components      │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/WebSocket
                  ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                     │
│  ┌─────────────────────────────────────────┐   │
│  │         API Gateway & Router            │   │
│  │  ┌─────────────────────────────────┐    │   │
│  │  │  Auth     │ Chat    │ Workflows │    │   │
│  │  │  Users    │ History │ Analytics │    │   │
│  │  │  Docs     │ Sources │ Settings  │    │   │
│  │  └─────────────────────────────────┘    │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │         Core Services Layer             │   │
│  │  ┌─────────────────────────────────┐    │   │
│  │  │  AI Service  │ Document Service │    │   │
│  │  │  Workflow    │ Analytics Service│    │   │
│  │  │  Auth        │ Langfuse Service │    │   │
│  │  └─────────────────────────────────┘    │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │         Data Access Layer               │   │
│  │  ┌─────────────────────────────────┐    │   │
│  │  │  PostgreSQL  │ Redis Cache      │    │   │
│  │  │  File Store  │ Vector DB        │    │   │
│  │  └─────────────────────────────────┘    │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│          External Integrations                   │
│  ┌─────────────────────────────────────────┐   │
│  │  Google Gemini  │ Langfuse Server      │   │
│  │  OpenAI         │ Email Service        │   │
│  │  Document OCR   │ File Storage (GCS)   │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 2. Project Structure

### 2.1 Directory Layout
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Configuration management
│   │   └── database.py         # Database configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependencies (auth, db sessions)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── chat.py        # Chat and messaging
│   │       ├── workflows.py   # Workflow management
│   │       ├── documents.py   # Document processing
│   │       ├── analytics.py   # Usage analytics
│   │       ├── users.py       # User management
│   │       └── health.py      # Health checks
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication logic
│   │   ├── security.py       # Security utilities
│   │   └── exceptions.py     # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py     # AI model integration
│   │   ├── document_service.py  # Document processing
│   │   ├── workflow_service.py  # Workflow execution
│   │   ├── analytics_service.py # Analytics and reporting
│   │   ├── langfuse_service.py  # Observability
│   │   └── notification_service.py # Email/notifications
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User models
│   │   ├── conversation.py   # Chat models
│   │   ├── document.py       # Document models
│   │   ├── workflow.py       # Workflow models
│   │   └── analytics.py      # Analytics models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication schemas
│   │   ├── chat.py           # Chat schemas
│   │   ├── workflow.py       # Workflow schemas
│   │   ├── document.py       # Document schemas
│   │   └── analytics.py      # Analytics schemas
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py           # Base database class
│   │   ├── session.py        # Database session management
│   │   └── migrations/       # Alembic migrations
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py     # File handling utilities
│       ├── pdf_parser.py     # PDF processing
│       ├── doc_parser.py     # DOC/DOCX processing
│       ├── vector_utils.py   # Vector embeddings
│       └── email_utils.py    # Email utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_auth.py         # Authentication tests
│   ├── test_chat.py         # Chat functionality tests
│   ├── test_workflows.py    # Workflow tests
│   └── test_analytics.py    # Analytics tests
├── alembic/                 # Database migrations
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
├── scripts/
│   ├── start.py            # Development server
│   ├── migrate.py          # Database migrations
│   └── seed.py             # Database seeding
├── requirements/
│   ├── base.txt            # Base requirements
│   ├── dev.txt             # Development requirements
│   └── prod.txt            # Production requirements
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 3. Core Dependencies

### 3.1 Production Dependencies (`requirements/base.txt`)
```txt
# FastAPI and ASGI
fastapi==0.105.0
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database
sqlalchemy==2.0.23
alembic==1.13.1
asyncpg==0.29.0        # PostgreSQL async driver
redis==5.0.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-decouple==3.8

# AI & ML
google-generativeai==0.3.2
langchain==0.0.340
langchain-google-genai==0.0.8
openai==1.3.7
sentence-transformers==2.2.2

# Document Processing
pypdf2==3.0.1
python-docx==1.1.0
pytesseract==0.3.10   # OCR for scanned docs
Pillow==10.1.0

# Observability
langfuse==3.0.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
prometheus-client==0.19.0

# Email & Notifications
emails==0.6.0
jinja2==3.1.2

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
aiofiles==23.2.1
python-dateutil==2.8.2
celery==5.3.4         # Background tasks
```

### 3.2 Development Dependencies (`requirements/dev.txt`)
```txt
-r base.txt

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
faker==20.1.0

# Code Quality
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1

# Development Tools
watchfiles==0.21.0
python-dotenv==1.0.0
```

---

## 4. Configuration Management

### 4.1 Settings Configuration (`app/config/settings.py`)
```python
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Elenchus Legal AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_MAX_OVERFLOW: int = 20
    
    # Redis Cache
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # Authentication
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(None, env="GOOGLE_CLIENT_SECRET")
    
    # AI Services
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    DEFAULT_AI_MODEL: str = "gemini-1.5-flash"
    
    # Langfuse Observability
    LANGFUSE_PUBLIC_KEY: Optional[str] = Field(None, env="LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = Field(None, env="LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = Field("http://localhost:3001", env="LANGFUSE_HOST")
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".doc", ".docx", ".txt"]
    
    # Google Cloud Storage (optional)
    GCS_BUCKET_NAME: Optional[str] = Field(None, env="GCS_BUCKET_NAME")
    GCS_CREDENTIALS_PATH: Optional[str] = Field(None, env="GCS_CREDENTIALS_PATH")
    
    # Email Configuration
    SMTP_HOST: Optional[str] = Field(None, env="SMTP_HOST")
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = Field(None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = True
    EMAIL_FROM: Optional[str] = Field(None, env="EMAIL_FROM")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://elenchus.legal",
    ]
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL environment variable is required")
        return v
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
```

### 4.2 Database Configuration (`app/config/database.py`)
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config.settings import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_POOL_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_database_session() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## 5. Database Models

### 5.1 User Model (`app/models/user.py`)
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # OAuth fields
    google_id = Column(String, unique=True, index=True)
    avatar_url = Column(String)
    
    # Profile information
    organization = Column(String)
    role = Column(String)
    preferences = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    documents = relationship("Document", back_populates="user")
    workflows = relationship("WorkflowExecution", back_populates="user")
    analytics = relationship("UserAnalytics", back_populates="user")
```

### 5.2 Conversation Model (`app/models/conversation.py`)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    
    # Conversation metadata
    session_id = Column(String, unique=True, index=True)
    context_summary = Column(Text)
    metadata = Column(JSON, default={})
    
    # State management
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    documents = relationship("Document", secondary="conversation_documents", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)
    message_type = Column(String, default="text")  # text, image, document, workflow_result
    
    # AI-specific fields
    model_used = Column(String)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    
    # Tracing
    trace_id = Column(String, index=True)
    span_id = Column(String)
    generation_id = Column(String)
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


# Association table for conversation-document many-to-many relationship
from sqlalchemy import Table
conversation_documents = Table(
    'conversation_documents',
    Base.metadata,
    Column('conversation_id', Integer, ForeignKey('conversations.id')),
    Column('document_id', Integer, ForeignKey('documents.id'))
)
```

### 5.3 Document Model (`app/models/document.py`)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Document metadata
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, doc, docx, txt
    file_size = Column(Integer)
    file_path = Column(String)
    storage_url = Column(String)  # For cloud storage
    
    # Content
    content = Column(Text)
    content_hash = Column(String, index=True)
    
    # Processing status
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text)
    
    # Vector embeddings
    embedding_id = Column(String)  # Reference to vector database
    chunk_count = Column(Integer, default=0)
    
    # Legal-specific metadata
    document_category = Column(String)  # contract, case_law, statute, brief, etc.
    jurisdiction = Column(String)
    practice_area = Column(String)
    keywords = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    conversations = relationship("Conversation", secondary="conversation_documents", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer)
    end_char = Column(Integer)
    
    # Vector embedding
    embedding_vector = Column(String)  # JSON serialized vector
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
```

### 5.4 Workflow Model (`app/models/workflow.py`)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.config.database import Base


class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template metadata
    name = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    icon = Column(String)
    
    # Workflow definition
    definition = Column(JSON, nullable=False)  # Workflow steps and configuration
    input_schema = Column(JSON)  # JSON schema for input validation
    output_schema = Column(JSON)  # JSON schema for output validation
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    estimated_duration = Column(Integer)  # Seconds
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_duration = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    executions = relationship("WorkflowExecution", back_populates="template")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    
    # Execution metadata
    execution_id = Column(String, unique=True, index=True)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING)
    
    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    
    # Progress tracking
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer)
    progress_percentage = Column(Float, default=0.0)
    
    # Error handling
    error_message = Column(Text)
    error_step = Column(Integer)
    
    # Performance metrics
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Tracing
    trace_id = Column(String, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    template = relationship("WorkflowTemplate", back_populates="executions")
    steps = relationship("WorkflowStep", back_populates="execution", cascade="all, delete-orphan")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    
    # Step metadata
    step_name = Column(String, nullable=False)
    step_index = Column(Integer, nullable=False)
    step_type = Column(String, nullable=False)  # ai_query, document_analysis, email_send, etc.
    
    # Step data
    input_data = Column(JSON)
    output_data = Column(JSON)
    
    # Status
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING)
    error_message = Column(Text)
    
    # Performance
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="steps")
```

### 5.5 Analytics Model (`app/models/analytics.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class UserAnalytics(Base):
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Date for aggregation
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Usage metrics
    total_queries = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time = Column(Float, default=0.0)
    successful_queries = Column(Integer, default=0)
    failed_queries = Column(Integer, default=0)
    
    # Document metrics
    documents_uploaded = Column(Integer, default=0)
    documents_analyzed = Column(Integer, default=0)
    total_document_size = Column(Integer, default=0)
    
    # Workflow metrics
    workflows_executed = Column(Integer, default=0)
    workflows_completed = Column(Integer, default=0)
    workflows_failed = Column(Integer, default=0)
    
    # Cost tracking
    estimated_cost = Column(Float, default=0.0)
    
    # Session metrics
    active_sessions = Column(Integer, default=0)
    session_duration = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")


class SystemAnalytics(Base):
    __tablename__ = "system_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Date for aggregation
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # System metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    
    # Usage metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time = Column(Float, default=0.0)
    p95_response_time = Column(Float, default=0.0)
    uptime_percentage = Column(Float, default=100.0)
    
    # Resource usage
    cpu_usage_avg = Column(Float, default=0.0)
    memory_usage_avg = Column(Float, default=0.0)
    disk_usage_avg = Column(Float, default=0.0)
    
    # AI metrics
    total_ai_requests = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    estimated_ai_cost = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## 6. API Endpoints

### 6.1 Authentication API (`app/api/v1/auth.py`)
```python
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_database_session
from app.core.auth import authenticate_user, create_access_token, get_password_hash
from app.core.security import verify_password
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse, UserLogin
from app.services.langfuse_service import LangfuseService
from app.config.settings import settings

router = APIRouter()
langfuse_service = LangfuseService()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_database_session)
) -> Any:
    """Login endpoint."""
    
    # Track login attempt
    trace = langfuse_service.create_trace(
        name="user_login",
        input={"email": form_data.username},
        metadata={"endpoint": "/auth/login"}
    )
    
    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            langfuse_service.update_trace(trace.id, status="ERROR", output={"error": "Invalid credentials"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif not user.is_active:
            langfuse_service.update_trace(trace.id, status="ERROR", output={"error": "Inactive user"})
            raise HTTPException(status_code=400, detail="Inactive user")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Update last login
        user.last_login = func.now()
        await db.commit()
        
        langfuse_service.update_trace(
            trace.id, 
            status="SUCCESS", 
            output={"user_id": user.id, "access_granted": True}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse.from_orm(user)
        }
    
    except Exception as e:
        langfuse_service.update_trace(trace.id, status="ERROR", output={"error": str(e)})
        raise


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_database_session)
) -> Any:
    """User registration endpoint."""
    
    trace = langfuse_service.create_trace(
        name="user_registration",
        input={"email": user_data.email, "full_name": user_data.full_name},
        metadata={"endpoint": "/auth/register"}
    )
    
    try:
        # Check if user already exists
        existing_user = await db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            langfuse_service.update_trace(trace.id, status="ERROR", output={"error": "Email already registered"})
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system."
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            organization=user_data.organization,
            role=user_data.role,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        langfuse_service.update_trace(
            trace.id, 
            status="SUCCESS", 
            output={"user_id": user.id, "registered": True}
        )
        
        return UserResponse.from_orm(user)
    
    except Exception as e:
        await db.rollback()
        langfuse_service.update_trace(trace.id, status="ERROR", output={"error": str(e)})
        raise


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Refresh access token."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Logout endpoint (token invalidation would be handled by frontend)."""
    
    langfuse_service.create_event(
        name="user_logout",
        input={"user_id": current_user.id},
        metadata={"endpoint": "/auth/logout"}
    )
    
    return {"message": "Successfully logged out"}
```

### 6.2 Chat API (`app/api/v1/chat.py`)
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_database_session
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.chat import (
    ConversationCreate, ConversationResponse, MessageCreate, MessageResponse,
    ChatRequest, ChatResponse
)
from app.services.ai_service import AIService
from app.services.langfuse_service import LangfuseService
from app.utils.websocket_manager import WebSocketManager

router = APIRouter()
ai_service = AIService()
langfuse_service = LangfuseService()
websocket_manager = WebSocketManager()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new conversation."""
    
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
        session_id=conversation_data.session_id,
        metadata=conversation_data.metadata or {}
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    # Track conversation creation
    langfuse_service.create_event(
        name="conversation_created",
        input={"conversation_id": conversation.id, "title": conversation.title},
        metadata={"user_id": current_user.id}
    )
    
    return ConversationResponse.from_orm(conversation)


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get user's conversations."""
    
    conversations = await db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_active == True
    ).offset(skip).limit(limit).all()
    
    return [ConversationResponse.from_orm(conv) for conv in conversations]


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get messages from a conversation."""
    
    # Verify conversation ownership
    conversation = await db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    
    return [MessageResponse.from_orm(msg) for msg in messages]


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Handle chat completion request."""
    
    # Create or get conversation
    conversation = None
    if chat_request.conversation_id:
        conversation = await db.query(Conversation).filter(
            Conversation.id == chat_request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=chat_request.content[:50] + "..." if len(chat_request.content) > 50 else chat_request.content,
            session_id=chat_request.session_id
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Create user message
    user_message = Message(
        conversation_id=conversation.id,
        content=chat_request.content,
        is_user=True,
        trace_id=chat_request.trace_id
    )
    db.add(user_message)
    
    # Start Langfuse generation tracking
    generation = langfuse_service.create_generation(
        name="chat_completion",
        trace_id=chat_request.trace_id,
        input=chat_request.content,
        model=chat_request.model or ai_service.default_model,
        metadata={
            "conversation_id": conversation.id,
            "user_id": current_user.id,
            "sources_count": len(chat_request.sources) if chat_request.sources else 0
        }
    )
    
    try:
        # Get AI response
        ai_response = await ai_service.generate_response(
            message=chat_request.content,
            conversation_history=await _get_conversation_history(conversation.id, db),
            sources=chat_request.sources,
            model=chat_request.model,
            trace_id=chat_request.trace_id
        )
        
        # Create AI message
        ai_message = Message(
            conversation_id=conversation.id,
            content=ai_response.content,
            is_user=False,
            model_used=ai_response.model,
            prompt_tokens=ai_response.usage.prompt_tokens,
            completion_tokens=ai_response.usage.completion_tokens,
            total_tokens=ai_response.usage.total_tokens,
            trace_id=chat_request.trace_id,
            generation_id=generation.id
        )
        db.add(ai_message)
        
        await db.commit()
        
        # Update Langfuse generation
        langfuse_service.update_generation(
            generation.id,
            output=ai_response.content,
            usage={
                "prompt_tokens": ai_response.usage.prompt_tokens,
                "completion_tokens": ai_response.usage.completion_tokens,
                "total_tokens": ai_response.usage.total_tokens
            },
            end_time=ai_response.completion_time
        )
        
        return ChatResponse(
            message=MessageResponse.from_orm(ai_message),
            conversation_id=conversation.id,
            usage=ai_response.usage
        )
        
    except Exception as e:
        await db.rollback()
        langfuse_service.update_generation(
            generation.id,
            status="ERROR",
            output={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
    token: str,
    db: AsyncSession = Depends(get_database_session)
):
    """WebSocket endpoint for real-time chat."""
    
    # Authenticate user (implement token validation)
    user = await authenticate_websocket_user(token, db)
    if not user:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Verify conversation access
    conversation = await db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conversation:
        await websocket.close(code=1008, reason="Conversation not found")
        return
    
    await websocket_manager.connect(websocket, conversation_id, user.id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message (similar to chat_completion but with streaming)
            await process_websocket_message(data, conversation, user, db, websocket)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, conversation_id, user.id)


async def _get_conversation_history(conversation_id: int, db: AsyncSession) -> List[Message]:
    """Get conversation history for context."""
    messages = await db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(10).all()
    
    return list(reversed(messages))
```

### 6.3 Workflow API (`app/api/v1/workflows.py`)
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_database_session
from app.models.user import User
from app.models.workflow import WorkflowTemplate, WorkflowExecution, WorkflowStatus
from app.schemas.workflow import (
    WorkflowTemplateResponse, WorkflowExecutionCreate, WorkflowExecutionResponse,
    WorkflowExecutionUpdate
)
from app.services.workflow_service import WorkflowService
from app.services.langfuse_service import LangfuseService

router = APIRouter()
workflow_service = WorkflowService()
langfuse_service = LangfuseService()


@router.get("/templates", response_model=List[WorkflowTemplateResponse])
async def get_workflow_templates(
    category: Optional[str] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_database_session)
):
    """Get available workflow templates."""
    
    query = db.query(WorkflowTemplate).filter(WorkflowTemplate.is_active == is_active)
    
    if category:
        query = query.filter(WorkflowTemplate.category == category)
    
    templates = await query.offset(skip).limit(limit).all()
    return [WorkflowTemplateResponse.from_orm(template) for template in templates]


@router.get("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def get_workflow_template(
    template_id: int,
    db: AsyncSession = Depends(get_database_session)
):
    """Get specific workflow template."""
    
    template = await db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == template_id,
        WorkflowTemplate.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    
    return WorkflowTemplateResponse.from_orm(template)


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    execution_data: WorkflowExecutionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Execute a workflow."""
    
    # Get workflow template
    template = await db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == execution_data.template_id,
        WorkflowTemplate.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    
    # Create execution record
    execution = WorkflowExecution(
        user_id=current_user.id,
        template_id=template.id,
        execution_id=execution_data.execution_id or str(uuid.uuid4()),
        input_data=execution_data.input_data,
        total_steps=len(template.definition.get("steps", [])),
        trace_id=execution_data.trace_id
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # Start workflow execution in background
    background_tasks.add_task(
        workflow_service.execute_workflow,
        execution.id,
        template.definition,
        execution_data.input_data,
        current_user.id
    )
    
    # Track workflow execution start
    langfuse_service.create_event(
        name="workflow_execution_started",
        trace_id=execution_data.trace_id,
        input={
            "execution_id": execution.execution_id,
            "template_name": template.name,
            "input_data": execution_data.input_data
        },
        metadata={"user_id": current_user.id}
    )
    
    return WorkflowExecutionResponse.from_orm(execution)


@router.get("/executions", response_model=List[WorkflowExecutionResponse])
async def get_workflow_executions(
    status: Optional[WorkflowStatus] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get user's workflow executions."""
    
    query = db.query(WorkflowExecution).filter(
        WorkflowExecution.user_id == current_user.id
    ).options(selectinload(WorkflowExecution.template))
    
    if status:
        query = query.filter(WorkflowExecution.status == status)
    
    executions = await query.order_by(
        WorkflowExecution.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [WorkflowExecutionResponse.from_orm(execution) for execution in executions]


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get specific workflow execution."""
    
    execution = await db.query(WorkflowExecution).filter(
        WorkflowExecution.execution_id == execution_id,
        WorkflowExecution.user_id == current_user.id
    ).options(
        selectinload(WorkflowExecution.template),
        selectinload(WorkflowExecution.steps)
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Workflow execution not found")
    
    return WorkflowExecutionResponse.from_orm(execution)


@router.post("/executions/{execution_id}/cancel")
async def cancel_workflow_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Cancel a running workflow execution."""
    
    execution = await db.query(WorkflowExecution).filter(
        WorkflowExecution.execution_id == execution_id,
        WorkflowExecution.user_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Workflow execution not found")
    
    if execution.status not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed workflow")
    
    # Cancel the workflow
    await workflow_service.cancel_workflow(execution.id)
    
    execution.status = WorkflowStatus.CANCELLED
    await db.commit()
    
    # Track cancellation
    langfuse_service.create_event(
        name="workflow_execution_cancelled",
        input={"execution_id": execution_id},
        metadata={"user_id": current_user.id}
    )
    
    return {"message": "Workflow execution cancelled"}


@router.get("/categories")
async def get_workflow_categories(
    db: AsyncSession = Depends(get_database_session)
):
    """Get available workflow categories."""
    
    categories = await db.query(WorkflowTemplate.category).filter(
        WorkflowTemplate.is_active == True
    ).distinct().all()
    
    return [category[0] for category in categories]
```

### 6.4 Analytics API (`app/api/v1/analytics.py`)
```python
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_

from app.api.deps import get_current_user, get_database_session
from app.models.user import User
from app.models.analytics import UserAnalytics, SystemAnalytics
from app.models.conversation import Message
from app.models.workflow import WorkflowExecution
from app.schemas.analytics import (
    AnalyticsResponse, UsageStatsResponse, TokenUsageResponse,
    WorkflowStatsResponse, ActivityLogResponse
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get user usage statistics."""
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    # Get aggregated analytics
    analytics = await db.query(UserAnalytics).filter(
        UserAnalytics.user_id == current_user.id,
        UserAnalytics.date >= start_date,
        UserAnalytics.date <= end_date
    ).all()
    
    if not analytics:
        return UsageStatsResponse(
            total_queries=0,
            total_tokens=0,
            documents_analyzed=0,
            avg_response_time=0.0,
            period_days=days
        )
    
    return UsageStatsResponse(
        total_queries=sum(a.total_queries for a in analytics),
        total_tokens=sum(a.total_tokens for a in analytics),
        documents_analyzed=sum(a.documents_analyzed for a in analytics),
        avg_response_time=sum(a.avg_response_time for a in analytics) / len(analytics),
        workflows_executed=sum(a.workflows_executed for a in analytics),
        estimated_cost=sum(a.estimated_cost for a in analytics),
        period_days=days
    )


@router.get("/tokens", response_model=List[TokenUsageResponse])
async def get_token_usage(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get daily token usage breakdown."""
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    analytics = await db.query(UserAnalytics).filter(
        UserAnalytics.user_id == current_user.id,
        UserAnalytics.date >= start_date,
        UserAnalytics.date <= end_date
    ).order_by(UserAnalytics.date.asc()).all()
    
    return [
        TokenUsageResponse(
            date=a.date,
            total_tokens=a.total_tokens,
            prompt_tokens=a.prompt_tokens,
            completion_tokens=a.completion_tokens,
            estimated_cost=a.estimated_cost
        ) for a in analytics
    ]


@router.get("/activity", response_model=List[ActivityLogResponse])
async def get_activity_log(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get recent user activity."""
    
    # Get recent messages
    messages = await db.query(Message).join(Message.conversation).filter(
        Message.conversation.has(user_id=current_user.id)
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    # Get recent workflow executions
    workflows = await db.query(WorkflowExecution).filter(
        WorkflowExecution.user_id == current_user.id
    ).order_by(WorkflowExecution.created_at.desc()).limit(limit).all()
    
    # Combine and sort activities
    activities = []
    
    for message in messages:
        activities.append(ActivityLogResponse(
            id=message.id,
            timestamp=message.created_at,
            action="AI Query" if message.is_user else "AI Response",
            document=None,
            tokens=message.total_tokens,
            response_time=None,
            status="completed"
        ))
    
    for workflow in workflows:
        activities.append(ActivityLogResponse(
            id=workflow.id,
            timestamp=workflow.created_at,
            action=f"Workflow: {workflow.template.name}",
            document=None,
            tokens=0,
            response_time=workflow.duration_seconds,
            status=workflow.status.value
        ))
    
    # Sort by timestamp descending
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    return activities[:limit]


@router.get("/workflows", response_model=WorkflowStatsResponse)
async def get_workflow_stats(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Get workflow execution statistics."""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get workflow execution stats
    stats = await db.query(
        func.count(WorkflowExecution.id).label("total_executions"),
        func.count(case([(WorkflowExecution.status == "completed", 1)])).label("completed"),
        func.count(case([(WorkflowExecution.status == "failed", 1)])).label("failed"),
        func.avg(WorkflowExecution.duration_seconds).label("avg_duration")
    ).filter(
        WorkflowExecution.user_id == current_user.id,
        WorkflowExecution.created_at >= start_date
    ).first()
    
    return WorkflowStatsResponse(
        total_executions=stats.total_executions or 0,
        completed_executions=stats.completed or 0,
        failed_executions=stats.failed or 0,
        avg_duration_seconds=float(stats.avg_duration or 0),
        success_rate=float(stats.completed or 0) / max(stats.total_executions or 1, 1) * 100,
        period_days=days
    )


@router.post("/refresh")
async def refresh_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database_session)
):
    """Manually refresh analytics data."""
    
    await analytics_service.update_user_analytics(current_user.id, db)
    
    return {"message": "Analytics refreshed successfully"}
```

---

## 7. Core Services

### 7.1 AI Service (`app/services/ai_service.py`)
```python
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from app.config.settings import settings
from app.schemas.chat import AIResponse, TokenUsage
from app.services.langfuse_service import LangfuseService
from app.models.conversation import Message


class AIService:
    def __init__(self):
        self.default_model = settings.DEFAULT_AI_MODEL
        self.langfuse_service = LangfuseService()
        
        # Initialize Google Gemini
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.gemini_client = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.7
            )
        
        # Legal-specific prompts
        self.legal_system_prompt = """
        You are Elenchus, an expert legal AI assistant specializing in legal research, 
        document analysis, and case law interpretation. You provide accurate, well-reasoned 
        legal analysis while being careful to note when advice requires human legal expertise.
        
        Key principles:
        - Provide thorough legal analysis based on available sources
        - Cite relevant cases, statutes, and regulations when applicable
        - Note jurisdictional limitations and variations in law
        - Recommend consulting with qualified legal professionals for specific advice
        - Maintain client confidentiality and professional standards
        """
    
    async def generate_response(
        self,
        message: str,
        conversation_history: List[Message] = None,
        sources: List[str] = None,
        model: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> AIResponse:
        """Generate AI response with legal context."""
        
        start_time = datetime.utcnow()
        model_name = model or self.default_model
        
        # Create Langfuse generation
        generation = self.langfuse_service.create_generation(
            name="legal_ai_response",
            trace_id=trace_id,
            input=message,
            model=model_name,
            metadata={
                "sources_count": len(sources) if sources else 0,
                "has_history": bool(conversation_history)
            }
        )
        
        try:
            # Build conversation context
            messages = [SystemMessage(content=self.legal_system_prompt)]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    if msg.is_user:
                        messages.append(HumanMessage(content=msg.content))
                    else:
                        messages.append(AIMessage(content=msg.content))
            
            # Add source context if available
            if sources:
                source_context = "\n\nRelevant source materials:\n"
                for i, source in enumerate(sources[:5], 1):  # Limit to 5 sources
                    source_context += f"{i}. {source}\n"
                
                context_message = f"Please analyze the following query in the context of the provided sources:{source_context}\n\nQuery: {message}"
                messages.append(HumanMessage(content=context_message))
            else:
                messages.append(HumanMessage(content=message))
            
            # Generate response using Gemini
            response = await self._generate_with_gemini(messages)
            
            end_time = datetime.utcnow()
            
            # Calculate token usage (approximate for Gemini)
            prompt_tokens = self._estimate_tokens(" ".join([m.content for m in messages]))
            completion_tokens = self._estimate_tokens(response.content)
            total_tokens = prompt_tokens + completion_tokens
            
            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
            
            # Update Langfuse generation
            self.langfuse_service.update_generation(
                generation.id,
                output=response.content,
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                end_time=end_time
            )
            
            return AIResponse(
                content=response.content,
                model=model_name,
                usage=usage,
                completion_time=end_time,
                generation_id=generation.id
            )
            
        except Exception as e:
            # Update generation with error
            self.langfuse_service.update_generation(
                generation.id,
                status="ERROR",
                output={"error": str(e)},
                end_time=datetime.utcnow()
            )
            raise
    
    async def _generate_with_gemini(self, messages: List) -> AIMessage:
        """Generate response using Google Gemini."""
        try:
            response = await self.gemini_client.agenerate([messages])
            return AIMessage(content=response.generations[0][0].text)
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    async def analyze_document(
        self,
        document_content: str,
        analysis_type: str = "general",
        specific_questions: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze legal document content."""
        
        analysis_prompt = f"""
        Please analyze the following legal document with focus on {analysis_type} analysis:
        
        Document Content:
        {document_content[:10000]}  # Limit content length
        
        Please provide:
        1. Document type and purpose
        2. Key legal concepts and terms
        3. Important clauses or provisions
        4. Potential issues or concerns
        5. Recommendations for review
        
        {'Additional questions to address: ' + '; '.join(specific_questions) if specific_questions else ''}
        """
        
        messages = [
            SystemMessage(content=self.legal_system_prompt),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = await self._generate_with_gemini(messages)
        
        return {
            "analysis": response.content,
            "document_type": analysis_type,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def generate_brief(
        self,
        case_facts: str,
        legal_issues: List[str],
        relevant_sources: List[str]
    ) -> str:
        """Generate a legal brief based on case facts and issues."""
        
        brief_prompt = f"""
        Please draft a legal brief based on the following information:
        
        Case Facts:
        {case_facts}
        
        Legal Issues:
        {chr(10).join([f"- {issue}" for issue in legal_issues])}
        
        Relevant Sources:
        {chr(10).join([f"- {source}" for source in relevant_sources[:10]])}
        
        Please structure the brief with:
        1. Statement of Facts
        2. Issues Presented
        3. Legal Analysis
        4. Conclusion
        5. Recommended Actions
        
        Ensure proper legal citation format and professional tone.
        """
        
        messages = [
            SystemMessage(content=self.legal_system_prompt),
            HumanMessage(content=brief_prompt)
        ]
        
        response = await self._generate_with_gemini(messages)
        return response.content
```

### 7.2 Langfuse Service (`app/services/langfuse_service.py`)
```python
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from langfuse import Langfuse
from langfuse.model import CreateTrace, CreateGeneration, CreateEvent

from app.config.settings import settings


class LangfuseService:
    def __init__(self):
        self.client = None
        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            self.client = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST,
                debug=settings.DEBUG
            )
    
    def create_trace(
        self,
        name: str,
        input: Optional[Dict[str, Any]] = None,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Optional[str]:
        """Create a new trace in Langfuse."""
        
        if not self.client:
            return None
        
        try:
            trace = self.client.trace(
                id=trace_id,
                name=name,
                input=input,
                output=output,
                metadata=metadata,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
            return trace.id
            
        except Exception as e:
            print(f"Error creating Langfuse trace: {e}")
            return None
    
    def update_trace(
        self,
        trace_id: str,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        end_time: Optional[datetime] = None
    ):
        """Update an existing trace."""
        
        if not self.client:
            return
        
        try:
            self.client.trace(
                id=trace_id,
                output=output,
                metadata=metadata,
                level=status,
                end_time=end_time or datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error updating Langfuse trace: {e}")
    
    def create_generation(
        self,
        name: str,
        trace_id: Optional[str] = None,
        input: Optional[str] = None,
        output: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None
    ) -> Optional[str]:
        """Create a generation (LLM call) in Langfuse."""
        
        if not self.client:
            return None
        
        try:
            generation = self.client.generation(
                name=name,
                trace_id=trace_id,
                input=input,
                output=output,
                model=model,
                metadata=metadata,
                start_time=start_time or datetime.utcnow()
            )
            return generation.id
            
        except Exception as e:
            print(f"Error creating Langfuse generation: {e}")
            return None
    
    def update_generation(
        self,
        generation_id: str,
        output: Optional[str] = None,
        usage: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        end_time: Optional[datetime] = None
    ):
        """Update a generation with completion data."""
        
        if not self.client:
            return
        
        try:
            self.client.generation(
                id=generation_id,
                output=output,
                usage=usage,
                metadata=metadata,
                level=status,
                end_time=end_time or datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error updating Langfuse generation: {e}")
    
    def create_event(
        self,
        name: str,
        trace_id: Optional[str] = None,
        input: Optional[Dict[str, Any]] = None,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create an event in Langfuse."""
        
        if not self.client:
            return
        
        try:
            self.client.event(
                name=name,
                trace_id=trace_id,
                input=input,
                output=output,
                metadata=metadata,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error creating Langfuse event: {e}")
    
    def create_score(
        self,
        trace_id: str,
        name: str,
        value: float,
        data_type: str = "NUMERIC",
        comment: Optional[str] = None
    ):
        """Create a score for a trace."""
        
        if not self.client:
            return
        
        try:
            self.client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                data_type=data_type,
                comment=comment
            )
            
        except Exception as e:
            print(f"Error creating Langfuse score: {e}")
    
    def flush(self):
        """Flush pending data to Langfuse."""
        
        if self.client:
            try:
                self.client.flush()
            except Exception as e:
                print(f"Error flushing Langfuse data: {e}")
    
    async def track_user_session(
        self,
        user_id: str,
        session_id: str,
        session_data: Dict[str, Any]
    ):
        """Track user session metrics."""
        
        self.create_event(
            name="user_session",
            input={
                "user_id": user_id,
                "session_id": session_id,
                "session_data": session_data
            },
            metadata={
                "event_type": "session_tracking",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def track_workflow_execution(
        self,
        workflow_name: str,
        execution_id: str,
        user_id: str,
        status: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        duration: Optional[float] = None
    ):
        """Track workflow execution."""
        
        trace_id = self.create_trace(
            name=f"workflow_{workflow_name}",
            input=input_data,
            output=output_data,
            metadata={
                "workflow_name": workflow_name,
                "execution_id": execution_id,
                "status": status,
                "duration_seconds": duration
            },
            user_id=user_id
        )
        
        return trace_id
    
    def get_analytics_data(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Get analytics data from Langfuse (if API supports it)."""
        
        # Note: This would require Langfuse API to support analytics queries
        # For now, return None and rely on local analytics
        return None
```

---

## 8. Deployment Configuration

### 8.1 Docker Configuration (`docker/Dockerfile`)
```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and user
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements/prod.txt requirements.txt
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.11-slim as production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/app/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directory
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=app:app /home/app/.local /home/app/.local

# Copy application code
COPY --chown=app:app . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 8.2 Docker Compose (`docker/docker-compose.yml`)
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: elenchus-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-elenchus}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-elenchus}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    networks:
      - elenchus-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-elenchus}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: elenchus-redis
    environment:
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - elenchus-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # FastAPI Backend
  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: elenchus-backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-elenchus}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-elenchus}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_HOST=${LANGFUSE_HOST:-http://langfuse:3000}
      - EMAIL_FROM=${EMAIL_FROM}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - elenchus-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Langfuse (Optional - for self-hosted observability)
  langfuse-postgres:
    image: postgres:15-alpine
    container_name: langfuse-postgres
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: ${LANGFUSE_POSTGRES_PASSWORD}
      POSTGRES_DB: langfuse
    volumes:
      - langfuse_postgres_data:/var/lib/postgresql/data
    networks:
      - elenchus-network
    restart: unless-stopped

  langfuse:
    image: langfuse/langfuse:latest
    container_name: langfuse-server
    depends_on:
      - langfuse-postgres
    environment:
      DATABASE_URL: postgresql://langfuse:${LANGFUSE_POSTGRES_PASSWORD}@langfuse-postgres:5432/langfuse
      NEXTAUTH_SECRET: ${LANGFUSE_NEXTAUTH_SECRET}
      NEXTAUTH_URL: ${LANGFUSE_PUBLIC_URL:-http://localhost:3001}
      TELEMETRY_ENABLED: false
    ports:
      - "3001:3000"
    networks:
      - elenchus-network
    restart: unless-stopped

  # Nginx Reverse Proxy (Optional)
  nginx:
    image: nginx:alpine
    container_name: elenchus-nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - elenchus-network
    restart: unless-stopped

networks:
  elenchus-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  langfuse_postgres_data:
```

### 8.3 Environment Configuration (`.env.example`)
```bash
# Application Settings
APP_NAME="Elenchus Legal AI"
DEBUG=false
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# Database Configuration
POSTGRES_USER=elenchus
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=elenchus
DATABASE_URL=postgresql+asyncpg://elenchus:your-postgres-password@localhost:5432/elenchus

# Redis Configuration
REDIS_PASSWORD=your-redis-password
REDIS_URL=redis://:your-redis-password@localhost:6379/0

# Google AI API
GOOGLE_API_KEY=your-google-api-key

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Langfuse Observability
LANGFUSE_PUBLIC_KEY=pk_lf_xxxxx
LANGFUSE_SECRET_KEY=sk_lf_xxxxx
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_POSTGRES_PASSWORD=langfuse-db-password
LANGFUSE_NEXTAUTH_SECRET=langfuse-nextauth-secret
LANGFUSE_PUBLIC_URL=http://localhost:3001

# Email Configuration (optional)
EMAIL_FROM=noreply@elenchus.legal
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Storage (optional - for Google Cloud Storage)
GCS_BUCKET_NAME=elenchus-documents
GCS_CREDENTIALS_PATH=/path/to/service-account.json

# CORS Origins
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://elenchus.legal"]
```

---

## 9. Development & Deployment Scripts

### 9.1 Development Start Script (`scripts/start.py`)
```python
#!/usr/bin/env python3
"""Development server startup script."""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import uvicorn
        import fastapi
        import sqlalchemy
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Run: pip install -r requirements/dev.txt")
        return False

def check_environment():
    """Check if environment variables are set."""
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "GOOGLE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Copy .env.example to .env and fill in the values")
        return False
    
    print("✓ Environment variables are set")
    return True

async def run_migrations():
    """Run database migrations."""
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Database migrations completed")
            return True
        else:
            print(f"✗ Migration failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ Alembic not found. Install with: pip install alembic")
        return False

def start_server():
    """Start the development server."""
    print("🚀 Starting Elenchus Backend Server...")
    
    os.environ["PYTHONPATH"] = str(Path(__file__).parent.parent)
    
    subprocess.run([
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ])

async def main():
    """Main startup sequence."""
    print("🔧 Elenchus Backend Development Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Run migrations
    if not await run_migrations():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    asyncio.run(main())
```

### 9.2 Production Deployment Script (`scripts/deploy.py`)
```python
#!/usr/bin/env python3
"""Production deployment script."""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def build_docker_image(tag: str = "latest"):
    """Build Docker image for production."""
    print(f"🐳 Building Docker image: elenchus-backend:{tag}")
    
    result = subprocess.run([
        "docker", "build",
        "-f", "docker/Dockerfile",
        "-t", f"elenchus-backend:{tag}",
        "."
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Docker image built successfully")
        return True
    else:
        print(f"✗ Docker build failed: {result.stderr}")
        return False

def deploy_to_cloud_run(project_id: str, region: str = "us-central1"):
    """Deploy to Google Cloud Run."""
    service_name = "elenchus-backend"
    image_name = f"gcr.io/{project_id}/{service_name}:latest"
    
    # Build and push image
    print(f"📤 Pushing image to Google Container Registry...")
    
    subprocess.run(["docker", "tag", f"elenchus-backend:latest", image_name])
    subprocess.run(["docker", "push", image_name])
    
    # Deploy to Cloud Run
    print(f"🚀 Deploying to Cloud Run...")
    
    result = subprocess.run([
        "gcloud", "run", "deploy", service_name,
        "--image", image_name,
        "--region", region,
        "--platform", "managed",
        "--allow-unauthenticated",
        "--memory", "2Gi",
        "--cpu", "2",
        "--min-instances", "0",
        "--max-instances", "10",
        "--port", "8000",
        "--timeout", "300s",
        "--concurrency", "80",
        "--set-env-vars", f"DATABASE_URL={os.getenv('DATABASE_URL')}",
        "--set-env-vars", f"SECRET_KEY={os.getenv('SECRET_KEY')}",
        "--set-env-vars", f"GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY')}",
        "--project", project_id
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Deployment successful!")
        print(f"Service URL: {result.stdout.strip()}")
        return True
    else:
        print(f"✗ Deployment failed: {result.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Deploy Elenchus Backend")
    parser.add_argument("--project", required=True, help="Google Cloud Project ID")
    parser.add_argument("--region", default="us-central1", help="Deployment region")
    parser.add_argument("--tag", default="latest", help="Docker image tag")
    
    args = parser.parse_args()
    
    print("🚀 Elenchus Backend Deployment")
    print("=" * 40)
    
    # Build Docker image
    if not build_docker_image(args.tag):
        sys.exit(1)
    
    # Deploy to Cloud Run
    if not deploy_to_cloud_run(args.project, args.region):
        sys.exit(1)
    
    print("✅ Deployment completed successfully!")

if __name__ == "__main__":
    main()
```

---

## 10. Testing Strategy

### 10.1 Test Configuration (`tests/conftest.py`)
```python
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config.database import get_database_session, Base
from app.config.settings import settings
from app.models.user import User
from app.core.auth import get_password_hash

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

TestAsyncSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client.""" 
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_database_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    response = await client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### 10.2 Authentication Tests (`tests/test_auth.py`)
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "newpassword123",
        "organization": "Test Corp",
        "role": "lawyer"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, test_user: User):
    """Test user login."""
    response = await client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "testpassword"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post("/api/v1/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user information."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    """Test accessing protected route without token."""
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
```

---

## 11. Performance & Monitoring

### 11.1 Monitoring Setup (`app/utils/monitoring.py`)
```python
import time
import psutil
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from functools import wraps

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method='POST', endpoint=func.__name__, status='success').inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method='POST', endpoint=func.__name__, status='error').inc()
            raise
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    
    return wrapper

def update_system_metrics():
    """Update system-level metrics."""
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    CPU_USAGE.set(psutil.cpu_percent(interval=1))

def start_metrics_server(port: int = 9090):
    """Start Prometheus metrics server."""
    start_http_server(port)
    print(f"Metrics server started on port {port}")
```

---

## 12. Quick Start Guide

### 12.1 Development Setup
```bash
# 1. Clone repository and setup
git clone <repository>
cd elenchus/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements/dev.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your configuration

# 5. Setup database
docker run -d --name postgres \
  -e POSTGRES_USER=elenchus \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=elenchus \
  -p 5432:5432 postgres:15

# 6. Run migrations
alembic upgrade head

# 7. Start development server
python scripts/start.py
```

### 12.2 Production Deployment
```bash
# 1. Build and deploy with Docker Compose
cp .env.example .env
# Configure production environment variables

docker-compose -f docker/docker-compose.yml up -d

# 2. Or deploy to Google Cloud Run
python scripts/deploy.py --project your-project-id

# 3. Verify deployment
curl http://localhost:8000/api/v1/health
```

---

## 13. Migration from Current Implementation

### 13.1 Migration Steps
1. **Phase 1**: Deploy new FastAPI backend alongside current Chainlit
2. **Phase 2**: Migrate authentication and user management
3. **Phase 3**: Migrate chat functionality with enhanced features
4. **Phase 4**: Add workflow management capabilities
5. **Phase 5**: Implement analytics and monitoring
6. **Phase 6**: Full Langfuse integration
7. **Phase 7**: Decommission Chainlit backend

### 13.2 Data Migration Script (`scripts/migrate_data.py`)
```python
#!/usr/bin/env python3
"""Data migration from Chainlit to FastAPI backend."""

import asyncio
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import AsyncSessionLocal
from app.models.user import User
from app.models.conversation import Conversation, Message


async def migrate_chainlit_data():
    """Migrate existing data from Chainlit."""
    async with AsyncSessionLocal() as db:
        # Migration logic here
        print("Data migration completed")

if __name__ == "__main__":
    asyncio.run(migrate_chainlit_data())
```

---

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "1", "content": "Analyze current app structure and frontend requirements", "status": "completed"}, {"id": "2", "content": "Design FastAPI backend architecture", "status": "completed"}, {"id": "3", "content": "Plan authentication and security implementation", "status": "completed"}, {"id": "4", "content": "Design conversation storage and history system", "status": "completed"}, {"id": "5", "content": "Plan workflow management system", "status": "completed"}, {"id": "6", "content": "Design Langfuse integration architecture", "status": "completed"}, {"id": "7", "content": "Create comprehensive backend implementation spec", "status": "completed"}]