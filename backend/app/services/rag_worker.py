"""
RAG Background Worker
Handles asynchronous document processing tasks using Redis Queue.
"""

import os
import logging
from typing import Dict, Any, Optional
import asyncio

from rq import Worker, Queue, Connection
import redis
import structlog

from .rag_service import rag_service
from .document_processor import document_processor
from ..config.settings import settings

logger = structlog.get_logger(__name__)

# Redis connection for RQ
redis_conn = redis.from_url(settings.RQ_REDIS_URL)
task_queue = Queue('rag_tasks', connection=redis_conn)


def process_document_task(document_id: str, user_id: str, file_content: bytes, filename: str, file_type: str) -> Dict[str, Any]:
    """Background task to process a document for RAG."""
    try:
        logger.info(f"Starting document processing task for {document_id}")
        
        # Validate document
        validation = document_processor.validate_document(file_content, filename)
        if not validation["valid"]:
            logger.error(f"Document validation failed: {validation['errors']}")
            return {
                "success": False,
                "error": "Document validation failed",
                "details": validation["errors"]
            }
        
        # Process document and extract text
        extracted_content = document_processor.process_document(file_content, filename, file_type)
        
        # Create chunks
        chunks = document_processor.create_chunks(extracted_content["text_content"])
        
        if not chunks:
            logger.warning(f"No chunks created for document {document_id}")
            return {
                "success": False,
                "error": "No content could be extracted from document"
            }
        
        # Initialize RAG service if not already done
        if not rag_service._initialized:
            asyncio.run(rag_service.initialize())
        
        # Store chunks with embeddings
        asyncio.run(rag_service.store_document_chunks(document_id, chunks, user_id))
        
        # Upload to GCS if available
        gcs_path = None
        if rag_service.gcs_client:
            try:
                gcs_path = asyncio.run(rag_service.upload_to_gcs(file_content, user_id, document_id, filename))
            except Exception as e:
                logger.warning(f"Failed to upload to GCS: {str(e)}")
        
        result = {
            "success": True,
            "document_id": document_id,
            "chunks_created": len(chunks),
            "total_pages": extracted_content["metadata"].get("total_pages", 1),
            "gcs_path": gcs_path,
            "processing_metadata": extracted_content["metadata"]
        }
        
        logger.info(f"Document processing completed for {document_id}: {len(chunks)} chunks created")
        return result
        
    except Exception as e:
        logger.error(f"Document processing failed for {document_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "document_id": document_id
        }


def delete_document_task(document_id: str) -> Dict[str, Any]:
    """Background task to delete document from RAG."""
    try:
        logger.info(f"Starting document deletion task for {document_id}")
        
        # Initialize RAG service if not already done
        if not rag_service._initialized:
            asyncio.run(rag_service.initialize())
        
        # Delete chunks from Qdrant
        success = asyncio.run(rag_service.delete_document_chunks(document_id))
        
        if success:
            logger.info(f"Document deletion completed for {document_id}")
            return {
                "success": True,
                "document_id": document_id,
                "message": "Document chunks deleted successfully"
            }
        else:
            return {
                "success": False,
                "document_id": document_id,
                "error": "Failed to delete document chunks"
            }
            
    except Exception as e:
        logger.error(f"Document deletion failed for {document_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "document_id": document_id
        }


class RAGWorkerService:
    """Service to manage RAG background workers."""
    
    def __init__(self):
        self.redis_conn = redis_conn
        self.queue = task_queue
    
    def enqueue_document_processing(
        self,
        document_id: str,
        user_id: str,
        file_content: bytes,
        filename: str,
        file_type: str,
        job_timeout: Optional[int] = None
    ) -> str:
        """Enqueue document processing task."""
        try:
            job = self.queue.enqueue(
                process_document_task,
                document_id,
                user_id,
                file_content,
                filename,
                file_type,
                job_timeout=job_timeout or settings.TASK_TIMEOUT,
                retry=settings.RETRY_ATTEMPTS
            )
            
            logger.info(f"Enqueued document processing job {job.id} for document {document_id}")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to enqueue document processing: {str(e)}")
            raise
    
    def enqueue_document_deletion(self, document_id: str) -> str:
        """Enqueue document deletion task."""
        try:
            job = self.queue.enqueue(
                delete_document_task,
                document_id,
                job_timeout=300,  # 5 minutes for deletion
                retry=settings.RETRY_ATTEMPTS
            )
            
            logger.info(f"Enqueued document deletion job {job.id} for document {document_id}")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to enqueue document deletion: {str(e)}")
            raise
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a background job."""
        try:
            from rq import job
            rq_job = job.Job.fetch(job_id, connection=self.redis_conn)
            
            return {
                "job_id": job_id,
                "status": rq_job.get_status(),
                "result": rq_job.result,
                "created_at": rq_job.created_at.isoformat() if rq_job.created_at else None,
                "started_at": rq_job.started_at.isoformat() if rq_job.started_at else None,
                "ended_at": rq_job.ended_at.isoformat() if rq_job.ended_at else None,
                "exc_info": rq_job.exc_info
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {str(e)}")
            return {
                "job_id": job_id,
                "status": "unknown",
                "error": str(e)
            }
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get information about the task queue."""
        try:
            return {
                "queue_name": self.queue.name,
                "jobs_queued": len(self.queue),
                "jobs_started": len(self.queue.started_job_registry),
                "jobs_finished": len(self.queue.finished_job_registry),
                "jobs_failed": len(self.queue.failed_job_registry)
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue info: {str(e)}")
            return {"error": str(e)}
    
    def start_worker(self):
        """Start RQ worker process."""
        try:
            logger.info("Starting RAG worker process")
            
            worker = Worker(
                [self.queue],
                connection=self.redis_conn,
                name=f"rag-worker-{os.getpid()}"
            )
            
            # Start worker (this blocks)
            worker.work()
            
        except Exception as e:
            logger.error(f"Worker failed: {str(e)}")
            raise


# Global worker service instance
rag_worker = RAGWorkerService()


if __name__ == "__main__":
    # Start worker when run directly
    rag_worker.start_worker()