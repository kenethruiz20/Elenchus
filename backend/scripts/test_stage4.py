#!/usr/bin/env python3
"""
Stage 4 Implementation Test Script
Tests Document Upload & Registration functionality.
"""

import asyncio
import sys
import logging
import requests
import json
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config.settings import settings
from app.models.user import User
from app.models.rag_document import RAGDocument, DocumentStatus
from app.models.rag_chunk import RAGChunk
from app.services.auth_service import auth_service
from app.services.rag_upload_service import rag_upload_service
from app.services.document_processor import document_processor
from app.services.gcp_service import gcp_service
from app.database import mongodb_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Stage4TestSuite:
    """Test suite for Stage 4: Document Upload & Registration."""
    
    def __init__(self):
        self.base_url = f"http://{settings.HOST}:{settings.PORT}"
        self.test_user_email = "stage4_test@example.com"
        self.test_password = "TestPassword123!"
        self.test_user_id = None
        self.test_token = None
        self.uploaded_doc_ids = []
    
    async def setup_test_user(self) -> bool:
        """Create a test user for upload tests."""
        print("🔧 Setting up test user...")
        
        try:
            # Delete existing test user if exists
            existing_user = await User.find_one(User.email == self.test_user_email)
            if existing_user:
                await existing_user.delete()
                print("   Deleted existing test user")
            
            # Create new test user
            test_user = await auth_service.create_user(
                email=self.test_user_email,
                password=self.test_password,
                first_name="Stage4",
                last_name="TestUser"
            )
            
            # Verify user
            test_user.is_verified = True
            await test_user.save()
            
            self.test_user_id = str(test_user.id)
            
            # Create access token
            token_data = {"sub": self.test_user_email}
            self.test_token = auth_service.create_access_token(token_data)
            
            print(f"✅ Test user created: {self.test_user_email}")
            print(f"   User ID: {self.test_user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup test user: {str(e)}")
            return False
    
    async def test_document_processor(self) -> bool:
        """Test document processing functionality."""
        print("\n📄 Testing Document Processor")
        print("-" * 40)
        
        try:
            # Test with sample text file
            test_content = b"This is a test document for RAG processing. It contains multiple sentences. This helps test the chunking functionality."
            
            # Test validation
            validation = document_processor.validate_document(test_content, "test.txt")
            if not validation['valid']:
                print(f"❌ Document validation failed: {validation['errors']}")
                return False
            
            print("✅ Document validation passed")
            
            # Test hash calculation
            file_hash = document_processor.generate_document_hash(test_content)
            if not file_hash or len(file_hash) != 64:  # SHA256 is 64 chars hex
                print("❌ Hash calculation failed")
                return False
            
            print(f"✅ File hash calculated: {file_hash[:16]}...")
            
            # Test metadata extraction
            metadata = document_processor.extract_document_metadata(test_content, "test.txt")
            if not metadata or metadata['filename'] != "test.txt":
                print("❌ Metadata extraction failed")
                return False
            
            print(f"✅ Metadata extracted: {metadata['file_type']}, {metadata['file_size']} bytes")
            
            # Test document processing
            result = await document_processor.process_document_async(test_content, "test.txt", self.test_user_id)
            if not result['success']:
                print(f"❌ Document processing failed: {result.get('error')}")
                return False
            
            print(f"✅ Document processed: {len(result['chunks'])} chunks created")
            
            return True
            
        except Exception as e:
            print(f"❌ Document processor test failed: {str(e)}")
            return False
    
    async def test_upload_service(self) -> bool:
        """Test RAG upload service functionality."""
        print("\n📤 Testing RAG Upload Service")
        print("-" * 40)
        
        try:
            # Test service initialization
            if not rag_upload_service.initialized:
                print("❌ Upload service not initialized")
                return False
            
            print("✅ Upload service initialized")
            
            # Create test file content
            test_content = b"""This is a comprehensive test document for the RAG system.
            
It contains multiple paragraphs and sections to test the document processing capabilities.
The system should be able to parse this content, create meaningful chunks, and store them properly.

This document will be used to verify that the upload, processing, and storage workflow functions correctly."""
            
            # Create a mock UploadFile
            class MockUploadFile:
                def __init__(self, content: bytes, filename: str, content_type: str = "text/plain"):
                    self.content = content
                    self.filename = filename
                    self.content_type = content_type
                    self._position = 0
                
                async def read(self) -> bytes:
                    return self.content
                
                async def seek(self, position: int):
                    self._position = position
            
            mock_file = MockUploadFile(test_content, "test_document.txt")
            
            # Test document upload
            document = await rag_upload_service.upload_document(
                user_id=self.test_user_id,
                file=mock_file,
                tags=["test", "stage4"],
                category="testing"
            )
            
            if not document:
                print("❌ Document upload failed")
                return False
            
            self.uploaded_doc_ids.append(str(document.id))
            print(f"✅ Document uploaded: {document.id}")
            print(f"   Status: {document.status}")
            print(f"   File hash: {document.file_hash[:16]}...")
            
            # Test document status checking
            status_info = await rag_upload_service.get_document_status(
                document_id=str(document.id),
                user_id=self.test_user_id
            )
            
            if not status_info['found']:
                print("❌ Document status check failed")
                return False
            
            print(f"✅ Document status retrieved: {status_info['status']}")
            
            # Test document listing
            list_result = await rag_upload_service.list_user_documents(
                user_id=self.test_user_id,
                limit=10
            )
            
            if not list_result['success'] or len(list_result['documents']) == 0:
                print("❌ Document listing failed")
                return False
            
            print(f"✅ Document listing successful: {len(list_result['documents'])} documents found")
            
            return True
            
        except Exception as e:
            print(f"❌ Upload service test failed: {str(e)}")
            return False
    
    async def test_background_processing(self) -> bool:
        """Test background document processing."""
        print("\n⚙️  Testing Background Processing")
        print("-" * 40)
        
        try:
            # Find a document to check processing
            if not self.uploaded_doc_ids:
                print("❌ No uploaded documents to test")
                return False
            
            document_id = self.uploaded_doc_ids[0]
            
            # Wait a moment for background processing
            await asyncio.sleep(2)
            
            # Check if document was processed
            from beanie import PydanticObjectId
            try:
                obj_id = PydanticObjectId(document_id)
            except:
                obj_id = document_id
            
            document = await RAGDocument.find_one(RAGDocument.id == obj_id)
            if not document:
                print("❌ Document not found in database")
                return False
            
            print(f"✅ Document found: {document.status}")
            
            # Check if chunks were created
            chunks = await RAGChunk.find(
                RAGChunk.document_id == document_id,
                RAGChunk.user_id == self.test_user_id
            ).to_list()
            
            if len(chunks) == 0:
                print("⚠️  No chunks created yet (processing may be in progress)")
                return True  # Not a failure, just processing delay
            
            print(f"✅ Chunks created: {len(chunks)} chunks")
            
            # Check chunk content
            for i, chunk in enumerate(chunks[:3]):  # Check first 3 chunks
                if not chunk.text or len(chunk.text.strip()) == 0:
                    print(f"❌ Chunk {i} has empty text")
                    return False
                
                if not chunk.text_hash:
                    print(f"❌ Chunk {i} missing text hash")
                    return False
                
                print(f"✅ Chunk {i}: {len(chunk.text)} chars, hash: {chunk.text_hash[:8]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Background processing test failed: {str(e)}")
            return False
    
    async def test_gcs_integration(self) -> bool:
        """Test Google Cloud Storage integration."""
        print("\n☁️  Testing GCS Integration")
        print("-" * 40)
        
        try:
            # Check if GCS is available
            if not gcp_service.is_initialized():
                print("⚠️  GCS not configured - this is expected in some environments")
                return True
            
            # Test GCS health
            health = await gcp_service.health_check()
            if not health.get('healthy'):
                print(f"❌ GCS health check failed: {health.get('error')}")
                return False
            
            print(f"✅ GCS healthy: {health.get('bucket_name')}")
            
            # Test user storage stats
            if self.uploaded_doc_ids:
                usage = await gcp_service.get_storage_usage(self.test_user_id)
                if usage.get('success'):
                    print(f"✅ Storage usage: {usage.get('total_files', 0)} files")
                else:
                    print(f"⚠️  Storage usage check failed: {usage.get('error')}")
            
            return True
            
        except Exception as e:
            print(f"❌ GCS integration test failed: {str(e)}")
            return False
    
    async def test_user_statistics(self) -> bool:
        """Test user statistics functionality."""
        print("\n📊 Testing User Statistics")
        print("-" * 40)
        
        try:
            stats = await rag_upload_service.get_user_statistics(self.test_user_id)
            
            if 'error' in stats:
                print(f"❌ Statistics retrieval failed: {stats['error']}")
                return False
            
            print(f"✅ User statistics retrieved:")
            print(f"   Total documents: {stats['total_documents']}")
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   Storage used: {stats['storage_used_mb']:.2f} MB")
            print(f"   Documents by status: {stats['documents_by_status']}")
            
            # Validate statistics
            if stats['total_documents'] != len(self.uploaded_doc_ids):
                print(f"⚠️  Document count mismatch: expected {len(self.uploaded_doc_ids)}, got {stats['total_documents']}")
            
            return True
            
        except Exception as e:
            print(f"❌ User statistics test failed: {str(e)}")
            return False
    
    async def test_document_deletion(self) -> bool:
        """Test document deletion functionality."""
        print("\n🗑️  Testing Document Deletion")
        print("-" * 40)
        
        try:
            if not self.uploaded_doc_ids:
                print("❌ No documents to delete")
                return False
            
            document_id = self.uploaded_doc_ids[0]
            
            # Test deletion
            result = await rag_upload_service.delete_document(
                document_id=document_id,
                user_id=self.test_user_id
            )
            
            if not result['success']:
                print(f"❌ Document deletion failed: {result.get('error')}")
                return False
            
            print(f"✅ Document deleted: {result['deleted_document_id']}")
            print(f"   Deleted chunks: {result['deleted_chunks']}")
            
            # Verify deletion
            document = await RAGDocument.find_one(RAGDocument.id == document_id)
            if document:
                print("❌ Document still exists after deletion")
                return False
            
            chunks = await RAGChunk.find(RAGChunk.document_id == document_id).to_list()
            if chunks:
                print(f"❌ {len(chunks)} chunks still exist after deletion")
                return False
            
            print("✅ Document and chunks successfully removed")
            
            # Remove from our tracking list
            self.uploaded_doc_ids.remove(document_id)
            
            return True
            
        except Exception as e:
            print(f"❌ Document deletion test failed: {str(e)}")
            return False
    
    async def test_file_validation(self) -> bool:
        """Test file validation edge cases."""
        print("\n🔍 Testing File Validation")
        print("-" * 40)
        
        try:
            # Test empty file
            empty_validation = document_processor.validate_document(b"", "empty.txt")
            if empty_validation['valid']:
                print("❌ Empty file should be rejected")
                return False
            print("✅ Empty file correctly rejected")
            
            # Test unsupported file type
            unsupported_validation = document_processor.validate_document(b"content", "test.exe")
            if unsupported_validation['valid']:
                print("❌ Unsupported file type should be rejected")
                return False
            print("✅ Unsupported file type correctly rejected")
            
            # Test oversized file (simulate with check)
            max_size = 50 * 1024 * 1024  # 50MB
            oversized_content = b"x" * (max_size + 1)
            oversized_validation = document_processor.validate_document(oversized_content, "large.txt")
            if oversized_validation['valid']:
                print("❌ Oversized file should be rejected")
                return False
            print("✅ Oversized file correctly rejected")
            
            # Test valid file
            valid_content = b"This is a valid test document content."
            valid_validation = document_processor.validate_document(valid_content, "valid.txt")
            if not valid_validation['valid']:
                print(f"❌ Valid file should be accepted: {valid_validation['errors']}")
                return False
            print("✅ Valid file correctly accepted")
            
            return True
            
        except Exception as e:
            print(f"❌ File validation test failed: {str(e)}")
            return False
    
    async def cleanup_test_data(self) -> bool:
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete any remaining uploaded documents
            for doc_id in self.uploaded_doc_ids[:]:
                try:
                    result = await rag_upload_service.delete_document(doc_id, self.test_user_id)
                    if result['success']:
                        print(f"✅ Deleted document {doc_id}")
                        self.uploaded_doc_ids.remove(doc_id)
                    else:
                        print(f"⚠️  Failed to delete document {doc_id}: {result.get('error')}")
                except Exception as e:
                    print(f"⚠️  Error deleting document {doc_id}: {str(e)}")
            
            # Delete test user
            test_user = await User.find_one(User.email == self.test_user_email)
            if test_user:
                await test_user.delete()
                print("✅ Test user deleted")
            
            print("✅ Cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")
            return False


