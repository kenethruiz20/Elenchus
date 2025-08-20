#!/usr/bin/env python3
"""
Test AI metadata generation for uploaded documents.
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
    def __init__(self, filename, content, content_type=None):
        self.filename = filename
        self.file = None
        self.content_type = content_type or "text/plain"
        self._content = content
    
    async def read(self):
        return self._content
    
    async def seek(self, pos):
        pass

async def test_ai_metadata_generation():
    """Test the AI metadata generation for different document types."""
    
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
    
    print(f"✅ Found user: {user.email}")
    print(f"🤖 AI Service initialized: {document_ai_service.is_initialized()}")
    
    # Test content for different file types
    test_files = [
        {
            "filename": "legal_contract.txt",
            "content": """
LEGAL SERVICES AGREEMENT

This Legal Services Agreement ("Agreement") is entered into on January 15, 2025, between Smith & Associates Law Firm ("Firm") and ABC Corporation ("Client").

SCOPE OF SERVICES:
The Firm agrees to provide the following legal services:
1. Contract review and negotiation
2. Corporate governance advice
3. Compliance consulting
4. Intellectual property protection

COMPENSATION:
Client agrees to pay the Firm at the following rates:
- Senior Partner: $500/hour
- Associate: $300/hour
- Paralegal: $150/hour

TERM:
This Agreement shall commence on January 15, 2025, and continue for a period of twelve (12) months, unless terminated earlier in accordance with the terms herein.

CONFIDENTIALITY:
Both parties acknowledge that confidential information may be disclosed during the course of this engagement and agree to maintain strict confidentiality.

By signing below, both parties agree to be bound by the terms and conditions of this Agreement.
            """.strip(),
            "content_type": "text/plain"
        },
        {
            "filename": "financial_report.csv",
            "content": """Quarter,Revenue,Expenses,Profit,Margin
Q1 2024,1500000,1200000,300000,20%
Q2 2024,1750000,1300000,450000,25.7%
Q3 2024,1900000,1400000,500000,26.3%
Q4 2024,2100000,1600000,500000,23.8%
Q1 2025,2250000,1650000,600000,26.7%""".strip(),
            "content_type": "text/csv"
        }
    ]
    
    for test_file in test_files:
        print(f"\n📄 Testing: {test_file['filename']}")
        print("=" * 50)
        
        mock_file = MockFile(
            test_file['filename'], 
            test_file['content'].encode(),
            test_file['content_type']
        )
        
        try:
            # Upload document
            start_time = time.time()
            document = await rag_upload_service.upload_document(
                user_id=str(user.id),
                file=mock_file,
                tags=["test", "ai-metadata"],
                category="testing",
                background_tasks=None  # No background processing for this test
            )
            
            print(f"✅ Document uploaded: {document.id}")
            print(f"   Status: {document.status}")
            print(f"   GCS Path: {document.gcs_path[:50]}..." if document.gcs_path else "   No GCS Path")
            
            # Wait for background processing to complete
            print("⏳ Waiting for background processing...")
            max_wait = 60  # Wait up to 60 seconds
            check_interval = 3
            
            for i in range(max_wait // check_interval):
                await asyncio.sleep(check_interval)
                
                # Check document status
                updated_doc = await RAGDocument.find_one(RAGDocument.id == document.id)
                if updated_doc:
                    print(f"   Status check {i+1}: {updated_doc.status}")
                    
                    if updated_doc.status in ['completed', 'failed']:
                        document = updated_doc
                        break
                    
                    # Check if AI metadata is available
                    if updated_doc.metadata.ai_summary:
                        document = updated_doc
                        break
            
            # Display results
            print(f"\n📊 Results for {test_file['filename']}:")
            print(f"   Final Status: {document.status}")
            print(f"   Processing Time: {time.time() - start_time:.1f}s")
            
            if document.metadata.ai_summary:
                print(f"\n🤖 AI-Generated Summary:")
                print(f"   {document.metadata.ai_summary}")
                
                print(f"\n📝 AI-Generated Description:")
                desc = document.metadata.ai_detailed_description
                if desc and len(desc) > 200:
                    print(f"   {desc[:200]}...")
                else:
                    print(f"   {desc}")
                
                print(f"\n🏷️  AI-Generated Topics:")
                for i, topic in enumerate(document.metadata.ai_topics or [], 1):
                    print(f"   {i}. {topic}")
                
                print(f"\n📅 Generated At: {document.metadata.ai_metadata_generated_at}")
                
            else:
                print("⚠️  No AI metadata generated")
                if document.processing_metrics.errors_encountered:
                    print(f"   Errors: {document.processing_metrics.errors_encountered}")
            
            print(f"\n📥 Download Available: {'Yes' if document.gcs_path else 'No'}")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 AI Metadata Generation Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_metadata_generation())