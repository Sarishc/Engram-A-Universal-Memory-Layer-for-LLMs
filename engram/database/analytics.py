"""SQLAlchemy ORM models for analytics and monitoring."""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Index,
    ForeignKey,
    JSON,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from engram.database.models import Base


class RequestLog(Base):
    """Request logging model for analytics and monitoring."""

    __tablename__ = "request_logs"

    id = Column(String(26), primary_key=True)  # ULID
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(26), nullable=False, index=True)
    request_id = Column(String(26), nullable=False, index=True)  # For tracing
    route = Column(String(255), nullable=False, index=True)  # e.g., "/v1/chat"
    method = Column(String(10), nullable=False, index=True)  # GET, POST, etc.
    status_code = Column(Integer, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=False)  # Response time in milliseconds
    tokens_used = Column(Integer, nullable=True)  # LLM tokens consumed
    cost_usd = Column(Float, nullable=True)  # Estimated cost in USD
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    request_metadata = Column(JSON, nullable=True, default=dict)  # Additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_request_logs_tenant_created", "tenant_id", "created_at"),
        Index("idx_request_logs_user_created", "user_id", "created_at"),
        Index("idx_request_logs_route_created", "route", "created_at"),
        Index("idx_request_logs_status_created", "status_code", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<RequestLog(id={self.id}, route={self.route}, status={self.status_code})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert request log to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "route": self.route,
            "method": self.method,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "request_metadata": self.request_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SystemMetrics(Base):
    """System metrics model for monitoring."""

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)  # e.g., "count", "ms", "bytes"
    tags = Column(JSON, nullable=True, default=dict)  # Additional labels
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_system_metrics_tenant_name", "tenant_id", "metric_name"),
        Index("idx_system_metrics_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SystemMetrics(name={self.metric_name}, value={self.metric_value})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert system metrics to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
