#!/usr/bin/env python3
"""
Database Index Creation Script
Creates optimized indexes for RAG system performance.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import mongodb_manager
import pymongo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_rag_document_indexes():
    """Create optimized indexes for RAG documents collection."""
    print("📋 Creating RAG Documents indexes...")
    
    collection = mongodb_manager.database.rag_documents
    
    indexes = [
        # Primary query patterns
        ([("user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)], 
         {"name": "user_status_created_idx"}),
        
        # File deduplication
        ([("file_hash", pymongo.ASCENDING)], 
         {"name": "file_hash_idx", "unique": True}),
        
        # Processing jobs
        ([("processing_job_id", pymongo.ASCENDING)], 
         {"name": "job_id_idx", "sparse": True}),
        
        # User + file type queries
        ([("user_id", pymongo.ASCENDING), ("file_type", pymongo.ASCENDING)], 
         {"name": "user_filetype_idx"}),
        
        # GCS path lookups
        ([("gcs_path", pymongo.ASCENDING)], 
         {"name": "gcs_path_idx", "sparse": True}),
        
        # Embeddings status
        ([("user_id", pymongo.ASCENDING), ("embeddings_created", pymongo.ASCENDING), ("updated_at", pymongo.DESCENDING)], 
         {"name": "user_embeddings_updated_idx"}),
        
        # Text search on filename and title
        ([("filename", pymongo.TEXT), ("metadata.title", pymongo.TEXT)], 
         {"name": "text_search_idx"}),
        
        # TTL index for failed documents (cleanup after 30 days)
        ([("updated_at", pymongo.ASCENDING)], 
         {"name": "failed_docs_ttl_idx", "expireAfterSeconds": 30*24*60*60, 
          "partialFilterExpression": {"status": "failed"}}),
    ]
    
    created_count = 0
    for index_spec, options in indexes:
        try:
            await collection.create_index(index_spec, background=True, **options)
            print(f"✅ Created index: {options['name']}")
            created_count += 1
        except Exception as e:
            if "already exists" in str(e) or "IndexOptionsConflict" in str(e):
                print(f"ℹ️  Index already exists: {options['name']}")
            else:
                print(f"❌ Failed to create {options['name']}: {str(e)}")
    
    print(f"📊 RAG Documents: {created_count} new indexes created")
    return created_count


async def create_rag_chunk_indexes():
    """Create optimized indexes for RAG chunks collection."""
    print("📋 Creating RAG Chunks indexes...")
    
    collection = mongodb_manager.database.rag_chunks
    
    indexes = [
        # Document relationship
        ([("document_id", pymongo.ASCENDING), ("chunk_index", pymongo.ASCENDING)], 
         {"name": "document_chunk_idx"}),
        
        # User isolation with document
        ([("user_id", pymongo.ASCENDING), ("document_id", pymongo.ASCENDING)], 
         {"name": "user_document_idx"}),
        
        # Text deduplication
        ([("text_hash", pymongo.ASCENDING)], 
         {"name": "text_hash_idx"}),
        
        # Qdrant point mapping
        ([("qdrant_point_id", pymongo.ASCENDING)], 
         {"name": "qdrant_point_idx", "unique": True, "sparse": True}),
        
        # User + chunk type
        ([("user_id", pymongo.ASCENDING), ("chunk_type", pymongo.ASCENDING)], 
         {"name": "user_chunktype_idx"}),
        
        # Page-based queries
        ([("document_id", pymongo.ASCENDING), ("metadata.page_number", pymongo.ASCENDING), ("chunk_index", pymongo.ASCENDING)], 
         {"name": "document_page_chunk_idx"}),
        
        # Text search
        ([("text", pymongo.TEXT), ("metadata.section_title", pymongo.TEXT)], 
         {"name": "chunk_text_search_idx"}),
        
        # Quality metrics
        ([("user_id", pymongo.ASCENDING), ("processing_quality_score", pymongo.ASCENDING)], 
         {"name": "user_quality_idx", "sparse": True}),
        
        # Reprocessing needed
        ([("reprocessing_needed", pymongo.ASCENDING), ("updated_at", pymongo.ASCENDING)], 
         {"name": "reprocessing_idx", "partialFilterExpression": {"reprocessing_needed": True}}),
        
        # Created date for cleanup
        ([("created_at", pymongo.DESCENDING)], 
         {"name": "created_date_idx"}),
    ]
    
    created_count = 0
    for index_spec, options in indexes:
        try:
            await collection.create_index(index_spec, background=True, **options)
            print(f"✅ Created index: {options['name']}")
            created_count += 1
        except Exception as e:
            if "already exists" in str(e) or "IndexOptionsConflict" in str(e):
                print(f"ℹ️  Index already exists: {options['name']}")
            else:
                print(f"❌ Failed to create {options['name']}: {str(e)}")
    
    print(f"📊 RAG Chunks: {created_count} new indexes created")
    return created_count


async def create_rag_session_indexes():
    """Create optimized indexes for RAG sessions collection."""
    print("📋 Creating RAG Sessions indexes...")
    
    collection = mongodb_manager.database.rag_sessions
    
    indexes = [
        # Active sessions by user
        ([("user_id", pymongo.ASCENDING), ("is_active", pymongo.ASCENDING), ("last_activity", pymongo.DESCENDING)], 
         {"name": "user_active_activity_idx"}),
        
        # Sessions by type
        ([("user_id", pymongo.ASCENDING), ("session_type", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)], 
         {"name": "user_type_created_idx"}),
        
        # Shared sessions
        ([("is_shared", pymongo.ASCENDING), ("updated_at", pymongo.DESCENDING)], 
         {"name": "shared_updated_idx"}),
        
        # Shared with specific users
        ([("shared_with", pymongo.ASCENDING), ("is_shared", pymongo.ASCENDING)], 
         {"name": "shared_with_idx"}),
        
        # Tag-based queries
        ([("tags", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING)], 
         {"name": "tags_user_idx"}),
        
        # Folder organization
        ([("folder", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING), ("updated_at", pymongo.DESCENDING)], 
         {"name": "folder_user_updated_idx"}),
        
        # Document references
        ([("referenced_document_ids", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING)], 
         {"name": "docs_user_idx"}),
        
        # Favorites
        ([("user_id", pymongo.ASCENDING), ("is_favorite", pymongo.ASCENDING), ("last_activity", pymongo.DESCENDING)], 
         {"name": "user_favorite_activity_idx"}),
        
        # Text search
        ([("session_title", pymongo.TEXT), ("messages.content", pymongo.TEXT)], 
         {"name": "session_text_search_idx"}),
        
        # Archived sessions cleanup (TTL after 1 year)
        ([("updated_at", pymongo.ASCENDING)], 
         {"name": "archived_sessions_ttl_idx", "expireAfterSeconds": 365*24*60*60,
          "partialFilterExpression": {"is_archived": True, "is_favorite": False}}),
    ]
    
    created_count = 0
    for index_spec, options in indexes:
        try:
            await collection.create_index(index_spec, background=True, **options)
            print(f"✅ Created index: {options['name']}")
            created_count += 1
        except Exception as e:
            if "already exists" in str(e) or "IndexOptionsConflict" in str(e):
                print(f"ℹ️  Index already exists: {options['name']}")
            else:
                print(f"❌ Failed to create {options['name']}: {str(e)}")
    
    print(f"📊 RAG Sessions: {created_count} new indexes created")
    return created_count


async def optimize_existing_collections():
    """Optimize existing collections with additional indexes."""
    print("📋 Creating additional indexes for existing collections...")
    
    created_count = 0
    
    # Users collection
    try:
        users_collection = mongodb_manager.database.users
        await users_collection.create_index([("email", pymongo.ASCENDING)], unique=True, background=True)
        await users_collection.create_index([("created_at", pymongo.DESCENDING)], background=True)
        print("✅ Enhanced users collection indexes")
        created_count += 2
    except Exception as e:
        print(f"ℹ️  Users indexes may already exist: {str(e)}")
    
    # Research sessions collection
    try:
        research_collection = mongodb_manager.database.research_sessions
        await research_collection.create_index([("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)], background=True)
        await research_collection.create_index([("type", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING)], background=True)
        print("✅ Enhanced research sessions indexes")
        created_count += 2
    except Exception as e:
        print(f"ℹ️  Research sessions indexes may already exist: {str(e)}")
    
    # Messages collection
    try:
        messages_collection = mongodb_manager.database.messages
        await messages_collection.create_index([("research_id", pymongo.ASCENDING), ("timestamp", pymongo.ASCENDING)], background=True)
        await messages_collection.create_index([("user_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)], background=True)
        print("✅ Enhanced messages collection indexes")
        created_count += 2
    except Exception as e:
        print(f"ℹ️  Messages indexes may already exist: {str(e)}")
    
    print(f"📊 Existing Collections: {created_count} additional indexes created")
    return created_count


async def analyze_index_usage():
    """Analyze index usage and provide recommendations."""
    print("📊 Analyzing index usage...")
    
    try:
        collections = ["rag_documents", "rag_chunks", "rag_sessions", "users"]
        
        for collection_name in collections:
            collection = mongodb_manager.database[collection_name]
            
            # Get index stats
            index_stats = await collection.index_stats().to_list(None)
            
            if index_stats:
                print(f"\n📈 {collection_name} Index Usage:")
                for stat in index_stats:
                    name = stat.get("name", "unknown")
                    accesses = stat.get("accesses", {})
                    ops = accesses.get("ops", 0)
                    since = accesses.get("since", "unknown")
                    
                    print(f"   {name}: {ops} operations (since {since})")
            else:
                print(f"\n📈 {collection_name}: No usage statistics available")
        
    except Exception as e:
        print(f"⚠️  Index analysis failed: {str(e)}")


async def main():
    """Main index creation function."""
    print("🚀 Database Index Creation")
    print("=" * 50)
    
    # Initialize database connection
    try:
        await mongodb_manager.initialize()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return 1
    
    total_created = 0
    
    # Create RAG-specific indexes
    total_created += await create_rag_document_indexes()
    total_created += await create_rag_chunk_indexes()
    total_created += await create_rag_session_indexes()
    
    # Optimize existing collections
    total_created += await optimize_existing_collections()
    
    # Analyze index usage
    await analyze_index_usage()
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Index Creation Summary")
    print(f"Total new indexes created: {total_created}")
    
    if total_created > 0:
        print("✅ Index creation completed successfully!")
        print("\n💡 Recommendations:")
        print("- Monitor index usage over time")
        print("- Consider dropping unused indexes")
        print("- Run this script periodically to ensure optimal performance")
    else:
        print("ℹ️  All indexes already exist or creation skipped")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)