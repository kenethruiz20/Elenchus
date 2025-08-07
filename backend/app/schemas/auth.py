from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Request schemas
class UserRegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


# Response schemas
class UserResponse(BaseModel):
    """User response schema."""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    full_name: str = Field(..., description="User full name or email prefix")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class LoginResponse(BaseModel):
    """Login response schema."""
    user: UserResponse
    token: TokenResponse


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")


# Token payload schema
class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None