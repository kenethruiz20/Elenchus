#!/usr/bin/env python3
"""
Test background processing functionality.
"""

import asyncio
from app.services.rag_upload_service import rag_upload_service
from app.database import mongodb_manager
from app.services.gcp_service import gcp_service
from app.services.document_ai_service import document_ai_service

async def test_background():
    """Test background processing directly."""
    
    # Initialize services
    await mongodb_manager.initialize()
    await gcp_service.initialize()
    await document_ai_service.initialize()
    await rag_upload_service.initialize()
    
    print(f"🤖 AI Service: {document_ai_service.is_initialized()}")
    
    # Test content
    test_content = b"""Legal Services Agreement

This agreement outlines the terms for legal services between the law firm and client.

Key provisions:
- Scope of work: Contract review and legal advice
- Payment terms: $300/hour for associate work
- Confidentiality requirements
- Term: 12 months

Both parties agree to the terms outlined in this document."""
    
    # Test background processing directly
    try:
        await rag_upload_service._process_document_background(
            "test_doc_id",
            test_content,
            "test_user_id"
        )
        print("✅ Background processing completed")
    except Exception as e:
        print(f"❌ Background processing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_background())