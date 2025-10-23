"""Analytics API routes for memory system insights."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, text

from engram.api.deps import get_db_session
from engram.api.models import AnalyticsOverviewResponse
from engram.database.models import Memory, UserMemoryStats
from engram.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db_session),
) -> AnalyticsOverviewResponse:
    """Get comprehensive analytics overview for a user."""
    try:
        # Get total memories
        total_memories = db.query(func.count(Memory.id)).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
            )
        ).scalar() or 0
        
        # Get memory types distribution
        memory_types = {}
        type_counts = db.query(
            Memory.modality,
            func.count(Memory.id)
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
            )
        ).group_by(Memory.modality).all()
        
        for modality, count in type_counts:
            memory_types[modality.value] = count
        
        # Get top sources
        top_sources = db.query(
            Memory.source_uri,
            func.count(Memory.id).label('count')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.source_uri.isnot(None),
            )
        ).group_by(Memory.source_uri).order_by(desc('count')).limit(5).all()
        
        sources_list = [
            {"source": source, "count": count} 
            for source, count in top_sources
        ]
        
        # Get recent activity (last 10 memories)
        recent_activity = db.query(Memory).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
            )
        ).order_by(desc(Memory.created_at)).limit(10).all()
        
        activity_list = [
            {
                "id": memory.id,
                "text": memory.text[:100] + "..." if len(memory.text) > 100 else memory.text,
                "modality": memory.modality.value,
                "created_at": memory.created_at.isoformat(),
                "importance": memory.importance,
            }
            for memory in recent_activity
        ]
        
        # Get requests in last 24 hours (mock data for now)
        requests_last_24h = 0  # Would need request tracking system
        
        # Get P95 latency (mock data for now)
        p95_latency_ms = 85.0  # Would need latency tracking
        
        return AnalyticsOverviewResponse(
            total_memories=total_memories,
            total_requests=0,  # Would need request tracking
            requests_last_24h=requests_last_24h,
            p95_latency_ms=p95_latency_ms,
            memory_types=memory_types,
            top_sources=sources_list,
            recent_activity=activity_list,
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory-stats")
async def get_memory_stats(
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """Get detailed memory statistics."""
    try:
        # Get user stats
        user_stats = db.query(UserMemoryStats).filter(
            and_(
                UserMemoryStats.tenant_id == tenant_id,
                UserMemoryStats.user_id == user_id,
            )
        ).first()
        
        # Get memory distribution by importance
        importance_dist = db.query(
            func.floor(Memory.importance * 10).label('bucket'),
            func.count(Memory.id).label('count')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
            )
        ).group_by('bucket').order_by('bucket').all()
        
        # Get memory growth over time (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        daily_counts = db.query(
            func.date(Memory.created_at).label('date'),
            func.count(Memory.id).label('count')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.created_at >= thirty_days_ago,
            )
        ).group_by('date').order_by('date').all()
        
        # Get average importance by modality
        avg_importance = db.query(
            Memory.modality,
            func.avg(Memory.importance).label('avg_importance')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
            )
        ).group_by(Memory.modality).all()
        
        return {
            "user_stats": {
                "total_memories": user_stats.total_memories if user_stats else 0,
                "active_memories": user_stats.active_memories if user_stats else 0,
                "avg_importance": user_stats.avg_importance if user_stats else 0.0,
                "last_seen": user_stats.last_seen_at.isoformat() if user_stats else None,
            },
            "importance_distribution": [
                {"bucket": bucket, "count": count} 
                for bucket, count in importance_dist
            ],
            "daily_growth": [
                {"date": date.isoformat(), "count": count} 
                for date, count in daily_counts
            ],
            "avg_importance_by_modality": [
                {"modality": modality.value, "avg_importance": float(avg)} 
                for modality, avg in avg_importance
            ],
        }
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage-trends")
async def get_usage_trends(
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """Get usage trends over time."""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Get daily memory creation
        daily_memories = db.query(
            func.date(Memory.created_at).label('date'),
            func.count(Memory.id).label('count')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.created_at >= start_date,
            )
        ).group_by('date').order_by('date').all()
        
        # Get daily memory access
        daily_access = db.query(
            func.date(Memory.last_accessed_at).label('date'),
            func.count(Memory.id).label('count')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.last_accessed_at >= start_date,
            )
        ).group_by('date').order_by('date').all()
        
        # Get modality trends
        modality_trends = db.query(
            Memory.modality,
            func.date(Memory.created_at).label('date'),
            func.count(Memory.id).label('count')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.created_at >= start_date,
            )
        ).group_by(Memory.modality, 'date').order_by('date').all()
        
        # Group by modality
        modality_data = {}
        for modality, date, count in modality_trends:
            if modality.value not in modality_data:
                modality_data[modality.value] = []
            modality_data[modality.value].append({
                "date": date.isoformat(),
                "count": count
            })
        
        return {
            "daily_memories": [
                {"date": date.isoformat(), "count": count} 
                for date, count in daily_memories
            ],
            "daily_access": [
                {"date": date.isoformat(), "count": count} 
                for date, count in daily_access
            ],
            "modality_trends": modality_data,
        }
        
    except Exception as e:
        logger.error(f"Error getting usage trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-sources")
async def get_top_sources(
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of top sources to return"),
    db: Session = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """Get top content sources by memory count."""
    try:
        top_sources = db.query(
            Memory.source_uri,
            func.count(Memory.id).label('count'),
            func.avg(Memory.importance).label('avg_importance'),
            func.max(Memory.created_at).label('last_created')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.source_uri.isnot(None),
            )
        ).group_by(Memory.source_uri).order_by(desc('count')).limit(limit).all()
        
        return [
            {
                "source": source,
                "count": count,
                "avg_importance": float(avg_importance),
                "last_created": last_created.isoformat(),
            }
            for source, count, avg_importance, last_created in top_sources
        ]
        
    except Exception as e:
        logger.error(f"Error getting top sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory-health")
async def get_memory_health(
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """Get memory health metrics and recommendations."""
    try:
        # Get total memories
        total_memories = db.query(func.count(Memory.id)).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
            )
        ).scalar() or 0
        
        # Get low importance memories
        low_importance = db.query(func.count(Memory.id)).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.importance < 0.3,
            )
        ).scalar() or 0
        
        # Get stale memories (not accessed in 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        stale_memories = db.query(func.count(Memory.id)).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.last_accessed_at < thirty_days_ago,
            )
        ).scalar() or 0
        
        # Get duplicate sources
        duplicate_sources = db.query(
            Memory.source_uri,
            func.count(Memory.id).label('count')
        ).filter(
            and_(
                Memory.tenant_id == tenant_id,
                Memory.user_id == user_id,
                Memory.active == True,
                Memory.source_uri.isnot(None),
            )
        ).group_by(Memory.source_uri).having(func.count(Memory.id) > 1).all()
        
        # Calculate health score
        health_score = 100
        if total_memories > 0:
            low_importance_ratio = low_importance / total_memories
            stale_ratio = stale_memories / total_memories
            
            health_score -= (low_importance_ratio * 20)
            health_score -= (stale_ratio * 15)
        
        # Generate recommendations
        recommendations = []
        if low_importance_ratio > 0.3:
            recommendations.append("Consider reviewing and deleting low-importance memories")
        if stale_ratio > 0.5:
            recommendations.append("Many memories haven't been accessed recently - consider consolidation")
        if len(duplicate_sources) > 5:
            recommendations.append("Multiple memories from same source detected - consider deduplication")
        
        return {
            "health_score": max(0, min(100, health_score)),
            "total_memories": total_memories,
            "low_importance_count": low_importance,
            "stale_memories_count": stale_memories,
            "duplicate_sources": len(duplicate_sources),
            "recommendations": recommendations,
        }
        
    except Exception as e:
        logger.error(f"Error getting memory health: {e}")
        raise HTTPException(status_code=500, detail=str(e))