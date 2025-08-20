#!/usr/bin/env python3
"""
Fix MongoDB text index that's causing language override field error.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_indexes():
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://elenchus_admin:elenchus_password_2024@localhost:27018/elenchus?authSource=admin")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.elenchus
    collection = db.rag_documents
    
    try:
        # List all indexes
        print("Current indexes:")
        indexes = await collection.list_indexes().to_list(None)
        for idx in indexes:
            print(f"  - {idx.get('name')}: {idx.get('key')}")
        
        # Drop the text index if it exists
        for idx in indexes:
            if 'text' in str(idx.get('key', {})):
                index_name = idx.get('name')
                print(f"\nDropping text index: {index_name}")
                await collection.drop_index(index_name)
                print(f"✅ Dropped index: {index_name}")
        
        # List indexes again to confirm
        print("\nIndexes after cleanup:")
        indexes = await collection.list_indexes().to_list(None)
        for idx in indexes:
            print(f"  - {idx.get('name')}: {idx.get('key')}")
        
        print("\n✅ MongoDB indexes fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_indexes())