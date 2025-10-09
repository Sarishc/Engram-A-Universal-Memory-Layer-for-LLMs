"""SQLAlchemy ORM models for the graph layer."""

from datetime import datetime
from typing import Dict, Any

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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .models import Base


class Node(Base):
    """Graph node representing entities extracted from content."""
    
    __tablename__ = "nodes"
    
    id = Column(String(26), primary_key=True)  # ULID
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(26), nullable=False, index=True)
    
    # Node properties
    label = Column(String(255), nullable=False, index=True)
    node_type = Column(String(100), nullable=False, default="entity")  # entity, concept, person, etc.
    properties = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_nodes_tenant_user", "tenant_id", "user_id"),
        Index("idx_nodes_label", "label"),
        Index("idx_nodes_type", "node_type"),
        Index("idx_nodes_tenant_user_label", "tenant_id", "user_id", "label", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<Node(id={self.id}, label={self.label}, type={self.node_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary.
        
        Returns:
            Dictionary representation of the node
        """
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "label": self.label,
            "type": self.node_type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Edge(Base):
    """Graph edge representing relationships between entities."""
    
    __tablename__ = "edges"
    
    id = Column(String(26), primary_key=True)  # ULID
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(26), nullable=False, index=True)
    
    # Edge properties
    src_id = Column(String(26), ForeignKey("nodes.id"), nullable=False, index=True)
    dst_id = Column(String(26), ForeignKey("nodes.id"), nullable=False, index=True)
    relation = Column(String(100), nullable=False, index=True)
    weight = Column(Float, nullable=False, default=1.0)
    properties = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")
    source_node = relationship("Node", foreign_keys=[src_id])
    target_node = relationship("Node", foreign_keys=[dst_id])
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_edges_tenant_user", "tenant_id", "user_id"),
        Index("idx_edges_src", "src_id"),
        Index("idx_edges_dst", "dst_id"),
        Index("idx_edges_relation", "relation"),
        Index("idx_edges_weight", "weight"),
        Index("idx_edges_tenant_user_src_dst", "tenant_id", "user_id", "src_id", "dst_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<Edge(id={self.id}, {self.src_id} -> {self.dst_id}, {self.relation})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary.
        
        Returns:
            Dictionary representation of the edge
        """
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "src": self.src_id,
            "dst": self.dst_id,
            "relation": self.relation,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
