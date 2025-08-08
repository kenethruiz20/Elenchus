#!/usr/bin/env python3
"""
Test script for RAG stack setup and connectivity.
Validates all components are working correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.rag_service import rag_service
from app.services.document_processor import document_processor
from app.services.rag_worker import rag_worker
from app.config.settings import settings


async def test_rag_service_initialization():
    """Test RAG service initialization."""
    print("🔧 Testing RAG Service Initialization...")
    
    try:
        await rag_service.initialize()
        print("✅ RAG service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ RAG service initialization failed: {str(e)}")
        return False


async def test_qdrant_connectivity():
    """Test Qdrant connection and collection."""
    print("🗃️  Testing Qdrant Connectivity...")
    
    try:
        if not rag_service._initialized:
            await rag_service.initialize()
        
        # Test basic connection
        collections = rag_service.qdrant_client.get_collections()
        print(f"✅ Connected to Qdrant, found {len(collections.collections)} collections")
        
        # Check if our collection exists
        collection_names = [col.name for col in collections.collections]
        if settings.QDRANT_COLLECTION_NAME in collection_names:
            print(f"✅ Collection '{settings.QDRANT_COLLECTION_NAME}' exists")
        else:
            print(f"⚠️  Collection '{settings.QDRANT_COLLECTION_NAME}' not found")
        
        return True
    except Exception as e:
        print(f"❌ Qdrant connectivity test failed: {str(e)}")
        return False


def test_embedding_model():
    """Test embedding model loading and generation."""
    print("🧠 Testing Embedding Model...")
    
    try:
        if not rag_service._initialized:
            print("❌ RAG service not initialized, cannot test embeddings")
            return False
        
        # Test embedding generation
        test_texts = ["This is a legal document.", "Contract law analysis."]
        embeddings = rag_service.generate_embeddings(test_texts)
        
        print(f"✅ Generated embeddings for {len(test_texts)} texts")
        print(f"✅ Embedding dimension: {len(embeddings[0])}")
        print(f"✅ Expected dimension: {settings.EMBED_DIMENSION}")
        
        if len(embeddings[0]) == settings.EMBED_DIMENSION:
            print("✅ Embedding dimensions match configuration")
            return True
        else:
            print("⚠️  Embedding dimensions don't match configuration")
            return False
            
    except Exception as e:
        print(f"❌ Embedding model test failed: {str(e)}")
        return False


def test_document_processor():
    """Test document processing capabilities."""
    print("📄 Testing Document Processor...")
    
    try:
        # Test with sample text
        sample_text = """
        This is a sample legal document for testing purposes.
        It contains multiple sentences and paragraphs to test chunking functionality.
        
        The document processor should be able to extract this text and create meaningful chunks.
        Each chunk should be properly sized according to the configuration settings.
        """
        
        # Test text extraction
        text_content = [{
            "page": 1,
            "text": sample_text
        }]
        
        # Test chunking
        chunks = document_processor.create_chunks(text_content)
        
        print(f"✅ Created {len(chunks)} chunks from sample text")
        
        # Test validation
        sample_bytes = sample_text.encode('utf-8')
        validation = document_processor.validate_document(sample_bytes, "test.txt")
        
        if validation["valid"]:
            print("✅ Document validation working")
        else:
            print(f"❌ Document validation failed: {validation['errors']}")
        
        return len(chunks) > 0 and validation["valid"]
        
    except Exception as e:
        print(f"❌ Document processor test failed: {str(e)}")
        return False


def test_redis_connectivity():
    """Test Redis connectivity for background workers."""
    print("🔄 Testing Redis Connectivity...")
    
    try:
        # Test Redis connection
        import redis
        redis_conn = redis.from_url(settings.RQ_REDIS_URL)
        redis_conn.ping()
        
        print("✅ Redis connection successful")
        
        # Test queue info
        queue_info = rag_worker.get_queue_info()
        if "error" not in queue_info:
            print(f"✅ Task queue accessible: {queue_info['queue_name']}")
            print(f"   - Queued jobs: {queue_info['jobs_queued']}")
            print(f"   - Started jobs: {queue_info['jobs_started']}")
            print(f"   - Finished jobs: {queue_info['jobs_finished']}")
            print(f"   - Failed jobs: {queue_info['jobs_failed']}")
            return True
        else:
            print(f"❌ Queue access failed: {queue_info['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Redis connectivity test failed: {str(e)}")
        return False


async def test_gcs_connectivity():
    """Test Google Cloud Storage connectivity."""
    print("☁️  Testing GCS Connectivity...")
    
    try:
        if not rag_service._initialized:
            await rag_service.initialize()
        
        if not rag_service.gcs_client:
            print("⚠️  GCS client not initialized (credentials may be missing)")
            return False
        
        # Test bucket access
        bucket = rag_service.gcs_client.bucket(settings.GCP_BUCKET)
        exists = bucket.exists()
        
        if exists:
            print(f"✅ GCS bucket '{settings.GCP_BUCKET}' accessible")
            return True
        else:
            print(f"⚠️  GCS bucket '{settings.GCP_BUCKET}' not accessible or doesn't exist")
            return False
            
    except Exception as e:
        print(f"❌ GCS connectivity test failed: {str(e)}")
        return False


async def test_end_to_end_workflow():
    """Test complete RAG workflow."""
    print("🔄 Testing End-to-End Workflow...")
    
    try:
        if not rag_service._initialized:
            await rag_service.initialize()
        
        # Test document processing and storage
        test_text = "This is a test legal document for end-to-end workflow testing."
        test_chunks = document_processor.create_chunks([{"page": 1, "text": test_text}])
        
        # Store chunks
        success = await rag_service.store_document_chunks("test_doc_123", test_chunks, "test_user_456")
        
        if success:
            print("✅ Document chunks stored successfully")
        else:
            print("❌ Failed to store document chunks")
            return False
        
        # Test search
        search_results = await rag_service.search_similar_chunks("legal document", "test_user_456", top_k=3)
        
        if search_results:
            print(f"✅ Search returned {len(search_results)} results")
        else:
            print("⚠️  Search returned no results")
        
        # Cleanup
        await rag_service.delete_document_chunks("test_doc_123")
        print("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {str(e)}")
        return False


async def main():
    """Run all RAG setup tests."""
    print("🚀 Starting RAG Stack Setup Tests")
    print("=" * 50)
    
    tests = [
        ("RAG Service Initialization", test_rag_service_initialization()),
        ("Qdrant Connectivity", test_qdrant_connectivity()),
        ("Embedding Model", test_embedding_model),
        ("Document Processor", test_document_processor),
        ("Redis Connectivity", test_redis_connectivity),
        ("GCS Connectivity", test_gcs_connectivity()),
        ("End-to-End Workflow", test_end_to_end_workflow()),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        
        if asyncio.iscoroutine(test_func):
            result = await test_func
        else:
            result = test_func()
        
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RAG stack is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)