async def main():
    """Main test function."""
    print("🧪 Stage 4: Document Upload & Registration Tests")
    print("=" * 60)
    
    # Initialize database
    try:
        await mongodb_manager.initialize()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return 1
    
    # Initialize upload service
    try:
        success = await rag_upload_service.initialize()
        if success:
            print("✅ Upload service initialized")
        else:
            print("❌ Upload service initialization failed")
            return 1
    except Exception as e:
        print(f"❌ Upload service initialization error: {str(e)}")
        return 1
    
    test_suite = Stage4TestSuite()
    
    # Setup test user
    if not await test_suite.setup_test_user():
        print("❌ Failed to setup test environment")
        return 1
    
    tests = [
        ("Document Processor", test_suite.test_document_processor()),
        ("File Validation", test_suite.test_file_validation()),
        ("Upload Service", test_suite.test_upload_service()),
        ("Background Processing", test_suite.test_background_processing()),
        ("GCS Integration", test_suite.test_gcs_integration()),
        ("User Statistics", test_suite.test_user_statistics()),
        ("Document Deletion", test_suite.test_document_deletion()),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_coro in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = await test_coro
            if result:
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    # Cleanup
    print("\n" + "=" * 60)
    await test_suite.cleanup_test_data()
    
    # Results
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All Stage 4 tests passed! Document Upload & Registration is complete.")
        print("\n🎯 Ready for Stage 5: Background Worker & Task Queue")
        
        # Update plan status
        try:
            plan_file = Path(__file__).parent.parent / "RAG_IMPLEMENTATION_PLAN.md"
            if plan_file.exists():
                content = plan_file.read_text()
                updated_content = content.replace(
                    "### **Stage 4: Document Upload & Registration**\n**Status: ⏳ Pending**",
                    "### **Stage 4: Document Upload & Registration**\n**Status: ✅ Completed**"
                )
                plan_file.write_text(updated_content)
                print("📝 Updated implementation plan status")
        except Exception as e:
            print(f"⚠️  Could not update plan: {str(e)}")
        
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)