"""Analytics and monitoring API routes."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from engram.database.postgres import get_db_session
from engram.database.analytics import RequestLog, SystemMetrics
from engram.database.jobs import Job, JobStatus, JobType
from engram.database.models import Memory, ModalityType
from engram.api.middleware import require_scope, get_current_tenant_id
from engram.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/analytics/overview")
@require_scope("analytics:read")
async def get_analytics_overview(
    request,
    db: Session = Depends(get_db_session),
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
) -> Dict[str, Any]:
    """Get analytics overview for a tenant.
    
    Args:
        request: FastAPI request object
        db: Database session
        days: Number of days to analyze
        
    Returns:
        Analytics overview data
    """
    tenant_id = get_current_tenant_id(request)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")
    
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Request counts and latency
        request_stats = db.query(
            func.count(RequestLog.id).label("total_requests"),
            func.avg(RequestLog.duration_ms).label("avg_latency_ms"),
            func.percentile_cont(0.95).within_group(RequestLog.duration_ms).label("p95_latency_ms"),
            func.sum(RequestLog.tokens_used).label("total_tokens"),
            func.sum(RequestLog.cost_usd).label("total_cost_usd"),
        ).filter(
            and_(
                RequestLog.tenant_id == tenant_id,
                RequestLog.created_at >= start_date,
                RequestLog.created_at <= end_date,
            )
        ).first()
        
        # Status code breakdown
        status_breakdown = db.query(
            RequestLog.status_code,
            func.count(RequestLog.id).label("count"),
        ).filter(
            and_(
                RequestLog.tenant_id == tenant_id,
                RequestLog.created_at >= start_date,
                RequestLog.created_at <= end_date,
            )
        ).group_by(RequestLog.status_code).all()
        
        # Route breakdown
        route_breakdown = db.query(
            RequestLog.route,
            func.count(RequestLog.id).label("count"),
            func.avg(RequestLog.duration_ms).label("avg_latency_ms"),
        ).filter(
            and_(
                RequestLog.tenant_id == tenant_id,
                RequestLog.created_at >= start_date,
                RequestLog.created_at <= end_date,
            )
        ).group_by(RequestLog.route).order_by(desc("count")).limit(10).all()
        
        # Memory counts by modality
        memory_stats = db.query(
            Memory.modality,
            func.count(Memory.id).label("count"),
        ).filter(
            Memory.tenant_id == tenant_id,
            Memory.active == True,
        ).group_by(Memory.modality).all()
        
        # Job statistics
        job_stats = db.query(
            Job.job_type,
            Job.status,
            func.count(Job.id).label("count"),
        ).filter(
            Job.tenant_id == tenant_id,
            Job.created_at >= start_date,
            Job.created_at <= end_date,
        ).group_by(Job.job_type, Job.status).all()
        
        # Last 24 hours activity
        last_24h = end_date - timedelta(hours=24)
        last_24h_stats = db.query(
            func.count(RequestLog.id).label("requests_24h"),
            func.avg(RequestLog.duration_ms).label("avg_latency_24h"),
        ).filter(
            and_(
                RequestLog.tenant_id == tenant_id,
                RequestLog.created_at >= last_24h,
                RequestLog.created_at <= end_date,
            )
        ).first()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days,
            },
            "requests": {
                "total": request_stats.total_requests or 0,
                "last_24h": last_24h_stats.requests_24h or 0,
                "avg_latency_ms": round(request_stats.avg_latency_ms or 0, 2),
                "p95_latency_ms": round(request_stats.p95_latency_ms or 0, 2),
                "last_24h_avg_latency_ms": round(last_24h_stats.avg_latency_24h or 0, 2),
            },
            "costs": {
                "total_tokens": request_stats.total_tokens or 0,
                "total_cost_usd": round(request_stats.total_cost_usd or 0, 4),
            },
            "status_breakdown": [
                {"status_code": status, "count": count}
                for status, count in status_breakdown
            ],
            "route_breakdown": [
                {
                    "route": route,
                    "count": count,
                    "avg_latency_ms": round(avg_latency_ms or 0, 2),
                }
                for route, count, avg_latency_ms in route_breakdown
            ],
            "memory_stats": [
                {
                    "modality": modality.value if modality else "unknown",
                    "count": count,
                }
                for modality, count in memory_stats
            ],
            "job_stats": [
                {
                    "job_type": job_type.value,
                    "status": status.value,
                    "count": count,
                }
                for job_type, status, count in job_stats
            ],
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.get("/analytics/requests")
@require_scope("analytics:read")
async def get_request_logs(
    request,
    db: Session = Depends(get_db_session),
    limit: int = Query(100, ge=1, le=1000, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    route: Optional[str] = Query(None, description="Filter by route"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
) -> Dict[str, Any]:
    """Get detailed request logs.
    
    Args:
        request: FastAPI request object
        db: Database session
        limit: Maximum number of requests to return
        offset: Number of requests to skip
        route: Filter by specific route
        status_code: Filter by status code
        days: Number of days to look back
        
    Returns:
        Request logs data
    """
    tenant_id = get_current_tenant_id(request)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")
    
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = db.query(RequestLog).filter(
            and_(
                RequestLog.tenant_id == tenant_id,
                RequestLog.created_at >= start_date,
                RequestLog.created_at <= end_date,
            )
        )
        
        if route:
            query = query.filter(RequestLog.route == route)
        if status_code:
            query = query.filter(RequestLog.status_code == status_code)
            
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        request_logs = query.order_by(desc(RequestLog.created_at)).offset(offset).limit(limit).all()
        
        return {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "requests": [
                {
                    "id": log.id,
                    "request_id": log.request_id,
                    "route": log.route,
                    "method": log.method,
                    "status_code": log.status_code,
                    "duration_ms": log.duration_ms,
                    "tokens_used": log.tokens_used,
                    "cost_usd": log.cost_usd,
                    "user_agent": log.user_agent,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat(),
                    "metadata": log.metadata,
                }
                for log in request_logs
            ],
        }
        
    except Exception as e:
        logger.error(f"Failed to get request logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve request logs")


@router.get("/analytics/system")
@require_scope("analytics:read")
async def get_system_metrics(
    request,
    db: Session = Depends(get_db_session),
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
) -> Dict[str, Any]:
    """Get system metrics.
    
    Args:
        request: FastAPI request object
        db: Database session
        metric_name: Filter by specific metric name
        hours: Number of hours to look back
        
    Returns:
        System metrics data
    """
    tenant_id = get_current_tenant_id(request)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")
    
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        
        # Build query
        query = db.query(SystemMetrics).filter(
            and_(
                SystemMetrics.tenant_id == tenant_id,
                SystemMetrics.created_at >= start_date,
                SystemMetrics.created_at <= end_date,
            )
        )
        
        if metric_name:
            query = query.filter(SystemMetrics.metric_name == metric_name)
            
        # Get metrics
        metrics = query.order_by(desc(SystemMetrics.created_at)).all()
        
        # Group by metric name
        metrics_by_name = {}
        for metric in metrics:
            name = metric.metric_name
            if name not in metrics_by_name:
                metrics_by_name[name] = {
                    "name": name,
                    "unit": metric.metric_unit,
                    "values": [],
                }
            metrics_by_name[name]["values"].append({
                "value": metric.metric_value,
                "timestamp": metric.created_at.isoformat(),
                "tags": metric.tags,
            })
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "hours": hours,
            },
            "metrics": list(metrics_by_name.values()),
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")
