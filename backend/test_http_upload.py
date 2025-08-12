#!/usr/bin/env python3
"""Test document upload through HTTP API endpoint."""

import requests
import json
import sys
from pathlib import Path

def test_http_upload():
    """Test document upload via HTTP API."""
    
    print("=" * 60)
    print("HTTP Document Upload Test")
    print("=" * 60)
    
    # API configuration
    base_url = "http://localhost:8000"
    
    # First, we need to login to get a token
    print("\n🔐 Logging in...")
    
    # Try to login with test credentials
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    login_response = requests.post(
        f"{base_url}/api/v1/auth/login",
        data=login_data
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print("   ✅ Login successful")
        print(f"   Token: {access_token[:20]}...")
    else:
        print("   ❌ Login failed")
        print(f"   Status: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        
        # Try to register first
        print("\n📝 Registering test user...")
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        register_response = requests.post(
            f"{base_url}/api/v1/auth/register",
            json=register_data
        )
        
        if register_response.status_code in [200, 201]:
            print("   ✅ Registration successful")
            
            # Now login
            login_response = requests.post(
                f"{base_url}/api/v1/auth/login",
                data=login_data
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                print("   ✅ Login successful after registration")
            else:
                print("   ❌ Login failed after registration")
                return False
        else:
            print("   ❌ Registration failed")
            print(f"   Response: {register_response.text}")
            return False
    
    # Prepare headers with auth token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test document upload
    print("\n📤 Uploading test document...")
    
    # Create test file content
    test_content = """This is a test document uploaded via HTTP API.
It should be processed and stored in GCS.

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."""
    
    # Prepare multipart form data
    files = {
        'file': ('test_http_document.txt', test_content, 'text/plain')
    }
    
    data = {
        'tags': json.dumps(["test", "http", "verification"]),
        'category': 'testing'
    }
    
    upload_response = requests.post(
        f"{base_url}/api/v1/rag/documents/upload",
        headers=headers,
        files=files,
        data=data
    )
    
    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        print("   ✅ Upload successful!")
        print(f"   Document ID: {upload_data.get('id')}")
        print(f"   Filename: {upload_data.get('filename')}")
        print(f"   Size: {upload_data.get('file_size')} bytes")
        print(f"   Status: {upload_data.get('status')}")
        
        document_id = upload_data.get('id')
        
        # Check document status
        print("\n🔍 Checking document status...")
        status_response = requests.get(
            f"{base_url}/api/v1/rag/documents/{document_id}/status",
            headers=headers
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print("   ✅ Status retrieved")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Progress: {status_data.get('progress')}")
            print(f"   Chunks: {status_data.get('chunks_created')}")
        else:
            print("   ❌ Failed to get status")
            print(f"   Response: {status_response.text}")
        
        # List user documents
        print("\n📋 Listing user documents...")
        list_response = requests.get(
            f"{base_url}/api/v1/rag/documents",
            headers=headers,
            params={"limit": 5}
        )
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            documents = list_data.get('documents', [])
            print(f"   ✅ Found {len(documents)} documents")
            for doc in documents[:3]:
                print(f"      - {doc.get('filename')} ({doc.get('file_size')} bytes)")
        else:
            print("   ❌ Failed to list documents")
        
        # Delete test document
        print("\n🗑️  Deleting test document...")
        delete_response = requests.delete(
            f"{base_url}/api/v1/rag/documents/{document_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print("   ✅ Document deleted")
        else:
            print("   ⚠️  Failed to delete document")
        
    else:
        print("   ❌ Upload failed!")
        print(f"   Status: {upload_response.status_code}")
        print(f"   Response: {upload_response.text}")
        return False
    
    # Check RAG health
    print("\n🏥 Checking RAG system health...")
    health_response = requests.get(f"{base_url}/api/v1/rag/health")
    
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"   Overall status: {health_data.get('status')}")
        services = health_data.get('services', {})
        for service_name, service_data in services.items():
            print(f"   {service_name}: {service_data.get('status')}")
    
    print("\n" + "=" * 60)
    print("✅ HTTP upload test completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    print("\n⚠️  Make sure the backend server is running on port 8000!")
    print("   Run: cd backend && ./devrun.sh\n")
    
    try:
        # Check if server is running
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running\n")
            success = test_http_upload()
            sys.exit(0 if success else 1)
        else:
            print("❌ Server returned unexpected status")
            sys.exit(1)
    except requests.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Please start the server first!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)