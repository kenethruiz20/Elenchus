#!/usr/bin/env python3
"""Test the document upload API endpoint to diagnose issues."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_document_upload_api():
    """Test the document upload through the API service."""
    
    print("=" * 60)
    print("Document Upload API Test")
    print("=" * 60)
    
    # Import required modules
    from app.database import mongodb_manager
    from app.services.gcp_service import gcp_service
    from app.services.rag_upload_service import rag_upload_service
    from app.models.user import User
    from app.models.rag_document import RAGDocument
    from fastapi import UploadFile
    from io import BytesIO
    import tempfile
    
    # Initialize services
    print("\n🚀 Initializing services...")
    
    # Initialize MongoDB
    print("   Initializing MongoDB...")
    await mongodb_manager.initialize()
    print("   ✅ MongoDB initialized")
    
    # Initialize GCP
    print("   Initializing GCP service...")
    gcp_init = await gcp_service.initialize()
    if gcp_init:
        print("   ✅ GCP service initialized")
    else:
        print("   ❌ GCP service failed to initialize")
        return False
    
    # Initialize upload service
    print("   Initializing upload service...")
    upload_init = await rag_upload_service.initialize()
    if upload_init:
        print("   ✅ Upload service initialized")
    else:
        print("   ❌ Upload service failed to initialize")
        return False
    
    # Create or get test user
    print("\n👤 Setting up test user...")
    test_email = "test@example.com"
    test_user = await User.find_one(User.email == test_email)
    
    if not test_user:
        print("   Creating test user...")
        test_user = User(
            email=test_email,
            username="testuser",
            full_name="Test User",
            hashed_password="dummy_hash",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        await test_user.insert()
        print(f"   ✅ Test user created: {test_user.id}")
    else:
        print(f"   ✅ Test user exists: {test_user.id}")
    
    # Create test document content
    test_content = b"""This is a test document for upload verification.
It contains multiple lines of text.
This should be processed and uploaded to GCS.

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."""
    
    # Create UploadFile object
    print("\n📄 Creating test document...")
    file_like = BytesIO(test_content)
    upload_file = UploadFile(
        filename="test_document.txt",
        file=file_like,
        headers={"content-type": "text/plain"}
    )
    
    # Test upload without background tasks
    print("\n📤 Testing document upload (without background processing)...")
    try:
        document = await rag_upload_service.upload_document(
            user_id=str(test_user.id),
            file=upload_file,
            tags=["test", "verification"],
            category="testing",
            background_tasks=None  # No background processing for now
        )
        
        print("   ✅ Document uploaded successfully!")
        print(f"   Document ID: {document.id}")
        print(f"   Filename: {document.filename}")
        print(f"   Original: {document.original_filename}")
        print(f"   Size: {document.file_size} bytes")
        print(f"   GCS Path: {document.gcs_path}")
        print(f"   Status: {document.status}")
        
        # Check if file exists in GCS
        if document.gcs_path:
            print("\n🔍 Verifying GCS upload...")
            # Extract file_id from filename
            file_id = document.filename.split('_')[0]
            
            download_result = await gcp_service.download_file(
                user_id=str(test_user.id),
                file_id=file_id,
                filename=document.original_filename
            )
            
            if download_result['success']:
                print("   ✅ File verified in GCS")
                print(f"   Downloaded size: {download_result['size']} bytes")
            else:
                print("   ❌ File NOT found in GCS")
                print(f"   Error: {download_result.get('error')}")
        else:
            print("\n   ⚠️  No GCS path set - file may not have been uploaded")
        
        # Check document in database
        print("\n🔍 Verifying database record...")
        db_doc = await RAGDocument.find_one(RAGDocument.id == document.id)
        if db_doc:
            print("   ✅ Document found in database")
            print(f"   Status: {db_doc.status}")
            print(f"   GCS Path: {db_doc.gcs_path}")
        else:
            print("   ❌ Document NOT found in database")
        
        # List user's documents
        print("\n📋 Listing user documents...")
        user_docs = await rag_upload_service.list_user_documents(
            user_id=str(test_user.id),
            limit=5
        )
        
        if user_docs['success']:
            print(f"   Found {user_docs['total_count']} documents")
            for doc in user_docs['documents'][:3]:
                print(f"      - {doc['filename']} ({doc['file_size']} bytes) - Status: {doc['status']}")
        
        # Clean up - delete test document
        print("\n🗑️  Cleaning up test document...")
        delete_result = await rag_upload_service.delete_document(
            document_id=str(document.id),
            user_id=str(test_user.id)
        )
        
        if delete_result['success']:
            print("   ✅ Test document deleted")
            print(f"   Deleted chunks: {delete_result['deleted_chunks']}")
        else:
            print("   ⚠️  Could not delete test document")
        
    except Exception as e:
        print(f"   ❌ Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Close connections
    print("\n🔌 Closing connections...")
    await mongodb_manager.close()
    
    print("\n" + "=" * 60)
    print("✅ Document upload API test completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_document_upload_api())
    sys.exit(0 if success else 1)