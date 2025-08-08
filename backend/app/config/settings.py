from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


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
    
    # Database - MongoDB
    MONGODB_URL: str = Field("mongodb://elenchus_admin:elenchus_password_2024@localhost:27018/elenchus", env="MONGODB_URL")
    MONGODB_DATABASE: str = Field("elenchus", env="MONGODB_DATABASE")
    
    # Redis Cache
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    
    # Authentication
    SECRET_KEY: str = Field("your-secret-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # AI Services
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    LMSTUDIO_BASE_URL: Optional[str] = Field(None, env="LMSTUDIO_BASE_URL")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
    # Langfuse Tracing
    LANGFUSE_SECRET_KEY: Optional[str] = Field(None, env="LANGFUSE_SECRET_KEY")
    LANGFUSE_PUBLIC_KEY: Optional[str] = Field(None, env="LANGFUSE_PUBLIC_KEY")
    LANGFUSE_HOST: str = Field("https://cloud.langfuse.com", env="LANGFUSE_HOST")
    
    # RAG Stack Configuration
    # Vector Database - Qdrant
    QDRANT_URL: str = Field("http://localhost:6333", env="QDRANT_URL")
    QDRANT_COLLECTION_NAME: str = Field("legal_documents", env="QDRANT_COLLECTION_NAME")
    QDRANT_API_KEY: Optional[str] = Field(None, env="QDRANT_API_KEY")
    
    # Embeddings Configuration
    EMBED_MODEL: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBED_MODEL")
    EMBED_DIMENSION: int = Field(384, env="EMBED_DIMENSION")
    EMBEDDING_BATCH_SIZE: int = Field(32, env="EMBEDDING_BATCH_SIZE")
    
    # Google Cloud Platform Configuration
    GCP_PROJECT: str = Field("legalai-462213", env="GCP_PROJECT")
    GCP_BUCKET: str = Field("legalai_documents", env="GCP_BUCKET")
    GCP_BUCKET_BASE_PATH: str = Field("user_docs", env="GCP_BUCKET_BASE_PATH")
    GCP_CREDENTIALS_PATH: Optional[str] = Field(None, env="GCP_CREDENTIALS_PATH")
    GCP_CREDENTIALS_JSON: Optional[str] = Field(None, env="GCP_CREDENTIALS_JSON")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # RAG Performance Settings
    MAX_CHUNK_SIZE: int = Field(800, env="MAX_CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(100, env="CHUNK_OVERLAP")
    SEARCH_TOP_K: int = Field(8, env="SEARCH_TOP_K")
    MAX_CONTEXT_LENGTH: int = Field(4000, env="MAX_CONTEXT_LENGTH")
    
    # Background Worker Configuration
    WORKER_CONCURRENCY: int = Field(4, env="WORKER_CONCURRENCY")
    TASK_TIMEOUT: int = Field(3600, env="TASK_TIMEOUT")
    RETRY_ATTEMPTS: int = Field(3, env="RETRY_ATTEMPTS")
    RQ_REDIS_URL: str = Field("redis://localhost:6379/1", env="RQ_REDIS_URL")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()