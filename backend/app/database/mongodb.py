"""
MongoDB Database Utilities
Enhanced database connection and utilities for RAG system.
"""

import logging
from typing import Optional, List, Any, Dict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
import pymongo

from ..config.settings import settings
from ..models.user import User
from ..models.research import Research
from ..models.message import Message
from ..models.note import Note
from ..models.source import Source
from ..models.rag_document import RAGDocument
from ..models.rag_chunk import RAGChunk
from ..models.rag_session import RAGSession

logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB connection and utilities manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._is_initialized = False

    async def initialize(self):
        """Initialize MongoDB connection and Beanie ODM."""
        try:
            # Create MongoDB client
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
            )
            
            # Get database
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {settings.MONGODB_DATABASE}")
            
            # Initialize Beanie with all document models
            await init_beanie(
                database=self.database,
                document_models=[
                    # Existing models
                    User,
                    Research,
                    Message,
                    Note,
                    Source,
                    # RAG models
                    RAGDocument,
                    RAGChunk,
                    RAGSession,
                ]
            )
            
            logger.info("Beanie ODM initialized successfully")
            
            # Create additional indexes
            await self._create_additional_indexes()
            
            self._is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {str(e)}")
            raise

    async def _create_additional_indexes(self):
        """Create additional indexes for performance optimization."""
        try:
            # RAG Documents additional indexes
            rag_docs_collection = self.database.rag_documents
            
            # Compound indexes for common queries
            await rag_docs_collection.create_index([
                ("user_id", pymongo.ASCENDING),
                ("file_type", pymongo.ASCENDING),
                ("status", pymongo.ASCENDING)
            ], background=True)
            
            await rag_docs_collection.create_index([
                ("user_id", pymongo.ASCENDING),
                ("embeddings_created", pymongo.ASCENDING),
                ("created_at", pymongo.DESCENDING)
            ], background=True)
            
            # TTL index for failed documents (cleanup after 7 days)
            await rag_docs_collection.create_index(
                [("updated_at", pymongo.ASCENDING)],
                expireAfterSeconds=7 * 24 * 60 * 60,  # 7 days
                partialFilterExpression={"status": "failed"},
                background=True
            )
            
            # RAG Chunks additional indexes
            rag_chunks_collection = self.database.rag_chunks
            
            await rag_chunks_collection.create_index([
                ("user_id", pymongo.ASCENDING),
                ("qdrant_point_id", pymongo.ASCENDING)
            ], background=True)
            
            await rag_chunks_collection.create_index([
                ("document_id", pymongo.ASCENDING),
                ("metadata.page_number", pymongo.ASCENDING),
                ("chunk_index", pymongo.ASCENDING)
            ], background=True)
            
            # RAG Sessions additional indexes
            rag_sessions_collection = self.database.rag_sessions
            
            await rag_sessions_collection.create_index([
                ("user_id", pymongo.ASCENDING),
                ("is_favorite", pymongo.ASCENDING),
                ("last_activity", pymongo.DESCENDING)
            ], background=True)
            
            await rag_sessions_collection.create_index([
                ("shared_with", pymongo.ASCENDING),
                ("is_shared", pymongo.ASCENDING)
            ], background=True)
            
            logger.info("Additional indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Some indexes may already exist: {str(e)}")

    async def ping(self) -> bool:
        """Test database connection."""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {str(e)}")
            return False

    async def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            stats = await self.database.command("dbStats")
            
            # Get collection counts
            collections_stats = {}
            for collection_name in ["rag_documents", "rag_chunks", "rag_sessions", "users", "research_sessions"]:
                try:
                    count = await self.database[collection_name].count_documents({})
                    collections_stats[collection_name] = count
                except Exception as e:
                    logger.warning(f"Could not get count for {collection_name}: {e}")
                    collections_stats[collection_name] = 0
            
            return {
                "database_name": stats.get("db"),
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "index_size": stats.get("indexSize", 0),
                "documents": collections_stats,
                "ok": stats.get("ok", 0) == 1
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {"error": str(e)}

    async def create_user_data_indexes(self, user_id: str):
        """Create user-specific indexes for better performance."""
        try:
            # Create indexes for specific user's data
            await self.database.rag_documents.create_index([
                ("user_id", pymongo.ASCENDING)
            ], 
            partialFilterExpression={"user_id": user_id},
            background=True)
            
            await self.database.rag_chunks.create_index([
                ("user_id", pymongo.ASCENDING)
            ],
            partialFilterExpression={"user_id": user_id}, 
            background=True)
            
            logger.info(f"User-specific indexes created for user: {user_id}")
            
        except Exception as e:
            logger.warning(f"Failed to create user indexes: {str(e)}")

    async def cleanup_orphaned_chunks(self, user_id: str = None) -> int:
        """Clean up chunks that don't have corresponding documents."""
        try:
            # Find all chunk document_ids
            pipeline = [
                {"$group": {"_id": "$document_id"}},
                {"$project": {"document_id": "$_id", "_id": 0}}
            ]
            
            if user_id:
                pipeline.insert(0, {"$match": {"user_id": user_id}})
            
            chunk_doc_ids = set()
            async for doc in self.database.rag_chunks.aggregate(pipeline):
                chunk_doc_ids.add(doc["document_id"])
            
            # Find existing documents
            existing_doc_ids = set()
            query = {} if not user_id else {"user_id": user_id}
            async for doc in self.database.rag_documents.find(query, {"_id": 1}):
                existing_doc_ids.add(str(doc["_id"]))
            
            # Find orphaned chunk document_ids
            orphaned_doc_ids = chunk_doc_ids - existing_doc_ids
            
            if orphaned_doc_ids:
                # Delete orphaned chunks
                delete_query = {"document_id": {"$in": list(orphaned_doc_ids)}}
                if user_id:
                    delete_query["user_id"] = user_id
                
                result = await self.database.rag_chunks.delete_many(delete_query)
                
                logger.info(f"Cleaned up {result.deleted_count} orphaned chunks")
                return result.deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned chunks: {str(e)}")
            return 0

    async def get_user_storage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get storage statistics for a specific user."""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_documents": {"$sum": 1},
                    "total_file_size": {"$sum": "$file_size"},
                    "documents_by_type": {"$push": "$file_type"},
                    "documents_by_status": {"$push": "$status"}
                }}
            ]
            
            docs_stats = {}
            async for result in self.database.rag_documents.aggregate(pipeline):
                docs_stats = result
                break
            
            # Count chunks
            chunks_count = await self.database.rag_chunks.count_documents({"user_id": user_id})
            
            # Count sessions
            sessions_count = await self.database.rag_sessions.count_documents({"user_id": user_id})
            
            return {
                "user_id": user_id,
                "documents": {
                    "total_count": docs_stats.get("total_documents", 0),
                    "total_file_size": docs_stats.get("total_file_size", 0),
                    "by_type": self._count_by_field(docs_stats.get("documents_by_type", [])),
                    "by_status": self._count_by_field(docs_stats.get("documents_by_status", []))
                },
                "chunks": {
                    "total_count": chunks_count
                },
                "sessions": {
                    "total_count": sessions_count
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user storage stats: {str(e)}")
            return {"error": str(e)}

    def _count_by_field(self, field_values: List[str]) -> Dict[str, int]:
        """Count occurrences of field values."""
        counts = {}
        for value in field_values:
            counts[value] = counts.get(value, 0) + 1
        return counts

    @property
    def is_initialized(self) -> bool:
        """Check if the manager is initialized."""
        return self._is_initialized


# Global MongoDB manager instance
mongodb_manager = MongoDBManager()