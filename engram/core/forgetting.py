"""Smart forgetting engine for memory management."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from engram.utils.config import get_settings
from engram.utils.logger import get_logger
from engram.database.models import Memory
from engram.database.postgres import get_db_session

logger = get_logger(__name__)
settings = get_settings()


class ForgettingEngine:
    """Engine for smart forgetting of low-importance memories."""

    def __init__(self):
        """Initialize forgetting engine."""
        self.importance_threshold = settings.importance_threshold
        self.forgetting_days = settings.forgetting_days

    def forget_user_memories(
        self, tenant_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Forget low-importance memories for a user or all users in tenant.
        
        Args:
            tenant_id: Tenant ID
            user_id: Optional user ID (if None, processes all users in tenant)
            
        Returns:
            Dict with forgetting results
        """
        try:
            with get_db_session() as session:
                # Calculate cutoff date
                cutoff_date = datetime.utcnow() - timedelta(days=self.forgetting_days)
                
                # Build query for memories to forget
                query = session.query(Memory).filter(
                    and_(
                        Memory.tenant_id == tenant_id,
                        Memory.active == True,
                        Memory.importance < self.importance_threshold,
                        Memory.last_accessed_at < cutoff_date,
                    )
                )
                
                if user_id:
                    query = query.filter(Memory.user_id == user_id)
                
                # Get memories to forget
                memories_to_forget = query.all()
                
                if not memories_to_forget:
                    logger.info(
                        "No memories to forget",
                        extra={
                            "tenant_id": tenant_id,
                            "user_id": user_id,
                            "threshold": self.importance_threshold,
                            "days": self.forgetting_days,
                        }
                    )
                    return {
                        "memories_forgotten": 0,
                        "memories_processed": 0,
                        "threshold": self.importance_threshold,
                        "days": self.forgetting_days,
                    }
                
                # Deactivate memories (soft delete)
                memory_ids = [memory.id for memory in memories_to_forget]
                session.query(Memory).filter(
                    Memory.id.in_(memory_ids)
                ).update(
                    {"active": False, "updated_at": datetime.utcnow()},
                    synchronize_session=False
                )
                
                session.commit()
                
                logger.info(
                    "Forgot low-importance memories",
                    extra={
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "memories_forgotten": len(memories_to_forget),
                        "threshold": self.importance_threshold,
                        "days": self.forgetting_days,
                    }
                )
                
                return {
                    "memories_forgotten": len(memories_to_forget),
                    "memories_processed": len(memories_to_forget),
                    "threshold": self.importance_threshold,
                    "days": self.forgetting_days,
                    "memory_ids": memory_ids[:10],  # Return first 10 IDs for reference
                }
                
        except Exception as e:
            logger.error(f"Failed to forget memories: {e}")
            raise

    def forget_old_memories(
        self, tenant_id: str, retention_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Forget memories older than retention period.
        
        Args:
            tenant_id: Tenant ID
            retention_days: Memory retention period (defaults to config)
            
        Returns:
            Dict with forgetting results
        """
        try:
            if retention_days is None:
                retention_days = settings.memory_retention_days
                
            with get_db_session() as session:
                # Calculate cutoff date
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                
                # Get old memories
                old_memories = session.query(Memory).filter(
                    and_(
                        Memory.tenant_id == tenant_id,
                        Memory.active == True,
                        Memory.created_at < cutoff_date,
                    )
                ).all()
                
                if not old_memories:
                    logger.info(
                        "No old memories to forget",
                        extra={
                            "tenant_id": tenant_id,
                            "retention_days": retention_days,
                        }
                    )
                    return {
                        "memories_forgotten": 0,
                        "retention_days": retention_days,
                    }
                
                # Deactivate memories
                memory_ids = [memory.id for memory in old_memories]
                session.query(Memory).filter(
                    Memory.id.in_(memory_ids)
                ).update(
                    {"active": False, "updated_at": datetime.utcnow()},
                    synchronize_session=False
                )
                
                session.commit()
                
                logger.info(
                    "Forgot old memories",
                    extra={
                        "tenant_id": tenant_id,
                        "memories_forgotten": len(old_memories),
                        "retention_days": retention_days,
                    }
                )
                
                return {
                    "memories_forgotten": len(old_memories),
                    "retention_days": retention_days,
                    "memory_ids": memory_ids[:10],
                }
                
        except Exception as e:
            logger.error(f"Failed to forget old memories: {e}")
            raise

    def analyze_memory_health(
        self, tenant_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze memory health and suggest forgetting actions.
        
        Args:
            tenant_id: Tenant ID
            user_id: Optional user ID
            
        Returns:
            Dict with memory health analysis
        """
        try:
            with get_db_session() as session:
                # Build base query
                query = session.query(Memory).filter(
                    and_(
                        Memory.tenant_id == tenant_id,
                        Memory.active == True,
                    )
                )
                
                if user_id:
                    query = query.filter(Memory.user_id == user_id)
                
                # Get memory statistics
                total_memories = query.count()
                
                # Low importance memories
                low_importance = query.filter(
                    Memory.importance < self.importance_threshold
                ).count()
                
                # Old memories
                cutoff_date = datetime.utcnow() - timedelta(days=self.forgetting_days)
                old_memories = query.filter(
                    Memory.last_accessed_at < cutoff_date
                ).count()
                
                # Very old memories
                old_cutoff_date = datetime.utcnow() - timedelta(days=settings.memory_retention_days)
                very_old_memories = query.filter(
                    Memory.created_at < old_cutoff_date
                ).count()
                
                # Average importance
                avg_importance = session.query(
                    func.avg(Memory.importance)
                ).filter(
                    and_(
                        Memory.tenant_id == tenant_id,
                        Memory.active == True,
                    )
                ).scalar() or 0.0
                
                # Modality breakdown
                modality_counts = session.query(
                    Memory.modality,
                    func.count(Memory.id).label("count")
                ).filter(
                    and_(
                        Memory.tenant_id == tenant_id,
                        Memory.active == True,
                    )
                ).group_by(Memory.modality).all()
                
                return {
                    "total_memories": total_memories,
                    "low_importance_count": low_importance,
                    "old_memories_count": old_memories,
                    "very_old_memories_count": very_old_memories,
                    "avg_importance": round(avg_importance, 3),
                    "modality_breakdown": [
                        {
                            "modality": modality.value if modality else "unknown",
                            "count": count,
                        }
                        for modality, count in modality_counts
                    ],
                    "suggestions": {
                        "forget_low_importance": low_importance > 0,
                        "forget_old_memories": old_memories > 0,
                        "forget_very_old_memories": very_old_memories > 0,
                    },
                    "thresholds": {
                        "importance_threshold": self.importance_threshold,
                        "forgetting_days": self.forgetting_days,
                        "retention_days": settings.memory_retention_days,
                    },
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze memory health: {e}")
            raise
