from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr
from pymongo import IndexModel


class User(Document):
    """User model for authentication and user management."""
    
    # Core fields
    email: EmailStr = Field(..., description="User email address (unique)")
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="Whether user account is active")
    is_verified: bool = Field(default=False, description="Whether user email is verified")
    
    # Profile fields
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    # Password reset
    reset_token: Optional[str] = Field(None, description="Password reset token")
    reset_token_expires: Optional[datetime] = Field(None, description="Reset token expiration")
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel("email", unique=True),
            IndexModel("reset_token"),
            IndexModel("created_at"),
        ]
    
    @property
    def full_name(self) -> str:
        """Return full name or email if names not provided."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.email.split('@')[0]
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_reset_token(self, token: str, expires: datetime):
        """Set password reset token."""
        self.reset_token = token
        self.reset_token_expires = expires
        self.updated_at = datetime.utcnow()
    
    def clear_reset_token(self):
        """Clear password reset token."""
        self.reset_token = None
        self.reset_token_expires = None
        self.updated_at = datetime.utcnow()