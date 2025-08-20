#!/usr/bin/env python3
"""
Direct test of AI metadata generation without background processing.
"""

import asyncio
from app.services.document_ai_service import document_ai_service

async def test_ai_direct():
    """Test AI service directly."""
    
    await document_ai_service.initialize()
    
    print(f"🤖 AI Service initialized: {document_ai_service.is_initialized()}")
    
    if not document_ai_service.is_initialized():
        print("❌ AI service not available")
        return
    
    test_content = """
    BUSINESS PROPOSAL
    
    Executive Summary:
    This document outlines a comprehensive business proposal for expanding our operations into the European market.
    
    Market Analysis:
    The European market presents significant opportunities for growth, with an estimated market size of $2.5 billion.
    Our research indicates strong demand for our products, particularly in Germany, France, and the UK.
    
    Financial Projections:
    - Year 1: $500K revenue with 15% profit margin
    - Year 2: $1.2M revenue with 20% profit margin  
    - Year 3: $2.1M revenue with 25% profit margin
    
    Implementation Plan:
    We will establish regional offices in London, Berlin, and Paris to serve as our European headquarters.
    The implementation will be phased over 18 months starting Q2 2025.
    
    Risk Assessment:
    Key risks include currency fluctuation, regulatory changes, and competitive response.
    We have developed mitigation strategies for each identified risk.
    """.strip()
    
    print("\n📝 Testing AI metadata generation...")
    
    result = await document_ai_service.generate_document_metadata(
        test_content,
        "business_proposal.txt",
        "txt"
    )
    
    print(f"\n📊 Results:")
    print(f"   Success: {result['success']}")
    
    if result['success']:
        print(f"\n🤖 AI Summary:")
        print(f"   {result['ai_summary']}")
        
        print(f"\n📝 AI Description:")
        print(f"   {result['ai_detailed_description']}")
        
        print(f"\n🏷️ AI Topics:")
        for i, topic in enumerate(result['ai_topics'], 1):
            print(f"   {i}. {topic}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_ai_direct())