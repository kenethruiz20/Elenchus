"""
RAG (Retrieval Augmented Generation) Service
Handles document processing, embedding generation, and vector search.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from google.cloud import storage
import structlog

from ..config.settings import settings

logger = structlog.get_logger(__name__)


class RAGService:
    """Main RAG service for document processing and retrieval."""
    
    def __init__(self):
        self.qdrant_client = None
        self.embedding_model = None
        self.gcs_client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize RAG service connections and models."""
        try:
            # Initialize Qdrant client
            self.qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
            )
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {settings.EMBED_MODEL}")
            self.embedding_model = SentenceTransformer(settings.EMBED_MODEL)
            
            # Initialize GCS client
            if os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                self.gcs_client = storage.Client.from_service_account_json(
                    settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                logger.warning("GCS credentials not found, file storage disabled")
            
            # Ensure Qdrant collection exists
            await self._ensure_collection()
            
            self._initialized = True
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            raise
    
    async def _ensure_collection(self):
        """Ensure Qdrant collection exists with proper configuration."""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if settings.QDRANT_COLLECTION_NAME not in collection_names:
                logger.info(f"Creating Qdrant collection: {settings.QDRANT_COLLECTION_NAME}")
                
                self.qdrant_client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=settings.EMBED_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                logger.info("Qdrant collection created successfully")
            else:
                logger.info("Qdrant collection already exists")
                
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            embeddings = self.embedding_model.encode(
                texts,
                batch_size=settings.EMBEDDING_BATCH_SIZE,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    async def store_document_chunks(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        user_id: str
    ) -> bool:
        """Store document chunks with embeddings in Qdrant."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            points = []
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings for all chunks
            embeddings = self.generate_embeddings(texts)
            
            # Create Qdrant points
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = PointStruct(
                    id=f"{document_id}_{i}",
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "user_id": user_id,
                        "chunk_index": i,
                        "text": chunk["text"],
                        "text_hash": chunk.get("text_hash", ""),
                        "page": chunk.get("page", None),
                        "section": chunk.get("section", None),
                        "metadata": chunk.get("metadata", {})
                    }
                )
                points.append(point)
            
            # Insert points into Qdrant
            self.qdrant_client.upsert(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points=points
            )
            
            logger.info(f"Stored {len(points)} chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store document chunks: {str(e)}")
            raise
    
    async def search_similar_chunks(
        self,
        query: str,
        user_id: str,
        document_ids: Optional[List[str]] = None,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Build filter for user isolation
            filter_conditions = [
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
            
            # Add document filter if specified
            if document_ids:
                filter_conditions.append(
                    FieldCondition(key="document_id", match=MatchValue(value=document_ids))
                )
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Perform search
            search_result = self.qdrant_client.search(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=top_k or settings.SEARCH_TOP_K
            )
            
            # Format results
            results = []
            for scored_point in search_result:
                result = {
                    "chunk_id": scored_point.id,
                    "score": scored_point.score,
                    "text": scored_point.payload["text"],
                    "document_id": scored_point.payload["document_id"],
                    "chunk_index": scored_point.payload["chunk_index"],
                    "page": scored_point.payload.get("page"),
                    "section": scored_point.payload.get("section"),
                    "metadata": scored_point.payload.get("metadata", {})
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} similar chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {str(e)}")
            raise
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a specific document."""
        if not self._initialized:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # Delete points by document_id filter
            delete_filter = Filter(
                must=[
                    FieldCondition(key="document_id", match=MatchValue(value=document_id))
                ]
            )
            
            self.qdrant_client.delete(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points_selector=delete_filter
            )
            
            logger.info(f"Deleted chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document chunks: {str(e)}")
            raise
    
    async def upload_to_gcs(self, file_content: bytes, user_id: str, file_id: str, filename: str) -> str:
        """Upload file to Google Cloud Storage with structured path."""
        if not self.gcs_client:
            raise RuntimeError("GCS client not initialized")
        
        try:
            # Construct structured path: user_docs/user_id/file_id/filename
            file_path = f"{settings.GCP_BUCKET_BASE_PATH}/{user_id}/{file_id}/{filename}"
            
            bucket = self.gcs_client.bucket(settings.GCP_BUCKET)
            blob = bucket.blob(file_path)
            
            blob.upload_from_string(file_content)
            
            logger.info(f"Uploaded file to GCS: {file_path}")
            return f"gs://{settings.GCP_BUCKET}/{file_path}"
            
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {str(e)}")
            raise
    
    async def download_from_gcs(self, file_path: str) -> bytes:
        """Download file from Google Cloud Storage."""
        if not self.gcs_client:
            raise RuntimeError("GCS client not initialized")
        
        try:
            bucket = self.gcs_client.bucket(settings.GCP_BUCKET)
            blob = bucket.blob(file_path)
            
            content = blob.download_as_bytes()
            
            logger.info(f"Downloaded file from GCS: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to download from GCS: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of RAG service components."""
        health = {
            "initialized": self._initialized,
            "components": {}
        }
        
        # Check Qdrant
        try:
            if self.qdrant_client:
                collections = self.qdrant_client.get_collections()
                health["components"]["qdrant"] = "healthy"
            else:
                health["components"]["qdrant"] = "not_initialized"
        except Exception as e:
            health["components"]["qdrant"] = f"error: {str(e)}"
        
        # Check embedding model
        try:
            if self.embedding_model:
                test_embedding = self.embedding_model.encode(["test"])
                health["components"]["embeddings"] = "healthy"
            else:
                health["components"]["embeddings"] = "not_initialized"
        except Exception as e:
            health["components"]["embeddings"] = f"error: {str(e)}"
        
        # Check GCS
        try:
            if self.gcs_client:
                bucket = self.gcs_client.bucket(settings.GCP_BUCKET)
                bucket.exists()  # Test connection
                health["components"]["gcs"] = "healthy"
            else:
                health["components"]["gcs"] = "not_initialized"
        except Exception as e:
            health["components"]["gcs"] = f"error: {str(e)}"
        
        return health


# Global RAG service instance
rag_service = RAGService()