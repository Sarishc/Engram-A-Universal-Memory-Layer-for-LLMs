"""API key authentication and authorization."""

import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from engram.utils.config import get_settings
from engram.utils.logger import get_logger
from engram.database.apikeys import ApiKey
from engram.database.postgres import get_db_session
from engram.utils.ids import generate_ulid

logger = get_logger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Standard API scopes
SCOPES = {
    "memories:read": "Read memories and retrieve data",
    "memories:write": "Create, update, and delete memories",
    "ingest:write": "Ingest new content (URL, file, chat)",
    "chat:read": "Use chat endpoints",
    "router:call": "Call router completion endpoint",
    "graph:read": "Read graph data and subgraphs",
    "analytics:read": "View analytics and metrics",
    "admin:*": "Full administrative access",
}


class ApiKeyManager:
    """Manages API key creation, validation, and authorization."""

    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key.
        
        Returns:
            Raw API key string
        """
        # Generate random bytes and encode as base64
        key_bytes = secrets.token_bytes(settings.api_key_bytes)
        key_string = secrets.token_urlsafe(settings.api_key_bytes)
        return f"{settings.api_key_prefix}{key_string}"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage.
        
        Args:
            api_key: Raw API key
            
        Returns:
            Hashed API key
        """
        return pwd_context.hash(api_key)

    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str) -> bool:
        """Verify an API key against its hash.
        
        Args:
            api_key: Raw API key
            hashed_key: Stored hash
            
        Returns:
            True if key is valid
        """
        return pwd_context.verify(api_key, hashed_key)

    @staticmethod
    def create_api_key(
        tenant_id: str,
        user_id: str,
        name: str,
        scopes: List[str],
        expires_at: Optional[datetime] = None
    ) -> Dict[str, str]:
        """Create a new API key.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            name: Human-readable name for the key
            scopes: List of permission scopes
            expires_at: Optional expiration date
            
        Returns:
            Dict with api_key and key_id
        """
        try:
            # Generate new key
            raw_key = ApiKeyManager.generate_api_key()
            key_hash = ApiKeyManager.hash_api_key(raw_key)
            
            # Create database record
            key_id = generate_ulid()
            api_key = ApiKey(
                id=key_id,
                tenant_id=tenant_id,
                user_id=user_id,
                name=name,
                key_hash=key_hash,
                scopes=scopes,
                expires_at=expires_at
            )
            
            with get_db_session() as session:
                session.add(api_key)
                session.commit()
                
            logger.info(
                "Created API key",
                extra={
                    "key_id": key_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "name": name,
                    "scopes": scopes,
                }
            )
            
            return {
                "api_key": raw_key,
                "key_id": key_id,
            }
            
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise

    @staticmethod
    def validate_api_key(api_key: str) -> Optional[ApiKey]:
        """Validate an API key and return the associated record.
        
        Args:
            api_key: Raw API key
            
        Returns:
            ApiKey record if valid, None otherwise
        """
        try:
            with get_db_session() as session:
                # Get all active API keys (we need to check each one)
                api_keys = session.query(ApiKey).filter(
                    ApiKey.active == True,
                    ApiKey.expires_at > datetime.utcnow()
                ).all()
                
                for key_record in api_keys:
                    if ApiKeyManager.verify_api_key(api_key, key_record.key_hash):
                        # Update last used timestamp
                        key_record.last_used_at = datetime.utcnow()
                        session.commit()
                        
                        logger.debug(
                            "Validated API key",
                            extra={
                                "key_id": key_record.id,
                                "tenant_id": key_record.tenant_id,
                                "user_id": key_record.user_id,
                            }
                        )
                        
                        return key_record
                        
                return None
                
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return None

    @staticmethod
    def revoke_api_key(key_id: str, tenant_id: str) -> bool:
        """Revoke an API key.
        
        Args:
            key_id: API key ID
            tenant_id: Tenant ID (for security)
            
        Returns:
            True if revoked successfully
        """
        try:
            with get_db_session() as session:
                api_key = session.query(ApiKey).filter(
                    ApiKey.id == key_id,
                    ApiKey.tenant_id == tenant_id
                ).first()
                
                if api_key:
                    api_key.active = False
                    session.commit()
                    
                    logger.info(
                        "Revoked API key",
                        extra={
                            "key_id": key_id,
                            "tenant_id": tenant_id,
                        }
                    )
                    
                    return True
                    
                return False
                
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False

    @staticmethod
    def list_api_keys(tenant_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List API keys for a tenant/user.
        
        Args:
            tenant_id: Tenant ID
            user_id: Optional user ID filter
            
        Returns:
            List of API key records (without key hashes)
        """
        try:
            with get_db_session() as session:
                query = session.query(ApiKey).filter(ApiKey.tenant_id == tenant_id)
                
                if user_id:
                    query = query.filter(ApiKey.user_id == user_id)
                    
                api_keys = query.order_by(ApiKey.created_at.desc()).all()
                
                return [key.to_dict() for key in api_keys]
                
        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            return []

    @staticmethod
    def check_scope(api_key: ApiKey, required_scope: str) -> bool:
        """Check if an API key has a required scope.
        
        Args:
            api_key: API key record
            required_scope: Required permission scope
            
        Returns:
            True if authorized
        """
        if not api_key.is_valid:
            return False
            
        return api_key.has_scope(required_scope)

    @staticmethod
    def get_available_scopes() -> Dict[str, str]:
        """Get available API scopes.
        
        Returns:
            Dict mapping scope names to descriptions
        """
        return SCOPES.copy()
