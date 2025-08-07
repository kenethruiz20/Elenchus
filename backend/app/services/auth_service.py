import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config.settings import settings
from app.models.user import User


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    # Password operations
    def get_password_hash(self, password: str) -> str:
        """Hash a plain password."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    # JWT operations
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
    
    # User authentication
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = await User.find_one(User.email == email)
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.update_last_login()
        await user.save()
        
        return user
    
    async def get_user_by_token(self, token: str) -> User:
        """Get user from JWT token."""
        try:
            payload = self.decode_access_token(token)
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
        user = await User.find_one(User.email == email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        
        return user
    
    # User registration
    async def create_user(self, email: str, password: str, first_name: str = None, last_name: str = None) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await User.find_one(User.email == email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = self.get_password_hash(password)
        
        # Create user
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )
        
        await user.save()
        return user
    
    # Password reset
    def generate_reset_token(self) -> str:
        """Generate a secure reset token."""
        return secrets.token_urlsafe(32)
    
    async def create_reset_token(self, email: str) -> str:
        """Create a password reset token for user."""
        user = await User.find_one(User.email == email)
        if not user:
            # Don't reveal if email exists or not
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="If the email exists, a reset link has been sent"
            )
        
        # Generate token and set expiration (1 hour)
        reset_token = self.generate_reset_token()
        expires = datetime.utcnow() + timedelta(hours=1)
        
        user.set_reset_token(reset_token, expires)
        await user.save()
        
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> User:
        """Reset user password with token."""
        user = await User.find_one(User.reset_token == token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Check if token is expired
        if user.reset_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Update password and clear reset token
        user.hashed_password = self.get_password_hash(new_password)
        user.clear_reset_token()
        await user.save()
        
        return user


# Global auth service instance
auth_service = AuthService()