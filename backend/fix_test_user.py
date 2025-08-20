#!/usr/bin/env python3
"""
Fix test user password and verification status.
"""

import asyncio
from app.models.user import User
from app.database import mongodb_manager
from passlib.context import CryptContext

async def fix_test_user():
    # Initialize database connection
    await mongodb_manager.initialize()
    
    email = "test@example.com"
    password = "TestPassword123!"
    
    # Create password context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Find user
    user = await User.find_one({"email": email})
    
    if user:
        print(f"Found user: {email}")
        # Update password and verification status
        user.hashed_password = pwd_context.hash(password)
        user.is_active = True
        user.is_verified = False  # Set to False for testing
        await user.save()
        print(f"✅ Updated user:")
        print(f"  Password reset to: {password}")
        print(f"  Is active: {user.is_active}")
        print(f"  Is verified: {user.is_verified}")
    else:
        # Create new user
        new_user = User(
            email=email,
            hashed_password=pwd_context.hash(password),
            is_active=True,
            is_verified=False
        )
        await new_user.insert()
        print(f"✅ Created test user: {email}")
        print(f"  Password: {password}")
        print(f"  Is active: True")
        print(f"  Is verified: False")

if __name__ == "__main__":
    asyncio.run(fix_test_user())