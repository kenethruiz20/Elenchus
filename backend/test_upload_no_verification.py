#!/usr/bin/env python3
"""
Test document upload without email verification requirement.
"""

import asyncio
import aiohttp
import sys
from pathlib import Path

async def test_upload():
    # First, login to get a token
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        async with session.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data
        ) as response:
            if response.status != 200:
                print(f"Login failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            auth_response = await response.json()
            token = auth_response["access_token"]
            print(f"✅ Login successful")
            print(f"   User: {auth_response['user']['email']}")
            print(f"   Verified: {auth_response['user']['is_verified']}")
        
        # Prepare headers with auth token
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Create a test file
        test_file_path = Path("/tmp/test_document.txt")
        test_file_path.write_text("This is a test document for RAG upload without email verification.")
        
        # Upload document
        with open(test_file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file',
                          f,
                          filename='test_document.txt',
                          content_type='text/plain')
            data.add_field('tags', '["test", "no-verification"]')
            data.add_field('category', 'test')
            
            async with session.post(
                "http://localhost:8000/api/v1/rag/documents/upload",
                data=data,
                headers=headers
            ) as response:
                print(f"\n📤 Upload response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Upload successful!")
                    print(f"   Document ID: {result['id']}")
                    print(f"   Filename: {result['filename']}")
                    print(f"   Status: {result['status']}")
                else:
                    text = await response.text()
                    print(f"❌ Upload failed: {text}")
                    
                    # Check if it's the email verification error
                    if "Email not verified" in text:
                        print("\n⚠️  ISSUE: Email verification is still required!")
                        print("   The fix may not have been applied correctly.")
                    
                return response.status

if __name__ == "__main__":
    result = asyncio.run(test_upload())
    sys.exit(0 if result == 200 else 1)