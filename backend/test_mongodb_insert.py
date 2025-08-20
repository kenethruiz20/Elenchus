#!/usr/bin/env python3
"""
Test MongoDB insertion to isolate the language field issue.
"""

import asyncio
from app.models.rag_chunk import RAGChunk, ChunkType, ChunkMetadata
from app.database import mongodb_manager

async def test_chunk_insertion():
    """Test inserting a chunk to see if it fails."""
    
    await mongodb_manager.initialize()
    
    try:
        # Create a simple chunk without any language field
        chunk = RAGChunk(
            document_id="test_doc_id",
            user_id="test_user_id",
            chunk_index=0,
            chunk_id="test_chunk_0",
            text="This is a test chunk for MongoDB insertion testing.",
            text_hash="test_hash_123",
            chunk_type=ChunkType.TEXT,
            metadata=ChunkMetadata(
                page_number=1,
                word_count=10,
                char_count=50,
                sentence_count=1
            )
        )
        
        print("Attempting to insert chunk...")
        await chunk.insert()
        print("✅ Chunk inserted successfully")
        
        # Clean up
        await chunk.delete()
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Chunk insertion failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chunk_insertion())