"""
Google Cloud Platform Authentication and Storage Service
Handles GCP authentication and Google Cloud Storage operations.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import GoogleAPIError
import tempfile

from app.config.settings import settings

logger = logging.getLogger(__name__)


class GCPService:
    """Service for Google Cloud Platform operations."""
    
    def __init__(self):
        self.project_id = getattr(settings, 'GCP_PROJECT', None)
        self.bucket_name = getattr(settings, 'GCP_BUCKET', None)
        self.base_path = getattr(settings, 'GCP_BUCKET_BASE_PATH', 'user_docs')
        self.credentials_path = getattr(settings, 'GCP_CREDENTIALS_PATH', None)
        self.credentials_json = getattr(settings, 'GCP_CREDENTIALS_JSON', None)
        
        self._storage_client = None
        self._bucket = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize GCP client with authentication."""
        try:
            # Set credentials if provided
            if self.credentials_json:
                # Use JSON credentials from environment
                credentials_dict = json.loads(self.credentials_json)
                # Write to temporary file for google-cloud-storage
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(credentials_dict, f)
                    temp_creds_path = f.name
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_creds_path
                logger.info("Using GCP credentials from environment variable")
            
            elif self.credentials_path and os.path.exists(self.credentials_path):
                # Use credentials file
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
                logger.info(f"Using GCP credentials from file: {self.credentials_path}")
            
            else:
                # Try to use default credentials (ADC)
                logger.info("Using default GCP credentials (Application Default Credentials)")
            
            # Initialize storage client
            self._storage_client = storage.Client(project=self.project_id)
            
            # Get bucket
            if self.bucket_name:
                self._bucket = self._storage_client.bucket(self.bucket_name)
                # Test bucket access
                if not self._bucket.exists():
                    logger.error(f"GCP bucket '{self.bucket_name}' does not exist")
                    return False
                logger.info(f"Connected to GCP bucket: {self.bucket_name}")
            else:
                logger.warning("No GCP bucket configured")
                return False
            
            self._initialized = True
            return True
            
        except DefaultCredentialsError as e:
            logger.error(f"GCP credentials not found: {str(e)}")
            logger.error("Please set up GCP credentials using one of these methods:")
            logger.error("1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
            logger.error("2. Use 'gcloud auth application-default login'")
            logger.error("3. Provide GCP_CREDENTIALS_JSON in settings")
            return False
        
        except Exception as e:
            logger.error(f"Failed to initialize GCP service: {str(e)}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if GCP service is properly initialized."""
        return self._initialized and self._storage_client is not None and self._bucket is not None
    
    def _get_blob_path(self, user_id: str, file_id: str, filename: str) -> str:
        """Generate blob path for file storage."""
        return f"{self.base_path}/{user_id}/{file_id}/{filename}"
    
    async def upload_file(
        self, 
        user_id: str, 
        file_id: str, 
        filename: str, 
        file_content: bytes,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Google Cloud Storage.
        
        Args:
            user_id: User identifier for multi-tenant storage
            file_id: Unique file identifier 
            filename: Original filename
            file_content: File content as bytes
            content_type: MIME type of the file
        
        Returns:
            Dict with upload result information
        """
        if not self.is_initialized():
            raise Exception("GCP service not initialized")
        
        try:
            # Generate blob path
            blob_path = self._get_blob_path(user_id, file_id, filename)
            blob = self._bucket.blob(blob_path)
            
            # Add metadata
            blob.metadata = {
                'user_id': user_id,
                'file_id': file_id,
                'original_filename': filename,
                'upload_timestamp': datetime.utcnow().isoformat(),
                'uploaded_by': 'rag_system'
            }
            
            # Upload file with explicit content type
            blob.upload_from_string(
                file_content,
                content_type=content_type if content_type else 'application/octet-stream'
            )
            
            logger.info(f"Successfully uploaded file to GCS: {blob_path}")
            
            return {
                'success': True,
                'gcs_path': blob_path,
                'blob_name': blob.name,
                'size': len(file_content),
                'content_type': content_type if content_type else 'application/octet-stream',
                'upload_time': datetime.utcnow(),
                'public_url': None  # We don't make files public by default
            }
            
        except GoogleAPIError as e:
            logger.error(f"GCS upload failed: {str(e)}")
            return {
                'success': False,
                'error': f"Google Cloud Storage error: {str(e)}",
                'gcs_path': None
            }
        
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return {
                'success': False,
                'error': f"Upload error: {str(e)}",
                'gcs_path': None
            }
    
    async def download_file(self, user_id: str, file_id: str, filename: str) -> Dict[str, Any]:
        """
        Download file from Google Cloud Storage.
        
        Args:
            user_id: User identifier for multi-tenant access
            file_id: Unique file identifier
            filename: Original filename
        
        Returns:
            Dict with download result and file content
        """
        if not self.is_initialized():
            raise Exception("GCP service not initialized")
        
        try:
            # Generate blob path
            blob_path = self._get_blob_path(user_id, file_id, filename)
            blob = self._bucket.blob(blob_path)
            
            # Check if file exists
            if not blob.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'content': None
                }
            
            # Download file content
            content = blob.download_as_bytes()
            
            logger.info(f"Successfully downloaded file from GCS: {blob_path}")
            
            return {
                'success': True,
                'content': content,
                'size': len(content),
                'content_type': blob.content_type,
                'metadata': blob.metadata or {},
                'updated': blob.updated
            }
            
        except GoogleAPIError as e:
            logger.error(f"GCS download failed: {str(e)}")
            return {
                'success': False,
                'error': f"Google Cloud Storage error: {str(e)}",
                'content': None
            }
        
        except Exception as e:
            logger.error(f"File download failed: {str(e)}")
            return {
                'success': False,
                'error': f"Download error: {str(e)}",
                'content': None
            }
    
    async def delete_file(self, user_id: str, file_id: str, filename: str) -> Dict[str, Any]:
        """
        Delete file from Google Cloud Storage.
        
        Args:
            user_id: User identifier for multi-tenant access
            file_id: Unique file identifier
            filename: Original filename
        
        Returns:
            Dict with deletion result
        """
        if not self.is_initialized():
            raise Exception("GCP service not initialized")
        
        try:
            # Generate blob path
            blob_path = self._get_blob_path(user_id, file_id, filename)
            blob = self._bucket.blob(blob_path)
            
            # Check if file exists
            if not blob.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            # Delete file
            blob.delete()
            
            logger.info(f"Successfully deleted file from GCS: {blob_path}")
            
            return {
                'success': True,
                'deleted_path': blob_path
            }
            
        except GoogleAPIError as e:
            logger.error(f"GCS deletion failed: {str(e)}")
            return {
                'success': False,
                'error': f"Google Cloud Storage error: {str(e)}"
            }
        
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return {
                'success': False,
                'error': f"Deletion error: {str(e)}"
            }
    
    async def list_user_files(self, user_id: str, prefix: str = "") -> Dict[str, Any]:
        """
        List files for a specific user.
        
        Args:
            user_id: User identifier
            prefix: Additional prefix filter
        
        Returns:
            Dict with list of user's files
        """
        if not self.is_initialized():
            raise Exception("GCP service not initialized")
        
        try:
            # Build prefix for user's files
            user_prefix = f"{self.base_path}/{user_id}/"
            if prefix:
                user_prefix += prefix
            
            # List blobs with prefix
            blobs = self._bucket.list_blobs(prefix=user_prefix)
            
            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'metadata': blob.metadata or {}
                })
            
            logger.info(f"Listed {len(files)} files for user {user_id}")
            
            return {
                'success': True,
                'files': files,
                'count': len(files)
            }
            
        except Exception as e:
            logger.error(f"File listing failed: {str(e)}")
            return {
                'success': False,
                'error': f"Listing error: {str(e)}",
                'files': []
            }
    
    async def generate_signed_url(
        self, 
        user_id: str, 
        file_id: str, 
        filename: str,
        expiration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Generate signed URL for temporary file access.
        
        Args:
            user_id: User identifier
            file_id: Unique file identifier
            filename: Original filename
            expiration_minutes: URL expiration in minutes
        
        Returns:
            Dict with signed URL information
        """
        if not self.is_initialized():
            raise Exception("GCP service not initialized")
        
        try:
            # Generate blob path
            blob_path = self._get_blob_path(user_id, file_id, filename)
            blob = self._bucket.blob(blob_path)
            
            # Check if file exists
            if not blob.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'signed_url': None
                }
            
            # Generate signed URL
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method='GET'
            )
            
            logger.info(f"Generated signed URL for: {blob_path}")
            
            return {
                'success': True,
                'signed_url': signed_url,
                'expires_at': expiration,
                'blob_path': blob_path
            }
            
        except Exception as e:
            logger.error(f"Signed URL generation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Signed URL error: {str(e)}",
                'signed_url': None
            }
    
    async def get_storage_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get storage usage statistics for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            Dict with storage usage information
        """
        try:
            user_files = await self.list_user_files(user_id)
            
            if not user_files['success']:
                return user_files
            
            total_size = sum(file['size'] or 0 for file in user_files['files'])
            file_count = len(user_files['files'])
            
            # Calculate size in different units
            size_mb = total_size / (1024 * 1024)
            size_gb = size_mb / 1024
            
            return {
                'success': True,
                'user_id': user_id,
                'total_files': file_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(size_mb, 2),
                'total_size_gb': round(size_gb, 4),
                'files': user_files['files']
            }
            
        except Exception as e:
            logger.error(f"Storage usage calculation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Usage calculation error: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check GCP service health.
        
        Returns:
            Dict with health status
        """
        try:
            if not self.is_initialized():
                return {
                    'healthy': False,
                    'error': 'Service not initialized'
                }
            
            # Test bucket access
            bucket_exists = self._bucket.exists()
            
            if not bucket_exists:
                return {
                    'healthy': False,
                    'error': f'Bucket {self.bucket_name} not accessible'
                }
            
            return {
                'healthy': True,
                'bucket_name': self.bucket_name,
                'project_id': self.project_id,
                'base_path': self.base_path
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': f'Health check failed: {str(e)}'
            }


# Global GCP service instance
gcp_service = GCPService()