"""
Qdrant Vector Database Manager
Enhanced Qdrant client and collection management for RAG system.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, 
    MatchValue, Range, CollectionInfo, UpdateResult, ScoredPoint,
    CreateCollection, UpdateCollection, OptimizersConfigDiff,
    HnswConfigDiff, QuantizationConfig, ScalarQuantization,
    ScalarType, ScalarQuantizationConfig
)
import asyncio
import uuid

from ..config.settings import settings

logger = logging.getLogger(__name__)


class QdrantManager:
    """Qdrant vector database manager with enhanced functionality."""
    
    def __init__(self):
        self.client: Optional[AsyncQdrantClient] = None
        self.sync_client: Optional[QdrantClient] = None
        self._is_initialized = False
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def initialize(self):
        """Initialize Qdrant client and ensure collection exists."""
        try:
            # Initialize async client
            self.client = AsyncQdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                timeout=30.0,
                grpc_port=6334,
                prefer_grpc=False
            )
            
            # Initialize sync client for some operations
            self.sync_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                timeout=30.0,
                prefer_grpc=False
            )
            
            # Test connection
            collections = await self.client.get_collections()
            logger.info(f"Connected to Qdrant with {len(collections.collections)} collections")
            
            # Ensure main collection exists
            await self._ensure_collection_exists()
            
            self._is_initialized = True
            logger.info("Qdrant manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {str(e)}")
            raise

    async def _ensure_collection_exists(self):
        """Ensure the main RAG collection exists with optimal configuration."""
        try:
            collections = await self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBED_DIMENSION,
                        distance=Distance.COSINE,
                        hnsw_config=HnswConfigDiff(
                            m=16,  # Number of bi-directional links for each node
                            ef_construct=200,  # Size of dynamic candidate list
                            full_scan_threshold=10000,  # Threshold for switching to full scan
                            max_indexing_threads=4,  # Number of parallel threads for indexing
                        )
                    ),
                    optimizers_config=OptimizersConfigDiff(
                        default_segment_number=2,
                        max_segment_size=20000,
                        memmap_threshold=50000,
                        indexing_threshold=20000,
                        flush_interval_sec=5,
                        max_optimization_threads=2
                    ),
                    # Enable quantization for better performance and storage
                    quantization_config=ScalarQuantization(
                        scalar=ScalarQuantizationConfig(
                            type=ScalarType.INT8,
                            quantile=0.99,
                            always_ram=True
                        )
                    )
                )
                
                logger.info(f"Created collection '{self.collection_name}' with optimized configuration")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
        
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check Qdrant health and return status."""
        try:
            # Get collections info
            collections = await self.client.get_collections()
            
            # Get collection info if it exists
            collection_info = None
            if self.collection_name in [col.name for col in collections.collections]:
                collection_info = await self.client.get_collection(self.collection_name)
            
            return {
                "status": "healthy",
                "total_collections": len(collections.collections),
                "main_collection": {
                    "name": self.collection_name,
                    "exists": collection_info is not None,
                    "points_count": collection_info.points_count if collection_info else 0,
                    "vectors_count": collection_info.vectors_count if collection_info else 0,
                    "segments_count": collection_info.segments_count if collection_info else 0,
                    "config": {
                        "vector_size": collection_info.config.params.vectors.size if collection_info else settings.EMBED_DIMENSION,
                        "distance": str(collection_info.config.params.vectors.distance) if collection_info else "cosine"
                    } if collection_info else None
                }
            }
            
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def upsert_points(
        self,
        points: List[PointStruct],
        batch_size: int = 100
    ) -> bool:
        """Upsert points in batches for better performance."""
        try:
            total_points = len(points)
            logger.info(f"Upserting {total_points} points to collection '{self.collection_name}'")
            
            # Process in batches
            for i in range(0, total_points, batch_size):
                batch = points[i:i + batch_size]
                
                result = await self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                    wait=True
                )
                
                logger.debug(f"Upserted batch {i//batch_size + 1}/{(total_points + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully upserted {total_points} points")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert points: {str(e)}")
            raise

    async def search_similar(
        self,
        query_vector: List[float],
        user_id: str,
        document_ids: Optional[List[str]] = None,
        limit: int = None,
        score_threshold: float = 0.0
    ) -> List[ScoredPoint]:
        """Search for similar vectors with user isolation and optional document filtering."""
        try:
            # Build filter for user isolation
            filter_conditions = [
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )
            ]
            
            # Add document filter if specified
            if document_ids:
                filter_conditions.append(
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_ids)
                    )
                )
            
            search_filter = Filter(must=filter_conditions)
            search_limit = limit or settings.SEARCH_TOP_K
            
            # Perform search
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=search_limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False  # Don't return vectors to save bandwidth
            )
            
            logger.debug(f"Found {len(results)} similar points for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar vectors: {str(e)}")
            raise

    async def delete_points_by_filter(
        self,
        user_id: str,
        document_id: str = None
    ) -> bool:
        """Delete points by filter (user and optionally document)."""
        try:
            # Build filter
            filter_conditions = [
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )
            ]
            
            if document_id:
                filter_conditions.append(
                    FieldCondition(
                        key="document_id", 
                        match=MatchValue(value=document_id)
                    )
                )
            
            delete_filter = Filter(must=filter_conditions)
            
            # Delete points
            result = await self.client.delete(
                collection_name=self.collection_name,
                points_selector=delete_filter,
                wait=True
            )
            
            operation_id = result.operation_id if hasattr(result, 'operation_id') else 'unknown'
            logger.info(f"Deleted points for user {user_id}" + 
                       (f", document {document_id}" if document_id else "") +
                       f" (operation_id: {operation_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete points: {str(e)}")
            raise

    async def get_collection_info(self) -> Optional[CollectionInfo]:
        """Get detailed collection information."""
        try:
            return await self.client.get_collection(self.collection_name)
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return None

    async def optimize_collection(self) -> bool:
        """Optimize the collection for better performance."""
        try:
            logger.info(f"Optimizing collection '{self.collection_name}'")
            
            # Update collection configuration for optimization
            await self.client.update_collection(
                collection_name=self.collection_name,
                optimizers_config=OptimizersConfigDiff(
                    indexing_threshold=10000,
                    max_optimization_threads=2
                )
            )
            
            logger.info("Collection optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize collection: {str(e)}")
            return False

    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a specific user's vectors."""
        try:
            # Count points for user
            # Note: Qdrant doesn't have a direct count with filter, so we use search with limit=0
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            )
            
            # Get a small sample to estimate count
            sample_results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=[0.0] * settings.EMBED_DIMENSION,  # Dummy vector
                query_filter=filter_condition,
                limit=1,
                with_payload=True
            )
            
            # Get documents for this user
            documents = set()
            chunk_types = {}
            
            # Use scroll to get more comprehensive stats
            scroll_results = await self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )
            
            points_count = len(scroll_results[0])
            
            for point in scroll_results[0]:
                payload = point.payload
                if payload.get("document_id"):
                    documents.add(payload["document_id"])
                
                chunk_type = payload.get("chunk_type", "unknown")
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            return {
                "user_id": user_id,
                "points_count": points_count,
                "unique_documents": len(documents),
                "chunk_types": chunk_types
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {str(e)}")
            return {"error": str(e)}

    async def backup_user_data(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Backup all vector data for a specific user."""
        try:
            logger.info(f"Backing up vector data for user {user_id}")
            
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            )
            
            # Scroll through all user's points
            all_points = []
            offset = None
            
            while True:
                results, next_offset = await self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=filter_condition,
                    limit=1000,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True
                )
                
                for point in results:
                    all_points.append({
                        "id": point.id,
                        "vector": point.vector,
                        "payload": point.payload
                    })
                
                if next_offset is None:
                    break
                    
                offset = next_offset
            
            logger.info(f"Backed up {len(all_points)} points for user {user_id}")
            return all_points
            
        except Exception as e:
            logger.error(f"Failed to backup user data: {str(e)}")
            return None

    async def close(self):
        """Close Qdrant connections."""
        try:
            if self.client:
                await self.client.close()
            if self.sync_client:
                self.sync_client.close()
            logger.info("Qdrant connections closed")
        except Exception as e:
            logger.warning(f"Error closing Qdrant connections: {str(e)}")

    @property
    def is_initialized(self) -> bool:
        """Check if the manager is initialized."""
        return self._is_initialized


# Global Qdrant manager instance
qdrant_manager = QdrantManager()