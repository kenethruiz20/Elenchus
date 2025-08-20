#!/usr/bin/env python3
"""
Create a test user without email verification for testing.
"""

import asyncio
from app.models.user import User
from app.services.auth_service import auth_service
from app.database import mongodb_manager

async def create_test_user():
    # Initialize database connection
    await mongodb_manager.initialize()
    
    email = "test@example.com"
    password = "TestPassword123!"
    
    # Check if user exists
    existing_user = await User.find_one({"email": email})
    
    if existing_user:
        print(f"User already exists: {email}")
        print(f"  Is verified: {existing_user.is_verified}")
        print(f"  Is active: {existing_user.is_active}")
        
        # Update to ensure it's active but not verified
        existing_user.is_active = True
        existing_user.is_verified = False
        await existing_user.save()
        print("Updated user to: active=True, verified=False")
    else:
        # Create new user
        hashed_password = auth_service.pwd_context.hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False  # Not verified for testing
        )
        await new_user.insert()
        print(f"✅ Created test user: {email}")
        print(f"  Password: {password}")
        print(f"  Is active: True")
        print(f"  Is verified: False")
    
    # Test login
    print("\nTesting login...")
    user = await auth_service.authenticate_user(email, password)
    if user:
        print("✅ Login successful")
        token_data = await auth_service.create_access_token({"sub": email})
        print(f"  Token created: {token_data['access_token'][:20]}...")
    else:
        print("❌ Login failed")

if __name__ == "__main__":
    asyncio.run(create_test_user())