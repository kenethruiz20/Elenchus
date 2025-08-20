"""
RAG Document Upload Service
Handles document upload, storage, and registration without ML dependencies.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import UploadFile, BackgroundTasks

from app.models.rag_document import RAGDocument, DocumentStatus, DocumentType, DocumentMetadata
from app.models.rag_chunk import RAGChunk, ChunkType, ChunkMetadata
from app.services.document_processor import document_processor
from app.services.gcp_service import gcp_service
from app.services.content_extractor import content_extractor
from app.services.document_ai_service import document_ai_service
from app.database import mongodb_manager

logger = logging.getLogger(__name__)


class RAGUploadService:
    """Service for handling RAG document uploads and registration."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize the upload service."""
        try:
            # Ensure database and GCP are ready
            if not mongodb_manager.is_initialized:
                raise Exception("MongoDB not initialized")
            
            # GCP is optional for development
            if gcp_service.is_initialized():
                logger.info("RAG Upload Service initialized with GCP storage")
            else:
                logger.warning("RAG Upload Service initialized without GCP storage")
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG upload service: {str(e)}")
            return False
    
    async def upload_document(
        self,
        user_id: str,
        file: UploadFile,
        tags: List[str] = None,
        category: str = None,
        background_tasks: BackgroundTasks = None
    ) -> RAGDocument:
        """
        Upload and register a document for RAG processing.
        
        Args:
            user_id: User ID who owns the document
            file: Uploaded file
            tags: Optional list of tags
            category: Optional category
            background_tasks: Background tasks for processing
            
        Returns:
            RAGDocument instance
        """
        if not self.initialized:
            raise Exception("RAG upload service not initialized")
        
        try:
            # Read file content
            file_content = await file.read()
            original_filename = file.filename or "unknown"
            
            # Generate file hash for deduplication
            file_hash = document_processor.generate_document_hash(file_content)
            
            # Check for duplicate based on hash
            existing_doc = await RAGDocument.find_one(
                RAGDocument.file_hash == file_hash,
                RAGDocument.user_id == user_id
            )
            
            if existing_doc:
                logger.info(f"Document with hash {file_hash} already exists for user {user_id}")
                return existing_doc
            
            # Validate document
            validation = document_processor.validate_document(file_content, original_filename)
            if not validation['valid']:
                raise ValueError(f"Document validation failed: {', '.join(validation['errors'])}")
            
            # Extract basic metadata
            file_metadata = document_processor.extract_document_metadata(file_content, original_filename)
            
            # Determine document type
            document_type = self._get_document_type(original_filename)
            
            # Create document metadata
            metadata = DocumentMetadata(
                title=file_metadata.get('title', Path(original_filename).stem),
                author=file_metadata.get('author'),
                page_count=file_metadata.get('total_pages', 0),
                word_count=file_metadata.get('total_words', 0),
                char_count=file_metadata.get('total_chars', 0),
                # language='en',  # Commented out to avoid MongoDB text index conflict
                creation_date=datetime.utcnow()
            )
            
            # Generate a temporary file ID for GCS (before document creation)
            temp_file_id = str(uuid.uuid4())
            
            # Upload to GCS if available
            gcs_path = None
            if gcp_service.is_initialized():
                # Determine correct content type based on file extension
                content_type = self._get_content_type(original_filename)
                
                upload_result = await gcp_service.upload_file(
                    user_id=user_id,
                    file_id=temp_file_id,
                    filename=original_filename,
                    file_content=file_content,
                    content_type=content_type
                )
                
                if upload_result['success']:
                    gcs_path = upload_result['gcs_path']
                    logger.info(f"File uploaded to GCS: {gcs_path}")
                else:
                    logger.error(f"GCS upload failed: {upload_result.get('error')}")
                    # Continue without GCS for development
            
            # Create RAG document record
            rag_document = RAGDocument(
                user_id=user_id,
                filename=f"{temp_file_id}_{original_filename}",
                original_filename=original_filename,
                file_type=document_type,
                file_size=len(file_content),
                file_hash=file_hash,
                gcs_path=gcs_path,
                status=DocumentStatus.PENDING,
                metadata=metadata,
                tags=tags or [],
                category=category,
                embeddings_created=False,
                chunks_count=0
            )
            
            # Save to database
            await rag_document.insert()
            logger.info(f"Document registered: {rag_document.id} for user {user_id}")
            
            # Schedule background processing if available
            if background_tasks:
                background_tasks.add_task(
                    self._process_document_background,
                    str(rag_document.id),
                    file_content,
                    user_id
                )
                logger.info(f"Scheduled background processing for document {rag_document.id}")
            
            return rag_document
            
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}")
            raise
    
    def _get_document_type(self, filename: str) -> DocumentType:
        """Determine document type from filename."""
        from pathlib import Path
        
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            return DocumentType.PDF
        elif file_ext in ['.doc', '.docx']:
            return DocumentType.DOCX
        elif file_ext == '.txt':
            return DocumentType.TXT
        elif file_ext == '.md':
            return DocumentType.MARKDOWN
        elif file_ext == '.csv':
            return DocumentType.CSV
        else:
            return DocumentType.TXT  # Default fallback
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename."""
        from pathlib import Path
        
        file_ext = Path(filename).suffix.lower()
        
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.rtf': 'application/rtf',
            '.odt': 'application/vnd.oasis.opendocument.text'
        }
        
        return content_types.get(file_ext, 'application/octet-stream')
    
    async def _process_document_background(self, document_id: str, file_content: bytes, user_id: str):
        """Background task to process document content."""
        try:
            from beanie import PydanticObjectId
            
            # Convert document_id to ObjectId if needed
            try:
                obj_id = PydanticObjectId(document_id)
            except:
                obj_id = document_id
            
            # Find the document
            document = await RAGDocument.find_one(RAGDocument.id == obj_id)
            if not document:
                logger.error(f"Document {document_id} not found for processing")
                return
            
            # Mark as processing
            await document.mark_processing_started(f"job_{uuid.uuid4()}")
            logger.info(f"Started processing document {document_id}")
            
            # Extract content for AI analysis
            ai_metadata = {}
            if content_extractor.can_extract(document.original_filename):
                logger.info(f"Extracting content for AI analysis: {document.original_filename}")
                extraction_result = await content_extractor.extract_content(
                    file_content, 
                    document.original_filename
                )
                
                if extraction_result['success'] and extraction_result['text_content']:
                    # Initialize AI service if not already done
                    if not document_ai_service.is_initialized():
                        await document_ai_service.initialize()
                    
                    if document_ai_service.is_initialized():
                        # Generate AI metadata
                        logger.info(f"Generating AI metadata for {document.original_filename}")
                        ai_result = await document_ai_service.generate_document_metadata(
                            extraction_result['text_content'],
                            document.original_filename,
                            document.file_type.value
                        )
                        
                        if ai_result['success']:
                            ai_metadata = {
                                'ai_summary': ai_result['ai_summary'],
                                'ai_detailed_description': ai_result['ai_detailed_description'],
                                'ai_topics': ai_result['ai_topics'],
                                'ai_metadata_generated_at': datetime.utcnow()
                            }
                            logger.info(f"AI metadata generated successfully for {document_id}")
                        else:
                            logger.warning(f"AI metadata generation failed: {ai_result.get('error')}")
                    else:
                        logger.warning("Document AI service not available")
                else:
                    logger.warning(f"Content extraction failed: {extraction_result.get('error')}")
            else:
                logger.info(f"File format not supported for content extraction: {document.original_filename}")
            
            # Process document with document_processor
            processing_result = await document_processor.process_document_async(
                file_content,
                document.original_filename,
                user_id
            )
            
            if not processing_result['success']:
                # Mark as failed
                await document.mark_processing_failed(processing_result.get('error', 'Unknown error'))
                logger.error(f"Document processing failed for {document_id}: {processing_result.get('error')}")
                return
            
            # Create chunks in database
            chunks_created = 0
            for chunk_idx, chunk_data in enumerate(processing_result['chunks']):
                chunk = RAGChunk(
                    document_id=str(document.id),
                    user_id=user_id,
                    chunk_index=chunk_idx,
                    chunk_id=f"{document_id}_{chunk_idx}",
                    text=chunk_data['text'],
                    text_hash=chunk_data['text_hash'],
                    chunk_type=ChunkType.TEXT,
                    metadata=ChunkMetadata(
                        page_number=chunk_data.get('page', 1),
                        word_count=chunk_data.get('word_count', 0),
                        char_count=chunk_data.get('char_count', 0),
                        sentence_count=chunk_data.get('sentence_count', 0)
                    )
                )
                
                # Calculate quality metrics
                chunk.calculate_quality_metrics()
                await chunk.insert()
                chunks_created += 1
            
            # Update document with AI metadata if available
            if ai_metadata:
                logger.info(f"Updating document {document_id} with AI metadata")
                for key, value in ai_metadata.items():
                    setattr(document.metadata, key, value)
                await document.save()
            
            # Mark as completed (without embeddings for now)
            from app.models.rag_document import ProcessingMetrics
            metrics = ProcessingMetrics(
                chunks_created=chunks_created,
                processing_time_seconds=0.0,  # We're not timing this for now
                embedding_time_seconds=0.0
            )
            
            await document.mark_processing_completed(chunks_created, metrics)
            logger.info(f"Document {document_id} processing completed: {chunks_created} chunks created")
            
        except Exception as e:
            import traceback
            error_msg = f"Background processing failed for document {document_id}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            # Try to mark as failed if document still exists
            try:
                from beanie import PydanticObjectId
                try:
                    obj_id = PydanticObjectId(document_id)
                except:
                    obj_id = document_id
                    
                document = await RAGDocument.find_one(RAGDocument.id == obj_id)
                if document:
                    await document.mark_processing_failed(str(e))
            except Exception as inner_e:
                logger.error(f"Failed to mark document as failed: {str(inner_e)}")
    
    async def get_document_status(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Get processing status of a document."""
        try:
            from beanie import PydanticObjectId
            
            # Convert document_id to ObjectId if needed
            try:
                obj_id = PydanticObjectId(document_id)
            except:
                obj_id = document_id
            
            # Find document and verify ownership
            document = await RAGDocument.find_one(
                RAGDocument.id == obj_id,
                RAGDocument.user_id == user_id
            )
            
            if not document:
                return {
                    'found': False,
                    'error': 'Document not found'
                }
            
            # Calculate progress
            progress = 0.0
            if document.status == DocumentStatus.PROCESSING:
                progress = 0.5
            elif document.status == DocumentStatus.COMPLETED:
                progress = 1.0
            elif document.status == DocumentStatus.FAILED:
                progress = 0.0
            
            return {
                'found': True,
                'document_id': str(document.id),
                'status': document.status,
                'progress': progress,
                'chunks_count': document.chunks_count,
                'embeddings_created': document.embeddings_created,
                'processing_error': getattr(document, 'processing_error', None),
                'created_at': document.created_at,
                'updated_at': document.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get document status: {str(e)}")
            return {
                'found': False,
                'error': str(e)
            }
    
    async def list_user_documents(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: DocumentStatus = None
    ) -> Dict[str, Any]:
        """List documents for a user."""
        try:
            # Build query
            query = RAGDocument.user_id == user_id
            if status:
                query = query & (RAGDocument.status == status)
            
            # Get documents
            documents = await RAGDocument.find(query).sort([
                ("created_at", -1)
            ]).skip(offset).limit(limit).to_list()
            
            # Count total
            total_count = await RAGDocument.find(query).count()
            
            # Convert to response format
            document_list = []
            for doc in documents:
                document_list.append({
                    'id': str(doc.id),
                    'filename': doc.original_filename,
                    'file_type': doc.file_type,
                    'file_size': doc.file_size,
                    'status': doc.status,
                    'chunks_count': doc.chunks_count,
                    'embeddings_created': doc.embeddings_created,
                    'created_at': doc.created_at,
                    'updated_at': doc.updated_at,
                    'tags': doc.tags,
                    'category': doc.category,
                    # AI-generated metadata
                    'ai_summary': doc.metadata.ai_summary,
                    'ai_detailed_description': doc.metadata.ai_detailed_description,
                    'ai_topics': doc.metadata.ai_topics,
                    'ai_metadata_generated_at': doc.metadata.ai_metadata_generated_at,
                    'can_download': doc.gcs_path is not None
                })
            
            return {
                'success': True,
                'documents': document_list,
                'total_count': total_count,
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            logger.error(f"Failed to list user documents: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'documents': []
            }
    
    async def delete_document(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a document and all its associated data."""
        try:
            from beanie import PydanticObjectId
            
            # Convert document_id to ObjectId if needed
            try:
                obj_id = PydanticObjectId(document_id)
            except:
                obj_id = document_id
            
            # Find document and verify ownership
            document = await RAGDocument.find_one(
                RAGDocument.id == obj_id,
                RAGDocument.user_id == user_id
            )
            
            if not document:
                return {
                    'success': False,
                    'error': 'Document not found'
                }
            
            # Delete associated chunks
            deleted_chunks = await RAGChunk.find(
                RAGChunk.document_id == document_id,
                RAGChunk.user_id == user_id
            ).delete()
            
            logger.info(f"Deleted {deleted_chunks.deleted_count} chunks for document {document_id}")
            
            # Delete from GCS if exists
            if document.gcs_path and gcp_service.is_initialized():
                try:
                    # Extract file_id from filename (format: {file_id}_{original_filename})
                    filename_parts = document.filename.split('_', 1)
                    file_id = filename_parts[0] if len(filename_parts) > 1 else str(document.id)
                    
                    delete_result = await gcp_service.delete_file(
                        user_id=user_id,
                        file_id=file_id,
                        filename=document.original_filename
                    )
                    if delete_result['success']:
                        logger.info(f"Deleted file from GCS: {document.gcs_path}")
                    else:
                        logger.warning(f"GCS deletion failed: {delete_result.get('error')}")
                except Exception as e:
                    logger.warning(f"GCS deletion error: {str(e)}")
            
            # Delete document
            await document.delete()
            
            return {
                'success': True,
                'deleted_document_id': document_id,
                'deleted_chunks': deleted_chunks.deleted_count
            }
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user's document statistics."""
        try:
            # Get document counts by status
            total_docs = await RAGDocument.find(RAGDocument.user_id == user_id).count()
            completed_docs = await RAGDocument.find(
                RAGDocument.user_id == user_id,
                RAGDocument.status == DocumentStatus.COMPLETED
            ).count()
            processing_docs = await RAGDocument.find(
                RAGDocument.user_id == user_id,
                RAGDocument.status == DocumentStatus.PROCESSING
            ).count()
            failed_docs = await RAGDocument.find(
                RAGDocument.user_id == user_id,
                RAGDocument.status == DocumentStatus.FAILED
            ).count()
            
            # Get total chunks
            total_chunks = await RAGChunk.find(RAGChunk.user_id == user_id).count()
            
            # Get storage usage from database
            storage_stats = await mongodb_manager.get_user_storage_stats(user_id)
            
            return {
                'user_id': user_id,
                'total_documents': total_docs,
                'documents_by_status': {
                    'completed': completed_docs,
                    'processing': processing_docs,
                    'failed': failed_docs,
                    'pending': total_docs - completed_docs - processing_docs - failed_docs
                },
                'total_chunks': total_chunks,
                'total_file_size': storage_stats.get('documents', {}).get('total_file_size', 0),
                'storage_used_mb': storage_stats.get('documents', {}).get('total_file_size', 0) / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {str(e)}")
            return {
                'error': str(e)
            }


# Global upload service instance
rag_upload_service = RAGUploadService()