#!/usr/bin/env python3
"""
Remove the language field from existing documents to fix MongoDB text index conflicts.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def remove_language_fields():
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://elenchus_admin:elenchus_password_2024@localhost:27018/elenchus?authSource=admin")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.elenchus
    
    try:
        # Remove language field from rag_documents
        print("Removing language field from rag_documents...")
        result = await db.rag_documents.update_many(
            {"metadata.language": {"$exists": True}},
            {"$unset": {"metadata.language": ""}}
        )
        print(f"✅ Updated {result.modified_count} documents")
        
        # Remove language field from rag_chunks
        print("Removing language field from rag_chunks...")
        result = await db.rag_chunks.update_many(
            {"metadata.language": {"$exists": True}},
            {"$unset": {"metadata.language": ""}}
        )
        print(f"✅ Updated {result.modified_count} chunks")
        
        # Check remaining documents with language field
        remaining_docs = await db.rag_documents.count_documents({"metadata.language": {"$exists": True}})
        remaining_chunks = await db.rag_chunks.count_documents({"metadata.language": {"$exists": True}})
        
        print(f"\nRemaining documents with language field: {remaining_docs}")
        print(f"Remaining chunks with language field: {remaining_chunks}")
        
        print("\n✅ Language field cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(remove_language_fields())