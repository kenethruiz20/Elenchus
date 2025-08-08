"""
RAG System Middleware
Provides rate limiting, request validation, and security controls for RAG endpoints.
"""

import time
import json
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RateLimitStore:
    """In-memory rate limit store with sliding window."""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, key: str, limit: int, window_seconds: int) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed and return rate limit info."""
        async with self.lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Clean old requests
            request_times = self.requests[key]
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            # Check limit
            current_requests = len(request_times)
            allowed = current_requests < limit
            
            if allowed:
                request_times.append(now)
            
            # Calculate reset time
            if request_times:
                oldest_request = request_times[0]
                reset_time = oldest_request + window_seconds
            else:
                reset_time = now + window_seconds
            
            return allowed, {
                "limit": limit,
                "remaining": max(0, limit - current_requests - (1 if allowed else 0)),
                "reset": int(reset_time),
                "retry_after": max(0, int(reset_time - now)) if not allowed else 0
            }


class RAGSecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for RAG endpoints."""
    
    def __init__(self, app, rate_limit_store: Optional[RateLimitStore] = None):
        super().__init__(app)
        self.rate_limit_store = rate_limit_store or RateLimitStore()
        
        # Rate limit configurations (requests per minute)
        self.rate_limits = {
            "/api/v1/rag/documents/upload": 10,    # Document uploads
            "/api/v1/rag/search": 60,             # Search requests  
            "/api/v1/rag/chat": 30,               # Chat requests
            "/api/v1/rag/documents": 120,         # Document listing
            "/api/v1/rag/sessions": 60,           # Session management
            "default": 100                        # Default limit
        }
        
        # File size limits (bytes)
        self.max_upload_size = 50 * 1024 * 1024  # 50MB
        
        # Blocked patterns in requests
        self.blocked_patterns = [
            "DROP TABLE",
            "DELETE FROM", 
            "TRUNCATE",
            "../",
            "<script",
            "javascript:",
            "eval(",
            "exec(",
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware."""
        
        # Skip non-RAG endpoints
        if not request.url.path.startswith("/api/v1/rag"):
            return await call_next(request)
        
        try:
            # Apply security checks
            await self._validate_request_security(request)
            await self._apply_rate_limiting(request)
            await self._validate_file_upload(request)
            
            # Process request
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path
                }
            )
        except Exception as e:
            logger.error(f"RAG middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path
                }
            )
    
    async def _validate_request_security(self, request: Request):
        """Validate request for security issues."""
        
        # Check for malicious patterns in URL
        url_path = str(request.url)
        for pattern in self.blocked_patterns:
            if pattern.lower() in url_path.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Malicious pattern detected in request"
                )
        
        # Validate headers
        if request.headers.get("content-length"):
            try:
                content_length = int(request.headers["content-length"])
                if content_length > self.max_upload_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request too large. Maximum size: {self.max_upload_size // 1024 // 1024}MB"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Content-Length header"
                )
        
        # Check for suspicious headers
        suspicious_headers = ["x-forwarded-host", "x-real-ip"]
        for header in suspicious_headers:
            if header in request.headers:
                value = request.headers[header]
                if any(pattern in value.lower() for pattern in self.blocked_patterns):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Suspicious header value detected"
                    )
    
    async def _apply_rate_limiting(self, request: Request):
        """Apply rate limiting based on user and endpoint."""
        
        # Get user identifier (IP if no auth, user_id if authenticated)
        user_id = None
        if hasattr(request.state, "user_id"):
            user_id = request.state.user_id
        
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = user_id or client_ip
        
        # Get rate limit for endpoint
        endpoint_path = request.url.path
        rate_limit = self.rate_limits.get(endpoint_path, self.rate_limits["default"])
        
        # Check rate limit
        allowed, rate_info = await self.rate_limit_store.is_allowed(
            f"{rate_limit_key}:{endpoint_path}",
            rate_limit,
            60  # 1 minute window
        )
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["retry_after"])
                }
            )
    
    async def _validate_file_upload(self, request: Request):
        """Validate file upload requests."""
        
        if request.url.path == "/api/v1/rag/documents/upload":
            # Check content type
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("multipart/form-data"):
                return  # Not a file upload
            
            # Additional file upload validations can be added here
            # (file type validation is handled in the endpoint)
            pass


class RAGRequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for RAG requests."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("rag.requests")
    
    async def dispatch(self, request: Request, call_next):
        """Log RAG requests for monitoring."""
        
        # Skip non-RAG endpoints
        if not request.url.path.startswith("/api/v1/rag"):
            return await call_next(request)
        
        start_time = time.time()
        
        # Log request
        self.logger.info(f"RAG Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            self.logger.info(
                f"RAG Response: {response.status_code} - {process_time:.3f}s - {request.method} {request.url.path}"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(
                f"RAG Error: {str(e)} - {process_time:.3f}s - {request.method} {request.url.path}"
            )
            raise


class RAGContextMiddleware(BaseHTTPMiddleware):
    """Middleware to inject user context for RAG endpoints."""
    
    async def dispatch(self, request: Request, call_next):
        """Add user context to request state."""
        
        # Skip non-RAG endpoints
        if not request.url.path.startswith("/api/v1/rag"):
            return await call_next(request)
        
        # Extract user info from JWT if present
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                # Decode token to get user info (simplified - actual implementation would use auth_service)
                from app.services.auth_service import auth_service
                payload = auth_service.decode_access_token(token)
                request.state.user_email = payload.get("sub")
                request.state.user_id = payload.get("user_id")  # If included in token
            except Exception:
                # Invalid token - let the auth dependency handle it
                pass
        
        return await call_next(request)


# Utility functions
def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fall back to client host
    return request.client.host if request.client else "unknown"


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove dangerous patterns
    dangerous_patterns = [
        "<script",
        "</script>",
        "javascript:",
        "data:text/html",
        "vbscript:",
        "onload=",
        "onerror=",
    ]
    
    for pattern in dangerous_patterns:
        text = text.replace(pattern, "")
    
    return text.strip()


def validate_document_type(filename: str) -> bool:
    """Validate document type based on filename."""
    allowed_extensions = {
        ".pdf", ".txt", ".doc", ".docx", 
        ".md", ".rtf", ".odt"
    }
    
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in allowed_extensions)