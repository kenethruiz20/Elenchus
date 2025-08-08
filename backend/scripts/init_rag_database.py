#!/usr/bin/env python3
"""
RAG Database Initialization Script
Initializes MongoDB and Qdrant databases for the RAG system.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import mongodb_manager, qdrant_manager
from app.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_mongodb():
    """Initialize MongoDB with all collections and indexes."""
    print("🔧 Initializing MongoDB...")
    
    try:
        await mongodb_manager.initialize()
        
        # Test connection
        if await mongodb_manager.ping():
            print("✅ MongoDB connection successful")
        else:
            raise Exception("MongoDB ping failed")
        
        # Get database stats
        stats = await mongodb_manager.get_database_stats()
        print(f"📊 Database: {stats['database_name']}")
        print(f"   Collections: {stats['collections']}")
        print(f"   Data Size: {stats['data_size']:,} bytes")
        print(f"   Storage Size: {stats['storage_size']:,} bytes")
        print(f"   Index Size: {stats['index_size']:,} bytes")
        
        # Document counts
        print("📋 Document Counts:")
        for collection, count in stats.get('documents', {}).items():
            print(f"   {collection}: {count:,} documents")
        
        return True
        
    except Exception as e:
        logger.error(f"MongoDB initialization failed: {str(e)}")
        return False


async def initialize_qdrant():
    """Initialize Qdrant vector database."""
    print("\n🔧 Initializing Qdrant...")
    
    try:
        await qdrant_manager.initialize()
        
        # Get health status
        health = await qdrant_manager.health_check()
        if health["status"] == "healthy":
            print("✅ Qdrant connection successful")
            print(f"📊 Collections: {health['total_collections']}")
            
            # Main collection info
            main_col = health["main_collection"]
            print(f"🗃️  Main Collection: {main_col['name']}")
            print(f"   Exists: {main_col['exists']}")
            print(f"   Points: {main_col['points_count']:,}")
            print(f"   Vectors: {main_col['vectors_count']:,}")
            print(f"   Segments: {main_col['segments_count']}")
            
            if main_col['config']:
                config = main_col['config']
                print(f"   Vector Size: {config['vector_size']}")
                print(f"   Distance: {config['distance']}")
        else:
            raise Exception(f"Qdrant health check failed: {health}")
        
        return True
        
    except Exception as e:
        logger.error(f"Qdrant initialization failed: {str(e)}")
        return False


async def create_sample_data():
    """Create sample data for testing (optional)."""
    print("\n📝 Creating sample data...")
    
    try:
        from app.models.rag_document import RAGDocument, DocumentType, DocumentStatus
        from app.models.rag_session import RAGSession, SessionType
        
        # Check if sample data already exists
        existing_docs = await RAGDocument.find(RAGDocument.filename == "sample_legal_doc.pdf").count()
        
        if existing_docs == 0:
            # Create a sample document
            sample_doc = RAGDocument(
                user_id="sample_user_123",
                filename="sample_legal_doc.pdf",
                original_filename="Sample Legal Document.pdf",
                file_type=DocumentType.PDF,
                file_size=1024000,
                file_hash="sample_hash_123",
                status=DocumentStatus.COMPLETED,
                tags=["contract", "sample"],
                category="legal"
            )
            await sample_doc.insert()
            print("✅ Sample document created")
            
            # Create a sample session
            sample_session = RAGSession(
                user_id="sample_user_123",
                session_title="Sample Legal Research Session",
                session_type=SessionType.RESEARCH,
                tags=["sample", "demo"]
            )
            await sample_session.insert()
            print("✅ Sample session created")
            
            print(f"📋 Sample Data Created:")
            print(f"   Document ID: {sample_doc.id}")
            print(f"   Session ID: {sample_session.id}")
        else:
            print("ℹ️  Sample data already exists, skipping creation")
        
        return True
        
    except Exception as e:
        logger.error(f"Sample data creation failed: {str(e)}")
        return False


async def verify_system():
    """Verify that the RAG system is properly set up."""
    print("\n🔍 Verifying RAG system setup...")
    
    try:
        # Test MongoDB operations
        from app.models.rag_document import RAGDocument
        doc_count = await RAGDocument.find().count()
        print(f"✅ MongoDB: {doc_count} RAG documents found")
        
        # Test Qdrant operations
        collection_info = await qdrant_manager.get_collection_info()
        if collection_info:
            print(f"✅ Qdrant: Collection '{collection_info.name}' ready")
            print(f"   Points: {collection_info.points_count}")
        else:
            print("⚠️  Qdrant: Could not get collection info")
        
        # Test database managers
        mongo_stats = await mongodb_manager.get_database_stats()
        qdrant_health = await qdrant_manager.health_check()
        
        if mongo_stats.get("ok") and qdrant_health["status"] == "healthy":
            print("✅ All systems operational")
            return True
        else:
            print("⚠️  Some systems may have issues")
            return False
        
    except Exception as e:
        logger.error(f"System verification failed: {str(e)}")
        return False


async def cleanup_test_data():
    """Clean up any test data (optional)."""
    print("\n🧹 Cleaning up test data...")
    
    try:
        from app.models.rag_document import RAGDocument
        from app.models.rag_session import RAGSession
        
        # Delete sample documents
        deleted_docs = await RAGDocument.find(
            RAGDocument.user_id == "sample_user_123"
        ).delete()
        
        # Delete sample sessions
        deleted_sessions = await RAGSession.find(
            RAGSession.user_id == "sample_user_123"
        ).delete()
        
        print(f"🗑️  Cleaned up {deleted_docs.deleted_count} documents and {deleted_sessions.deleted_count} sessions")
        
        return True
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return False


async def main():
    """Main initialization function."""
    print("🚀 RAG Database Initialization")
    print("=" * 50)
    
    print(f"📋 Configuration:")
    print(f"   MongoDB URL: {settings.MONGODB_URL}")
    print(f"   MongoDB Database: {settings.MONGODB_DATABASE}")
    print(f"   Qdrant URL: {settings.QDRANT_URL}")
    print(f"   Qdrant Collection: {settings.QDRANT_COLLECTION_NAME}")
    print(f"   Vector Dimension: {settings.EMBED_DIMENSION}")
    
    success_count = 0
    total_steps = 4
    
    # Initialize MongoDB
    if await initialize_mongodb():
        success_count += 1
    
    # Initialize Qdrant
    if await initialize_qdrant():
        success_count += 1
    
    # Create sample data (optional)
    if await create_sample_data():
        success_count += 1
    
    # Verify system
    if await verify_system():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Initialization Summary: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("🎉 RAG database initialization completed successfully!")
        print("\n🎯 Next Steps:")
        print("1. Run the RAG setup test: python scripts/test_rag_setup.py")
        print("2. Start the development environment: ./devrun.sh")
        print("3. Test document upload and processing")
        return 0
    else:
        print("⚠️  Some initialization steps failed. Please check the logs.")
        return 1


if __name__ == "__main__":
    # Command line options
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize RAG database system")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test data")
    parser.add_argument("--no-sample", action="store_true", help="Skip sample data creation")
    
    args = parser.parse_args()
    
    if args.cleanup:
        asyncio.run(cleanup_test_data())
    else:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)