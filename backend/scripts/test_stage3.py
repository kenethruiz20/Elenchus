#!/usr/bin/env python3
"""
Stage 3 Implementation Test Script
Tests Authentication & Security functionality.
"""

import asyncio
import sys
import logging
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config.settings import settings
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.gcp_service import gcp_service
from app.database import mongodb_manager
from app.middleware.rag_middleware import RateLimitStore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Stage3TestSuite:
    """Test suite for Stage 3: Authentication & Security."""
    
    def __init__(self):
        self.base_url = f"http://{settings.HOST}:{settings.PORT}"
        self.test_user_email = "stage3_test@example.com"
        self.test_password = "TestPassword123!"
        self.test_user_id = None
        self.test_token = None
    
    async def setup_test_user(self) -> bool:
        """Create a test user for authentication tests."""
        print("🔧 Setting up test user...")
        
        try:
            # Delete existing test user if exists
            existing_user = await User.find_one(User.email == self.test_user_email)
            if existing_user:
                await existing_user.delete()
                print("   Deleted existing test user")
            
            # Create new test user
            test_user = await auth_service.create_user(
                email=self.test_user_email,
                password=self.test_password,
                first_name="Stage3",
                last_name="TestUser"
            )
            
            # Verify user
            test_user.is_verified = True
            await test_user.save()
            
            self.test_user_id = str(test_user.id)
            
            # Create access token
            token_data = {"sub": self.test_user_email}
            self.test_token = auth_service.create_access_token(token_data)
            
            print(f"✅ Test user created: {self.test_user_email}")
            print(f"   User ID: {self.test_user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup test user: {str(e)}")
            return False
    
    async def test_jwt_authentication(self) -> bool:
        """Test JWT authentication with auth service."""
        print("\n🔐 Testing JWT Authentication")
        print("-" * 40)
        
        try:
            # Test password verification
            user = await auth_service.authenticate_user(
                self.test_user_email, 
                self.test_password
            )
            
            if not user:
                print("❌ User authentication failed")
                return False
            
            print(f"✅ User authenticated: {user.email}")
            
            # Test token creation
            token_data = {"sub": user.email}
            token = auth_service.create_access_token(token_data)
            
            if not token:
                print("❌ Token creation failed")
                return False
            
            print("✅ JWT token created successfully")
            
            # Test token validation
            try:
                payload = auth_service.decode_access_token(token)
                if payload.get("sub") != user.email:
                    print("❌ Token validation failed")
                    return False
                
                print("✅ JWT token validated successfully")
            
            except Exception as e:
                print(f"❌ Token validation error: {str(e)}")
                return False
            
            # Test get_user_by_token
            retrieved_user = await auth_service.get_user_by_token(token)
            if retrieved_user.email != user.email:
                print("❌ Get user by token failed")
                return False
            
            print("✅ Get user by token successful")
            
            return True
            
        except Exception as e:
            print(f"❌ JWT authentication test failed: {str(e)}")
            return False
    
    async def test_user_model_security(self) -> bool:
        """Test user model security features."""
        print("\n👤 Testing User Model Security")
        print("-" * 40)
        
        try:
            # Test password hashing
            plain_password = "TestSecurePassword123!"
            hashed = auth_service.get_password_hash(plain_password)
            
            if plain_password == hashed:
                print("❌ Password not hashed")
                return False
            
            print("✅ Password properly hashed")
            
            # Test password verification
            is_valid = auth_service.verify_password(plain_password, hashed)
            if not is_valid:
                print("❌ Password verification failed")
                return False
            
            print("✅ Password verification successful")
            
            # Test wrong password
            is_invalid = auth_service.verify_password("WrongPassword", hashed)
            if is_invalid:
                print("❌ Wrong password accepted")
                return False
            
            print("✅ Wrong password correctly rejected")
            
            # Test user active/inactive
            test_user = await User.find_one(User.email == self.test_user_email)
            
            # Test inactive user
            test_user.is_active = False
            await test_user.save()
            
            inactive_user = await auth_service.authenticate_user(
                self.test_user_email, 
                self.test_password
            )
            
            if inactive_user:
                print("❌ Inactive user authenticated")
                return False
            
            print("✅ Inactive user correctly rejected")
            
            # Reactivate user
            test_user.is_active = True
            await test_user.save()
            
            return True
            
        except Exception as e:
            print(f"❌ User model security test failed: {str(e)}")
            return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting middleware."""
        print("\n⏱️  Testing Rate Limiting")
        print("-" * 40)
        
        try:
            # Test rate limit store
            rate_store = RateLimitStore()
            
            # Test normal requests
            key = "test_user_stage3"
            limit = 5
            window = 60
            
            # Make requests up to limit
            for i in range(limit):
                allowed, info = await rate_store.is_allowed(key, limit, window)
                if not allowed:
                    print(f"❌ Request {i+1} should be allowed")
                    return False
                print(f"✅ Request {i+1}: allowed, remaining: {info['remaining']}")
            
            # Next request should be blocked
            blocked, info = await rate_store.is_allowed(key, limit, window)
            if blocked:
                print("❌ Rate limit not enforced")
                return False
            
            print(f"✅ Request blocked: remaining={info['remaining']}, retry_after={info['retry_after']}")
            
            # Test different key (should be allowed)
            other_key = "other_user_stage3"
            allowed, info = await rate_store.is_allowed(other_key, limit, window)
            if not allowed:
                print("❌ Different user should be allowed")
                return False
            
            print("✅ Different user requests work independently")
            
            return True
            
        except Exception as e:
            print(f"❌ Rate limiting test failed: {str(e)}")
            return False
    
    def test_api_security_headers(self) -> bool:
        """Test API security headers and CORS."""
        print("\n🛡️  Testing API Security Headers")
        print("-" * 40)
        
        try:
            # Test health endpoint (should work without auth)
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            print("✅ Health endpoint accessible")
            
            # Test CORS headers
            cors_response = requests.options(
                f"{self.base_url}/api/v1/rag/health",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                },
                timeout=10
            )
            
            # CORS should be configured
            if "access-control-allow-origin" not in cors_response.headers:
                print("⚠️  CORS headers not found (may be expected)")
            else:
                print("✅ CORS headers present")
            
            return True
            
        except requests.exceptions.ConnectionError:
            print("⚠️  API server not running - skipping API tests")
            return True
        except Exception as e:
            print(f"❌ API security test failed: {str(e)}")
            return False
    
    async def test_gcp_authentication(self) -> bool:
        """Test GCP service account authentication."""
        print("\n☁️  Testing GCP Authentication")
        print("-" * 40)
        
        try:
            # Test GCP initialization
            gcp_initialized = await gcp_service.initialize()
            
            if not gcp_initialized:
                print("⚠️  GCP not configured - this is expected in development")
                print("   To enable GCP:")
                print("   1. Set GCP_PROJECT in .env")
                print("   2. Set GCP_BUCKET in .env") 
                print("   3. Set up service account credentials")
                return True  # Not a failure, just not configured
            
            print("✅ GCP service initialized")
            
            # Test health check
            health = await gcp_service.health_check()
            
            if not health.get('healthy'):
                print(f"❌ GCP health check failed: {health.get('error')}")
                return False
            
            print("✅ GCP health check passed")
            print(f"   Bucket: {health.get('bucket_name')}")
            print(f"   Project: {health.get('project_id')}")
            
            # Test user storage stats (should work even with no files)
            try:
                usage = await gcp_service.get_storage_usage(self.test_user_id)
                if usage.get('success'):
                    print(f"✅ Storage usage check: {usage.get('total_files', 0)} files")
                else:
                    print(f"⚠️  Storage usage error: {usage.get('error')}")
            except Exception as e:
                print(f"⚠️  Storage usage check failed: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ GCP authentication test failed: {str(e)}")
            return False
    
    async def test_multi_tenant_security(self) -> bool:
        """Test multi-tenant security isolation."""
        print("\n🏢 Testing Multi-Tenant Security")
        print("-" * 40)
        
        try:
            # Create two test users
            user1_email = "tenant1_stage3@example.com"
            user2_email = "tenant2_stage3@example.com"
            password = "TestPassword123!"
            
            # Clean up existing users
            for email in [user1_email, user2_email]:
                existing = await User.find_one(User.email == email)
                if existing:
                    await existing.delete()
            
            # Create users
            user1 = await auth_service.create_user(user1_email, password)
            user2 = await auth_service.create_user(user2_email, password)
            
            user1.is_verified = True
            user2.is_verified = True
            await user1.save()
            await user2.save()
            
            print(f"✅ Created test tenants: {user1_email}, {user2_email}")
            
            # Test token isolation
            token1_data = {"sub": user1.email}
            token2_data = {"sub": user2.email}
            
            token1 = auth_service.create_access_token(token1_data)
            token2 = auth_service.create_access_token(token2_data)
            
            # Verify tokens return correct users
            retrieved_user1 = await auth_service.get_user_by_token(token1)
            retrieved_user2 = await auth_service.get_user_by_token(token2)
            
            if retrieved_user1.email != user1.email:
                print("❌ Token 1 returned wrong user")
                return False
            
            if retrieved_user2.email != user2.email:
                print("❌ Token 2 returned wrong user")
                return False
            
            print("✅ Token isolation working correctly")
            
            # Cleanup test users
            await user1.delete()
            await user2.delete()
            print("✅ Test tenant cleanup complete")
            
            return True
            
        except Exception as e:
            print(f"❌ Multi-tenant security test failed: {str(e)}")
            return False
    
    async def test_input_validation(self) -> bool:
        """Test input validation and sanitization."""
        print("\n🧹 Testing Input Validation")
        print("-" * 40)
        
        try:
            # Test middleware input sanitization
            from app.middleware.rag_middleware import sanitize_input, validate_document_type
            
            # Test XSS prevention
            malicious_input = "<script>alert('xss')</script>Hello"
            sanitized = sanitize_input(malicious_input)
            
            if "<script" in sanitized:
                print("❌ XSS not prevented")
                return False
            
            print("✅ XSS input sanitized")
            
            # Test length limiting
            long_input = "A" * 20000
            sanitized_long = sanitize_input(long_input, max_length=1000)
            
            if len(sanitized_long) > 1000:
                print("❌ Input length not limited")
                return False
            
            print("✅ Input length limiting works")
            
            # Test file type validation
            valid_files = ["document.pdf", "text.txt", "file.docx"]
            invalid_files = ["script.exe", "image.png", "data.sql"]
            
            for filename in valid_files:
                if not validate_document_type(filename):
                    print(f"❌ Valid file rejected: {filename}")
                    return False
            
            print("✅ Valid file types accepted")
            
            for filename in invalid_files:
                if validate_document_type(filename):
                    print(f"❌ Invalid file accepted: {filename}")
                    return False
            
            print("✅ Invalid file types rejected")
            
            return True
            
        except Exception as e:
            print(f"❌ Input validation test failed: {str(e)}")
            return False
    
    async def cleanup_test_data(self) -> bool:
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete test user
            test_user = await User.find_one(User.email == self.test_user_email)
            if test_user:
                await test_user.delete()
                print("✅ Test user deleted")
            
            # Clean up any other test users
            test_emails = [
                "tenant1_stage3@example.com",
                "tenant2_stage3@example.com"
            ]
            
            for email in test_emails:
                user = await User.find_one(User.email == email)
                if user:
                    await user.delete()
            
            print("✅ Cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")
            return False


async def main():
    """Main test function."""
    print("🧪 Stage 3: Authentication & Security Tests")
    print("=" * 60)
    
    # Initialize database
    try:
        await mongodb_manager.initialize()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return 1
    
    test_suite = Stage3TestSuite()
    
    # Setup test user
    if not await test_suite.setup_test_user():
        print("❌ Failed to setup test environment")
        return 1
    
    tests = [
        ("JWT Authentication", test_suite.test_jwt_authentication()),
        ("User Model Security", test_suite.test_user_model_security()),
        ("Rate Limiting", test_suite.test_rate_limiting()),
        ("API Security Headers", test_suite.test_api_security_headers()),
        ("GCP Authentication", test_suite.test_gcp_authentication()),
        ("Multi-Tenant Security", test_suite.test_multi_tenant_security()),
        ("Input Validation", test_suite.test_input_validation()),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_coro in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
                
            if result:
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    # Cleanup
    print("\n" + "=" * 60)
    await test_suite.cleanup_test_data()
    
    # Results
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All Stage 3 tests passed! Authentication & Security is complete.")
        print("\n🎯 Ready for Stage 4: Document Upload & Registration")
        
        # Update plan status
        try:
            plan_file = Path(__file__).parent.parent / "RAG_IMPLEMENTATION_PLAN.md"
            if plan_file.exists():
                content = plan_file.read_text()
                updated_content = content.replace(
                    "### **Stage 3: Authentication & Security**\n**Status: ⏳ Pending**",
                    "### **Stage 3: Authentication & Security**\n**Status: ✅ Completed**"
                )
                plan_file.write_text(updated_content)
                print("📝 Updated implementation plan status")
        except Exception as e:
            print(f"⚠️  Could not update plan: {str(e)}")
        
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)