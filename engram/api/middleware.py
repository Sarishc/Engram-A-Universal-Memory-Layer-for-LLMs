"""FastAPI middleware for authentication and request logging."""

import time
import uuid
from typing import Callable, Optional
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from engram.utils.logger import get_logger
from engram.api.auth import ApiKeyManager
from engram.database.apikeys import ApiKey
from engram.database.analytics import RequestLog
from engram.database.postgres import get_db_session
from engram.utils.ids import generate_ulid

logger = get_logger(__name__)

# Security scheme for API keys
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API key validation."""

    def __init__(self, app, require_auth: bool = True):
        """Initialize auth middleware.
        
        Args:
            app: FastAPI app
            require_auth: Whether to require authentication
        """
        super().__init__(app)
        self.require_auth = require_auth
        self.public_paths = {
            "/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics",
            "/graph",  # Static graph visualization
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with authentication."""
        # Check if path is public
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Extract API key from Authorization header
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            if self.require_auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                # Set default values for unauthenticated requests
                request.state.tenant_id = None
                request.state.user_id = None
                request.state.api_key = None
                return await call_next(request)

        # Extract and validate API key
        api_key = auth_header[7:]  # Remove "Bearer " prefix
        api_key_record = ApiKeyManager.validate_api_key(api_key)
        
        if not api_key_record:
            if self.require_auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                request.state.tenant_id = None
                request.state.user_id = None
                request.state.api_key = None
                return await call_next(request)

        # Store auth info in request state
        request.state.tenant_id = api_key_record.tenant_id
        request.state.user_id = api_key_record.user_id
        request.state.api_key = api_key_record

        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware for analytics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log request (async to avoid blocking)
        try:
            self._log_request_async(
                request=request,
                response=response,
                duration_ms=duration_ms,
                request_id=request_id,
            )
        except Exception as e:
            logger.error(f"Failed to log request: {e}")

        return response

    def _log_request_async(
        self,
        request: Request,
        response: Response,
        duration_ms: int,
        request_id: str,
    ):
        """Log request asynchronously."""
        try:
            # Extract request info
            tenant_id = getattr(request.state, "tenant_id", None)
            user_id = getattr(request.state, "user_id", None)
            
            # Extract additional metadata
            user_agent = request.headers.get("user-agent", "")
            ip_address = request.client.host if request.client else None
            
            # Estimate tokens and cost (placeholder)
            tokens_used = None
            cost_usd = None
            
            # Try to extract from response headers or body
            if hasattr(response, "headers"):
                tokens_used = response.headers.get("x-tokens-used")
                cost_usd = response.headers.get("x-cost-usd")
                
            if tokens_used:
                tokens_used = int(tokens_used)
            if cost_usd:
                cost_usd = float(cost_usd)

            # Create request log
            request_log = RequestLog(
                id=generate_ulid(),
                tenant_id=tenant_id,
                user_id=user_id,
                request_id=request_id,
                route=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                user_agent=user_agent,
                ip_address=ip_address,
                metadata={
                    "query_params": dict(request.query_params),
                    "content_type": request.headers.get("content-type", ""),
                }
            )

            # Save to database
            with get_db_session() as session:
                session.add(request_log)
                session.commit()

            logger.info(
                "Request processed",
                extra={
                    "request_id": request_id,
                    "route": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                }
            )

        except Exception as e:
            logger.error(f"Failed to create request log: {e}")


def require_scope(required_scope: str):
    """Decorator to require a specific API scope.
    
    Args:
        required_scope: Required permission scope
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Check if API key is present
            api_key = getattr(request.state, "api_key", None)
            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check scope
            if not ApiKeyManager.check_scope(api_key, required_scope):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required scope: {required_scope}",
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_current_tenant_id(request: Request) -> Optional[str]:
    """Get current tenant ID from request."""
    return getattr(request.state, "tenant_id", None)


def get_current_user_id(request: Request) -> Optional[str]:
    """Get current user ID from request."""
    return getattr(request.state, "user_id", None)


def get_current_api_key(request: Request) -> Optional[ApiKey]:
    """Get current API key from request."""
    return getattr(request.state, "api_key", None)