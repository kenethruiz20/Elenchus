#!/usr/bin/env python3
"""
Script to verify test user in the database
"""
import asyncio
from app.models.user import User
from app.config.database import init_database

async def verify_test_user():
    """Verify the test user"""
    try:
        # Initialize database
        await init_database()
        print("✅ Database initialized")
        
        # Find test user
        user = await User.find_one(User.email == "test@example.com")
        if not user:
            print("❌ Test user not found")
            return
        
        print(f"📧 Found user: {user.email}")
        print(f"🔍 Current verification status: {user.is_verified}")
        
        # Update user to verified
        if not user.is_verified:
            await user.update({"$set": {"is_verified": True}})
            print("✅ User verification status updated to True")
        else:
            print("✅ User is already verified")
            
        # Confirm the update
        updated_user = await User.find_one(User.email == "test@example.com")
        if updated_user:
            print(f"🎉 Final verification status: {updated_user.is_verified}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_test_user())