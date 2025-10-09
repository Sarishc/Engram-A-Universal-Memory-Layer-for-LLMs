"""SQLAlchemy ORM models for job processing."""

from datetime import datetime
from typing import Dict, Any, Optional
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    Index,
    ForeignKey,
    JSON,
    Boolean,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from engram.database.models import Base


class JobStatus(enum.Enum):
    """Job processing status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(enum.Enum):
    """Job types."""
    INGEST_URL = "ingest_url"
    INGEST_FILE = "ingest_file"
    INGEST_CHAT = "ingest_chat"
    CONSOLIDATION = "consolidation"
    FORGETTING = "forgetting"
    CONNECTOR_SYNC = "connector_sync"


class Job(Base):
    """Job model for processing tasks."""

    __tablename__ = "jobs"

    id = Column(String(26), primary_key=True)  # ULID
    tenant_id = Column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String(26), nullable=False, index=True)
    job_type = Column(Enum(JobType), nullable=False, index=True)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING, index=True)
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    error = Column(Text, nullable=True)
    payload = Column(JSON, nullable=False, default=dict)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_jobs_tenant_user_status", "tenant_id", "user_id", "status"),
        Index("idx_jobs_type_status", "job_type", "status"),
        Index("idx_jobs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, type={self.job_type.value}, status={self.status.value})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "job_type": self.job_type.value if self.job_type else None,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "error": self.error,
            "payload": self.payload,
            "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_active(self) -> bool:
        """Check if job is currently active."""
        return self.status in [JobStatus.PENDING, JobStatus.RUNNING]
