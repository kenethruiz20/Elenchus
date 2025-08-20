#!/usr/bin/env python3
"""
Final test of document upload with all fixes applied.
"""

import asyncio
from datetime import datetime
from app.models.user import User
from app.services.rag_upload_service import rag_upload_service
from app.database import mongodb_manager
from app.models.rag_document import RAGDocument
from app.services.gcp_service import gcp_service

class MockFile:
    def __init__(self, filename, content, content_type=None):
        self.filename = filename
        self.file = None
        self.content_type = content_type or "application/octet-stream"
        self._content = content
    
    async def read(self):
        return self._content
    
    async def seek(self, pos):
        pass

async def test_final_upload():
    # Initialize services
    await mongodb_manager.initialize()
    await gcp_service.initialize()
    await rag_upload_service.initialize()
    
    # Get test user
    user = await User.find_one({"email": "test@example.com"})
    if not user:
        print("❌ Test user not found")
        return
    
    print(f"✅ Found user: {user.email}")
    print(f"   Is verified: {user.is_verified}")
    print(f"   Is active: {user.is_active}")
    
    # Test different file types
    test_files = [
        ("test_document.txt", b"This is a plain text document for testing.", "text/plain"),
        ("test_document.pdf", b"%PDF-1.4 fake pdf content for testing", "application/pdf"),
        ("test_document.docx", b"PK fake docx content for testing", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ]
    
    for filename, content, content_type in test_files:
        print(f"\n📤 Testing upload of {filename}...")
        
        mock_file = MockFile(filename, content, content_type)
        
        try:
            # Upload document
            document = await rag_upload_service.upload_document(
                user_id=str(user.id),
                file=mock_file,
                tags=["test", "final"],
                category="testing",
                background_tasks=None
            )
            
            print(f"✅ Document created:")
            print(f"   ID: {document.id}")
            print(f"   Status: {document.status}")
            print(f"   GCS Path: {document.gcs_path}")
            print(f"   File Type: {document.file_type}")
            
            # Check if properly saved
            await asyncio.sleep(0.5)
            saved_doc = await RAGDocument.find_one(RAGDocument.id == document.id)
            
            if saved_doc:
                if saved_doc.gcs_path:
                    print(f"   ✅ Uploaded to GCS: {saved_doc.gcs_path}")
                else:
                    print(f"   ⚠️  No GCS path")
                
                if saved_doc.processing_metrics.errors_encountered:
                    print(f"   ⚠️  Errors: {saved_doc.processing_metrics.errors_encountered}")
            
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_final_upload())