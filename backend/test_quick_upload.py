#!/usr/bin/env python3
"""
Quick test of the complete upload and AI metadata functionality.
"""

import asyncio
import time
from datetime import datetime
from app.models.user import User
from app.services.rag_upload_service import rag_upload_service
from app.services.gcp_service import gcp_service
from app.services.document_ai_service import document_ai_service
from app.database import mongodb_manager
from app.models.rag_document import RAGDocument

class MockFile:
    def __init__(self, filename, content, content_type="text/plain"):
        self.filename = filename
        self.file = None
        self.content_type = content_type
        self._content = content
    
    async def read(self):
        return self._content
    
    async def seek(self, pos):
        pass

async def quick_test():
    """Quick test of the upload and AI functionality."""
    
    # Initialize services
    await mongodb_manager.initialize()
    await gcp_service.initialize()
    await document_ai_service.initialize()
    await rag_upload_service.initialize()
    
    # Get test user
    user = await User.find_one({"email": "test@example.com"})
    if not user:
        print("❌ Test user not found")
        return
    
    print(f"✅ User: {user.email}")
    print(f"🤖 AI Service: {document_ai_service.is_initialized()}")
    
    # Test simple document
    content = """
    BUSINESS PROPOSAL
    
    Executive Summary:
    This document outlines a comprehensive business proposal for expanding our operations into the European market.
    
    Market Analysis:
    The European market presents significant opportunities for growth, with an estimated market size of $2.5 billion.
    
    Financial Projections:
    - Year 1: $500K revenue
    - Year 2: $1.2M revenue  
    - Year 3: $2.1M revenue
    
    Implementation Plan:
    We will establish regional offices in London, Berlin, and Paris to serve as our European headquarters.
    """.strip()
    
    mock_file = MockFile("business_proposal.txt", content.encode())
    
    try:
        # Upload document
        print(f"\n📤 Uploading document...")
        document = await rag_upload_service.upload_document(
            user_id=str(user.id),
            file=mock_file,
            tags=["business", "proposal"],
            category="planning",
            background_tasks=None
        )
        
        print(f"✅ Upload successful: {document.id}")
        print(f"   GCS Path: {'Yes' if document.gcs_path else 'No'}")
        
        # Wait briefly for processing
        print("⏳ Waiting for AI processing...")
        await asyncio.sleep(10)
        
        # Check results
        updated_doc = await RAGDocument.find_one(RAGDocument.id == document.id)
        if updated_doc:
            print(f"\n📊 Results:")
            print(f"   Status: {updated_doc.status}")
            
            if updated_doc.metadata.ai_summary:
                print(f"   AI Summary: {updated_doc.metadata.ai_summary}")
                print(f"   AI Topics: {updated_doc.metadata.ai_topics}")
            else:
                print("   No AI metadata yet")
        
        print(f"\n🔗 Download URL: /api/v1/rag/documents/{document.id}/download")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(quick_test())