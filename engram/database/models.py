"""SQLAlchemy ORM models for Engram."""

from datetime import datetime
from typing import Dict, Any
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    Index,
    JSON,
    ForeignKey,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class ModalityType(enum.Enum):
    """Supported content modalities."""
    TEXT = "text"
    PDF = "pdf"
    WEB = "web"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CHAT = "chat"


class Tenant(Base):
    """Tenant model for multi-tenant isolation."""
    
    __tablename__ = "tenants"
    
    id = Column(String(26), primary_key=True)  # ULID
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    memories = relationship("Memory", back_populates="tenant", cascade="all, delete-orphan")
    user_stats = relationship("UserMemoryStats", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name={self.name})>"


class Memory(Base):
    """Memory model for storing user memories."""
    
    __tablename__ = "memories"
    
    id = Column(String(26), primary_key=True)  # ULID
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(26), nullable=False, index=True)
    
    # Memory content
    text = Column(Text, nullable=False)
    memory_metadata = Column(JSON, nullable=False, default=dict)
    
    # Multimodal fields
    modality = Column(Enum(ModalityType), nullable=False, default=ModalityType.TEXT, index=True)
    source_uri = Column(Text, nullable=True)
    chunk_idx = Column(Integer, nullable=True)
    mime = Column(String(128), nullable=True)
    caption_or_transcript = Column(Text, nullable=True)
    
    # Memory properties
    importance = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    decay_weight = Column(Float, nullable=False, default=1.0)  # 0.0 to 1.0
    active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="memories")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_memories_tenant_user", "tenant_id", "user_id"),
        Index("idx_memories_active_created", "active", "created_at"),
        Index("idx_memories_importance", "importance"),
        Index("idx_memories_last_accessed", "last_accessed_at"),
        Index("idx_memories_modality", "modality"),
        Index("idx_memories_source_uri", "source_uri"),
        Index("idx_memories_tenant_user_modality", "tenant_id", "user_id", "modality"),
    )
    
    def __repr__(self) -> str:
        return f"<Memory(id={self.id}, tenant_id={self.tenant_id}, user_id={self.user_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary.
        
        Returns:
            Dictionary representation of the memory
        """
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "text": self.text,
            "metadata": self.memory_metadata,
            "modality": self.modality.value if self.modality else None,
            "source_uri": self.source_uri,
            "chunk_idx": self.chunk_idx,
            "mime": self.mime,
            "caption_or_transcript": self.caption_or_transcript,
            "importance": self.importance,
            "decay_weight": self.decay_weight,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserMemoryStats(Base):
    """User memory statistics for analytics and management."""
    
    __tablename__ = "user_memory_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(26), nullable=False, index=True)
    
    # Statistics
    total_memories = Column(Integer, nullable=False, default=0)
    active_memories = Column(Integer, nullable=False, default=0)
    avg_importance = Column(Float, nullable=False, default=0.0)
    
    # Timestamps
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="user_stats")
    
    # Unique constraint
    __table_args__ = (
        Index("idx_user_stats_tenant_user", "tenant_id", "user_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<UserMemoryStats(tenant_id={self.tenant_id}, user_id={self.user_id}, total={self.total_memories})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user stats to dictionary.
        
        Returns:
            Dictionary representation of the user stats
        """
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "total_memories": self.total_memories,
            "active_memories": self.active_memories,
            "avg_importance": self.avg_importance,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
