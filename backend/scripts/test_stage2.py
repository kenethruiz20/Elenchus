#!/usr/bin/env python3
"""
Stage 2 Implementation Test Script
Tests Data Models & Database Setup functionality.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import mongodb_manager, qdrant_manager
from app.models.rag_document import RAGDocument, DocumentType, DocumentStatus, DocumentMetadata
from app.models.rag_chunk import RAGChunk, ChunkType, ChunkMetadata
from app.models.rag_session import RAGSession, SessionType, MessageRole, MessageMetadata
from app.schemas.rag_schemas import DocumentUploadRequest, SearchRequest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_database_connections():
    """Test database connections and initialization."""
    print("🔗 Testing Database Connections")
    print("-" * 40)
    
    try:
        # Test MongoDB
        await mongodb_manager.initialize()
        mongo_ping = await mongodb_manager.ping()
        print(f"MongoDB: {'✅ Connected' if mongo_ping else '❌ Failed'}")
        
        # Test Qdrant
        await qdrant_manager.initialize()
        qdrant_health = await qdrant_manager.health_check()
        qdrant_ok = qdrant_health["status"] == "healthy"
        print(f"Qdrant: {'✅ Connected' if qdrant_ok else '❌ Failed'}")
        
        return mongo_ping and qdrant_ok
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False


async def test_rag_document_model():
    """Test RAG Document model operations."""
    print("\n📄 Testing RAG Document Model")
    print("-" * 40)
    
    try:
        # Create a test document
        test_doc = RAGDocument(
            user_id="test_user_stage2",
            filename="test_document.pdf",
            original_filename="Test Document.pdf",
            file_type=DocumentType.PDF,
            file_size=1024000,
            file_hash="test_hash_stage2_doc",
            metadata=DocumentMetadata(
                title="Test Legal Document",
                author="Test Author",
                page_count=10,
                word_count=5000
            ),
            tags=["test", "stage2"],
            category="legal"
        )
        
        # Insert document
        await test_doc.insert()
        print(f"✅ Document created with ID: {test_doc.id}")
        
        # Test status updates
        await test_doc.mark_processing_started("job_123")
        print("✅ Document marked as processing started")
        
        # Test completion
        from app.models.rag_document import ProcessingMetrics
        metrics = ProcessingMetrics(
            chunks_created=25,
            processing_time_seconds=45.5,
            embedding_time_seconds=12.3
        )
        await test_doc.mark_processing_completed(25, metrics)
        print("✅ Document marked as processing completed")
        
        # Test queries
        user_docs = await RAGDocument.find_user_documents("test_user_stage2", limit=10)
        print(f"✅ Found {len(user_docs)} user documents")
        
        completed_docs = await RAGDocument.find_by_user_and_status("test_user_stage2", DocumentStatus.COMPLETED)
        print(f"✅ Found {len(completed_docs)} completed documents")
        
        # Test hash lookup
        hash_doc = await RAGDocument.find_by_hash("test_hash_stage2_doc")
        print(f"✅ Found document by hash: {hash_doc.id if hash_doc else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document model test failed: {str(e)}")
        return False


async def test_rag_chunk_model():
    """Test RAG Chunk model operations."""
    print("\n📝 Testing RAG Chunk Model")
    print("-" * 40)
    
    try:
        # Get the test document
        test_doc = await RAGDocument.find_one(RAGDocument.user_id == "test_user_stage2")
        if not test_doc:
            raise Exception("Test document not found")
        
        document_id = str(test_doc.id)
        
        # Create test chunks
        chunks_data = [
            ("This is the first chunk of the legal document.", 1, 1),
            ("This chunk contains important contract terms.", 1, 2),
            ("The final chunk discusses legal implications.", 2, 3),
        ]
        
        created_chunks = []
        for text, page, index in chunks_data:
            chunk = RAGChunk(
                document_id=document_id,
                user_id="test_user_stage2",
                chunk_index=index,
                chunk_id=f"{document_id}_{index}",
                text=text,
                text_hash=f"hash_{index}_stage2",
                metadata=ChunkMetadata(
                    page_number=page,
                    word_count=len(text.split()),
                    char_count=len(text),
                    sentence_count=1
                )
            )
            
            # Calculate quality metrics
            chunk.calculate_quality_metrics()
            
            await chunk.insert()
            created_chunks.append(chunk)
            print(f"✅ Created chunk {index} with quality score: {chunk.processing_quality_score:.2f}")
        
        # Test queries
        doc_chunks = await RAGChunk.find_by_document(document_id, "test_user_stage2")
        print(f"✅ Found {len(doc_chunks)} chunks for document")
        
        page_chunks = await RAGChunk.find_chunks_by_page(document_id, 1, "test_user_stage2")
        print(f"✅ Found {len(page_chunks)} chunks for page 1")
        
        chunk_count = await RAGChunk.count_by_document(document_id, "test_user_stage2")
        print(f"✅ Document has {chunk_count} total chunks")
        
        # Test embedding marking
        test_chunk = created_chunks[0]
        await test_chunk.mark_embedding_created("qdrant_point_123", "sentence-transformers/all-MiniLM-L6-v2")
        print("✅ Chunk marked with embedding created")
        
        return True
        
    except Exception as e:
        print(f"❌ Chunk model test failed: {str(e)}")
        return False


async def test_rag_session_model():
    """Test RAG Session model operations."""
    print("\n💬 Testing RAG Session Model")
    print("-" * 40)
    
    try:
        # Create a test session
        test_session = RAGSession(
            user_id="test_user_stage2",
            session_title="Stage 2 Test Session",
            session_type=SessionType.RESEARCH,
            tags=["test", "stage2", "research"]
        )
        
        await test_session.insert()
        print(f"✅ Session created with ID: {test_session.id}")
        
        # Add some messages
        user_msg_id = await test_session.add_message(
            MessageRole.USER,
            "What are the key terms in the contract?",
            metadata=MessageMetadata(tokens_used=15, processing_time_ms=100.0)
        )
        print(f"✅ Added user message: {user_msg_id}")
        
        assistant_msg_id = await test_session.add_message(
            MessageRole.ASSISTANT,
            "Based on the document analysis, the key terms include...",
            metadata=MessageMetadata(
                tokens_used=45, 
                processing_time_ms=1200.0,
                confidence_score=0.85
            )
        )
        print(f"✅ Added assistant message: {assistant_msg_id}")
        
        # Test document references
        test_doc = await RAGDocument.find_one(RAGDocument.user_id == "test_user_stage2")
        if test_doc:
            await test_session.add_document_reference(str(test_doc.id))
            print("✅ Added document reference to session")
        
        # Test feedback
        await test_session.update_message_feedback(assistant_msg_id, 4, "Good response")
        print("✅ Updated message feedback")
        
        # Test queries
        user_sessions = await RAGSession.find_user_sessions(
            "test_user_stage2", 
            session_type=SessionType.RESEARCH
        )
        print(f"✅ Found {len(user_sessions)} user research sessions")
        
        # Test context messages
        context_msgs = test_session.get_context_messages(5)
        print(f"✅ Retrieved {len(context_msgs)} context messages")
        
        # Test conversation summary
        summary = test_session.get_conversation_summary()
        print(f"✅ Session summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Session model test failed: {str(e)}")
        return False


async def test_database_indexes():
    """Test database index creation and performance."""
    print("\n📊 Testing Database Indexes")
    print("-" * 40)
    
    try:
        # Run index creation script
        from scripts.create_indexes import create_rag_document_indexes, create_rag_chunk_indexes, create_rag_session_indexes
        
        doc_indexes = await create_rag_document_indexes()
        chunk_indexes = await create_rag_chunk_indexes()
        session_indexes = await create_rag_session_indexes()
        
        print(f"✅ Created indexes: {doc_indexes + chunk_indexes + session_indexes} total")
        
        # Test index usage with explain
        collection = mongodb_manager.database.rag_documents
        explain = await collection.find({"user_id": "test_user_stage2"}).explain()
        
        winning_plan = explain.get("executionStats", {}).get("executionStages", {})
        stage = winning_plan.get("stage", "unknown")
        
        if "IXSCAN" in stage:
            print("✅ Queries using indexes efficiently")
        else:
            print(f"⚠️  Query execution stage: {stage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Index test failed: {str(e)}")
        return False


async def test_qdrant_operations():
    """Test Qdrant vector database operations."""
    print("\n🔍 Testing Qdrant Operations")
    print("-" * 40)
    
    try:
        # Test collection info
        collection_info = await qdrant_manager.get_collection_info()
        if collection_info:
            print(f"✅ Collection '{collection_info.name}' exists")
            print(f"   Points: {collection_info.points_count}")
            print(f"   Vectors: {collection_info.vectors_count}")
        else:
            print("❌ Could not get collection info")
            return False
        
        # Test vector operations
        from qdrant_client.models import PointStruct
        import random
        
        # Create test points
        test_points = []
        for i in range(3):
            vector = [random.random() for _ in range(384)]  # Match embedding dimension
            point = PointStruct(
                id=f"test_point_{i}_stage2",
                vector=vector,
                payload={
                    "user_id": "test_user_stage2",
                    "document_id": "test_doc_id",
                    "chunk_id": f"chunk_{i}",
                    "text": f"This is test chunk number {i} for Stage 2 testing."
                }
            )
            test_points.append(point)
        
        # Upsert points
        success = await qdrant_manager.upsert_points(test_points)
        if success:
            print(f"✅ Upserted {len(test_points)} test points")
        else:
            print("❌ Failed to upsert points")
            return False
        
        # Test search
        query_vector = [random.random() for _ in range(384)]
        results = await qdrant_manager.search_similar(
            query_vector=query_vector,
            user_id="test_user_stage2",
            limit=5
        )
        
        print(f"✅ Search returned {len(results)} results")
        if results:
            print(f"   Best match score: {results[0].score:.4f}")
        
        # Test user statistics
        user_stats = await qdrant_manager.get_user_statistics("test_user_stage2")
        if "error" not in user_stats:
            print(f"✅ User statistics: {user_stats['points_count']} points")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant operations test failed: {str(e)}")
        return False


async def test_schema_validation():
    """Test Pydantic schema validation."""
    print("\n📋 Testing Schema Validation")
    print("-" * 40)
    
    try:
        # Test document upload schema
        doc_request = DocumentUploadRequest(
            filename="test.pdf",
            file_type=DocumentType.PDF,
            tags=["legal", "contract", "TEST"],  # Mixed case
            category="contracts",
            metadata={"custom_field": "value"}
        )
        
        print(f"✅ Document request validated: {doc_request.filename}")
        print(f"   Tags cleaned: {doc_request.tags}")
        
        # Test search request schema
        search_request = SearchRequest(
            query="contract terms and conditions",
            document_ids=["doc1", "doc2"],
            top_k=10,
            score_threshold=0.5
        )
        
        print(f"✅ Search request validated: '{search_request.query[:30]}...'")
        print(f"   Top K: {search_request.top_k}")
        print(f"   Threshold: {search_request.score_threshold}")
        
        # Test invalid schema
        try:
            invalid_request = DocumentUploadRequest(
                filename="",  # Invalid empty filename
                file_type=DocumentType.PDF
            )
            print("❌ Schema validation should have failed")
            return False
        except Exception as validation_error:
            print("✅ Schema validation correctly rejected invalid input")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation test failed: {str(e)}")
        return False


async def cleanup_test_data():
    """Clean up test data created during testing."""
    print("\n🧹 Cleaning Up Test Data")
    print("-" * 40)
    
    try:
        # Delete test chunks
        deleted_chunks = await RAGChunk.find(
            RAGChunk.user_id == "test_user_stage2"
        ).delete()
        print(f"✅ Deleted {deleted_chunks.deleted_count} test chunks")
        
        # Delete test documents
        deleted_docs = await RAGDocument.find(
            RAGDocument.user_id == "test_user_stage2"
        ).delete()
        print(f"✅ Deleted {deleted_docs.deleted_count} test documents")
        
        # Delete test sessions
        deleted_sessions = await RAGSession.find(
            RAGSession.user_id == "test_user_stage2"
        ).delete()
        print(f"✅ Deleted {deleted_sessions.deleted_count} test sessions")
        
        # Delete test points from Qdrant
        await qdrant_manager.delete_points_by_filter("test_user_stage2")
        print("✅ Deleted test points from Qdrant")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🧪 Stage 2: Data Models & Database Setup Tests")
    print("=" * 60)
    
    tests = [
        ("Database Connections", test_database_connections()),
        ("RAG Document Model", test_rag_document_model()),
        ("RAG Chunk Model", test_rag_chunk_model()),
        ("RAG Session Model", test_rag_session_model()),
        ("Database Indexes", test_database_indexes()),
        ("Qdrant Operations", test_qdrant_operations()),
        ("Schema Validation", test_schema_validation()),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_coro in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = await test_coro
            if result:
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    # Cleanup
    print("\n" + "=" * 60)
    await cleanup_test_data()
    
    # Results
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All Stage 2 tests passed! Data Models & Database Setup is complete.")
        print("\n🎯 Ready for Stage 3: Authentication & Security")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)