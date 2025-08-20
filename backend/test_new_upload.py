#!/usr/bin/env python3
"""
Test new document upload after MongoDB index fix.
"""

import asyncio
from datetime import datetime
from app.models.user import User
from app.services.rag_upload_service import rag_upload_service
from app.database import mongodb_manager
from app.models.rag_document import RAGDocument
from app.services.gcp_service import gcp_service

class MockFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = None
        self.content_type = "text/plain"
        self._content = content
    
    async def read(self):
        return self._content
    
    async def seek(self, pos):
        pass

async def test_new_upload():
    # Initialize database
    await mongodb_manager.initialize()
    
    # Initialize GCP service first
    gcp_init = await gcp_service.initialize()
    print(f"GCP Service initialized: {gcp_init}")
    
    # Initialize RAG upload service
    await rag_upload_service.initialize()
    
    # Get test user
    user = await User.find_one({"email": "test@example.com"})
    if not user:
        print("❌ Test user not found")
        return
    
    print(f"✅ Found user: {user.email}")
    
    # Create test file
    test_content = f"Test document created at {datetime.utcnow()}\nThis is a test to verify GCS upload works after MongoDB fix."
    mock_file = MockFile("test_after_fix.txt", test_content.encode())
    
    # Upload document
    print("\n📤 Uploading document...")
    try:
        document = await rag_upload_service.upload_document(
            user_id=str(user.id),
            file=mock_file,
            tags=["test", "after-fix"],
            category="testing",
            background_tasks=None  # No background tasks for direct testing
        )
        
        print(f"✅ Document created:")
        print(f"   ID: {document.id}")
        print(f"   Status: {document.status}")
        print(f"   GCS Path: {document.gcs_path}")
        print(f"   File Size: {document.file_size}")
        
        # Check if it was saved properly
        await asyncio.sleep(1)
        
        # Reload from database
        saved_doc = await RAGDocument.find_one(RAGDocument.id == document.id)
        if saved_doc:
            print(f"\n✅ Document saved to MongoDB:")
            print(f"   Status: {saved_doc.status}")
            print(f"   GCS Path: {saved_doc.gcs_path}")
            print(f"   Errors: {saved_doc.processing_metrics.errors_encountered}")
            
            if saved_doc.gcs_path:
                print(f"\n🎉 SUCCESS: File uploaded to GCS at: {saved_doc.gcs_path}")
            else:
                print(f"\n⚠️  WARNING: GCS path is still None")
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_upload())