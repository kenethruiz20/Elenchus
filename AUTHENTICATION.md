# Authentication System Documentation

## Overview

The Elenchus Legal AI backend now includes a comprehensive authentication system with:
- User registration and login
- JWT token-based authentication  
- Password hashing with bcrypt
- Password reset functionality
- Dependency injection for protecting endpoints

## API Endpoints

### Authentication Routes (`/api/v1/auth/`)

#### Register User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",      # Optional
  "last_name": "Doe"         # Optional
}
```

Response:
```json
{
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe", 
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-08-07T18:07:48.672000",
    "last_login": null
  },
  "token": {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### Login User
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com", 
  "password": "password123"
}
```

#### Get Current User Info
```bash
GET /api/v1/auth/me
Authorization: Bearer <jwt_token>
```

#### Logout (Client-side token removal)
```bash
POST /api/v1/auth/logout
Authorization: Bearer <jwt_token>
```

#### Request Password Reset
```bash
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Confirm Password Reset
```bash
POST /api/v1/auth/reset-password/confirm
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "newpassword123"
}
```

## Protecting Endpoints

### Using Authentication Dependencies

The system provides several dependency functions for protecting endpoints:

```python
from app.core.auth import get_current_user, get_current_active_user, get_current_verified_user
from app.models.user import User

# Basic authentication - user must be logged in
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}

# Active user only
@app.get("/active-only") 
async def active_only(current_user: User = Depends(get_current_active_user)):
    return {"user_id": str(current_user.id)}

# Verified user only
@app.get("/verified-only")
async def verified_only(current_user: User = Depends(get_current_verified_user)):
    return {"verified_user": current_user.email}
```

### Example: Protected Messages Endpoint

The `/api/v1/messages/` endpoints are now protected:

```python
@router.get("/research/{research_id}")
async def get_conversation(
    research_id: str,
    current_user_id: str = Depends(get_current_user_id)  # Protected!
):
    # Only authenticated users can access conversations
    # current_user_id contains the authenticated user's ID
```

## Environment Variables

Required environment variables in `.env`:

```bash
# Authentication
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Database  
MONGODB_URL=mongodb://user:pass@host:port/database
MONGODB_DATABASE=elenchus
```

## Architecture

### Models
- `User` (app/models/user.py): User document with email, hashed password, profile info
- Stores in MongoDB with unique email index

### Services  
- `AuthService` (app/services/auth_service.py): Core authentication logic
  - Password hashing/verification 
  - JWT token creation/validation
  - User registration/authentication
  - Password reset token management

### Dependencies
- `get_current_user()`: Get authenticated user
- `get_current_active_user()`: Get active user only
- `get_current_verified_user()`: Get verified user only  
- `get_optional_user()`: Get user if authenticated, None otherwise

### Security Features
- Passwords hashed with bcrypt
- JWT tokens with configurable expiration
- Secure reset tokens (32-byte URL-safe)
- Email validation with pydantic
- User status management (active/inactive, verified/unverified)

## Testing

All authentication functionality has been tested:
- ✅ User registration
- ✅ User login/logout  
- ✅ JWT token validation
- ✅ Protected endpoint access
- ✅ Password reset flow
- ✅ Authentication error handling

## Example Usage

```bash
# 1. Register user
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# 2. Extract token from response and use for protected routes
curl -X GET "http://localhost:8001/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. Access protected endpoints  
curl -X GET "http://localhost:8001/api/v1/messages/research/RESEARCH_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```