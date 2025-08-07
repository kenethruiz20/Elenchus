from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config.settings import settings
import asyncio
from typing import Optional

# Global MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None


async def get_database_client() -> AsyncIOMotorClient:
    """Get MongoDB database client."""
    global mongodb_client
    if mongodb_client is None:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    return mongodb_client


async def get_database():
    """Get MongoDB database."""
    client = await get_database_client()
    return client[settings.MONGODB_DATABASE]


async def init_database():
    """Initialize database connection and models."""
    global mongodb_client
    
    # Create MongoDB client
    mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Get database
    database = mongodb_client[settings.MONGODB_DATABASE]
    
    # Import models here to avoid circular imports
    from app.models import Research, Message, Source, Note
    
    # Initialize Beanie with models
    await init_beanie(
        database=database,
        document_models=[
            Research,
            Message,
            Source,
            Note
        ]
    )
    
    print("✅ MongoDB database initialized successfully")
    print(f"✅ Connected to database: {settings.MONGODB_DATABASE}")
    print(f"✅ Models registered: Research, Message, Source, Note")
    return database


async def close_database():
    """Close database connections."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        mongodb_client = None
        print("✅ MongoDB connection closed")


# Health check function
async def check_database_health() -> bool:
    """Check if database is healthy."""
    try:
        client = await get_database_client()
        # Ping the server
        await client.admin.command('ping')
        return True
    except Exception:
        return False