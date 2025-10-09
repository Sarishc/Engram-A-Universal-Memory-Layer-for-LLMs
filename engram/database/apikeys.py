"""SQLAlchemy ORM models for API keys and authentication."""

from datetime import datetime
from typing import Dict, Any, List, Optional
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Index,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from engram.database.models import Base


class ApiKey(Base):
    """API Key model for authentication."""

    __tablename__ = "api_keys"

    id = Column(String(26), primary_key=True)  # ULID
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(26), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    scopes = Column(JSON, nullable=False, default=list)  # List of permission scopes
    active = Column(Boolean, nullable=False, default=True, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_api_keys_tenant_user", "tenant_id", "user_id"),
        Index("idx_api_keys_active", "active"),
        Index("idx_api_keys_last_used", "last_used_at"),
    )

    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name={self.name}, active={self.active})>"

    def to_dict(self, include_key_hash: bool = False) -> Dict[str, Any]:
        """Convert API key to dictionary."""
        result = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "name": self.name,
            "scopes": self.scopes,
            "active": self.active,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_key_hash:
            result["key_hash"] = self.key_hash
            
        return result

    def has_scope(self, scope: str) -> bool:
        """Check if API key has a specific scope."""
        if not self.active:
            return False
            
        # Admin scope grants all permissions
        if "admin:*" in self.scopes:
            return True
            
        return scope in self.scopes

    def has_any_scope(self, scopes: List[str]) -> bool:
        """Check if API key has any of the specified scopes."""
        return any(self.has_scope(scope) for scope in scopes)

    @property
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if API key is valid (active and not expired)."""
        return self.active and not self.is_expired
