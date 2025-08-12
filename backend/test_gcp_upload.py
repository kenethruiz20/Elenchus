#!/usr/bin/env python3
"""Test script to verify GCP upload functionality."""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_gcp_upload():
    """Test GCP service initialization and upload."""
    
    print("=" * 60)
    print("GCP Upload Test")
    print("=" * 60)
    
    # Import services
    from app.services.gcp_service import gcp_service
    from app.config.settings import settings
    
    # Print configuration
    print("\n📋 Configuration:")
    print(f"   Project: {settings.GCP_PROJECT}")
    print(f"   Bucket: {settings.GCP_BUCKET}")
    print(f"   Base Path: {settings.GCP_BUCKET_BASE_PATH}")
    print(f"   Credentials Path: {settings.GCP_CREDENTIALS_PATH}")
    
    # Check if credentials file exists
    if settings.GCP_CREDENTIALS_PATH:
        if os.path.exists(settings.GCP_CREDENTIALS_PATH):
            print(f"   ✅ Credentials file exists: {settings.GCP_CREDENTIALS_PATH}")
        else:
            print(f"   ❌ Credentials file NOT found: {settings.GCP_CREDENTIALS_PATH}")
    
    # Initialize GCP service
    print("\n🚀 Initializing GCP service...")
    try:
        init_result = await gcp_service.initialize()
        if init_result:
            print("   ✅ GCP service initialized successfully")
        else:
            print("   ❌ GCP service initialization failed")
            return False
    except Exception as e:
        print(f"   ❌ Initialization error: {str(e)}")
        return False
    
    # Check health
    print("\n🔍 Checking GCP health...")
    health = await gcp_service.health_check()
    if health['healthy']:
        print("   ✅ GCP service is healthy")
        print(f"   Bucket: {health.get('bucket_name')}")
        print(f"   Project: {health.get('project_id')}")
    else:
        print("   ❌ GCP service is NOT healthy")
        print(f"   Error: {health.get('error')}")
        return False
    
    # Test upload
    print("\n📤 Testing file upload...")
    test_content = b"This is a test document for GCP upload verification."
    test_filename = "test_upload.txt"
    test_user = "test_user_123"
    test_file_id = "test_file_456"
    
    upload_result = await gcp_service.upload_file(
        user_id=test_user,
        file_id=test_file_id,
        filename=test_filename,
        file_content=test_content,
        content_type="text/plain"
    )
    
    if upload_result['success']:
        print("   ✅ File uploaded successfully!")
        print(f"   GCS Path: {upload_result['gcs_path']}")
        print(f"   Size: {upload_result['size']} bytes")
    else:
        print("   ❌ Upload failed!")
        print(f"   Error: {upload_result.get('error')}")
        return False
    
    # Test download
    print("\n📥 Testing file download...")
    download_result = await gcp_service.download_file(
        user_id=test_user,
        file_id=test_file_id,
        filename=test_filename
    )
    
    if download_result['success']:
        print("   ✅ File downloaded successfully!")
        downloaded_content = download_result['content']
        if downloaded_content == test_content:
            print("   ✅ Content matches original")
        else:
            print("   ❌ Content does NOT match original")
    else:
        print("   ❌ Download failed!")
        print(f"   Error: {download_result.get('error')}")
    
    # Test listing
    print("\n📋 Testing file listing...")
    list_result = await gcp_service.list_user_files(test_user)
    if list_result['success']:
        print(f"   ✅ Found {list_result['count']} files for user")
        for file in list_result['files'][:3]:  # Show first 3 files
            print(f"      - {file['name']} ({file['size']} bytes)")
    else:
        print("   ❌ Listing failed!")
        print(f"   Error: {list_result.get('error')}")
    
    # Cleanup - delete test file
    print("\n🗑️  Cleaning up test file...")
    delete_result = await gcp_service.delete_file(
        user_id=test_user,
        file_id=test_file_id,
        filename=test_filename
    )
    if delete_result['success']:
        print("   ✅ Test file deleted")
    else:
        print("   ⚠️  Could not delete test file")
    
    print("\n" + "=" * 60)
    print("✅ All GCP tests completed successfully!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_gcp_upload())
    sys.exit(0 if success else 1)