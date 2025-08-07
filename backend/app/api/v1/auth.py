from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserResponse,
    TokenResponse,
    LoginResponse,
    MessageResponse,
)
from app.models.user import User
from app.services.auth_service import auth_service
from app.core.auth import get_current_user, security
from app.config.settings import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """
    Register a new user.
    
    Creates a new user account and returns authentication tokens.
    """
    try:
        # Create user
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Prepare response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login,
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        
        return LoginResponse(user=user_response, token=token_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(user_data: UserLoginRequest):
    """
    Authenticate user and return access token.
    """
    # Authenticate user
    user = await auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Prepare response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
    )
    
    token_response = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return LoginResponse(user=user_response, token=token_response)


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user (client-side token invalidation).
    
    Note: Since we're using stateless JWT tokens, actual logout happens on the client side
    by deleting the token. This endpoint serves as a confirmation.
    """
    # Verify token is valid (will raise exception if not)
    await auth_service.get_user_by_token(credentials.credentials)
    
    return MessageResponse(
        message="Successfully logged out. Please remove the token from client storage.",
        success=True
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.post("/reset-password", response_model=MessageResponse)
async def request_password_reset(reset_data: PasswordResetRequest):
    """
    Request password reset.
    
    Generates a reset token and sends it via email (email sending not implemented yet).
    """
    try:
        reset_token = await auth_service.create_reset_token(reset_data.email)
        
        # TODO: Send email with reset token
        # For now, we'll return the token in the response (NOT for production!)
        return MessageResponse(
            message=f"Password reset requested. Token: {reset_token} (In production, this would be sent via email)",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )


@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_password_reset(reset_data: PasswordResetConfirm):
    """
    Confirm password reset with token.
    """
    try:
        user = await auth_service.reset_password(reset_data.token, reset_data.new_password)
        
        return MessageResponse(
            message="Password has been successfully reset. Please login with your new password.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset confirmation failed: {str(e)}"
        )