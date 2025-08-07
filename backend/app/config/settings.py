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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()