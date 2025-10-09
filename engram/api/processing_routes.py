"""Processing status and job management API routes."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from engram.utils.logger import get_logger
from engram.workers.queue import get_queue_manager
from engram.api.middleware import require_scope, get_current_tenant_id

logger = get_logger(__name__)
router = APIRouter(prefix="/v1/processing", tags=["processing"])


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    progress: float = Field(..., description="Progress (0.0 to 1.0)")
    error: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[dict] = Field(None, description="Job result if completed")
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    started_at: Optional[str] = Field(None, description="Job start timestamp")
    completed_at: Optional[str] = Field(None, description="Job completion timestamp")


@router.get("/status", response_model=JobStatusResponse)
@require_scope("memories:read")
async def get_job_status(
    request,
    job_id: str = Query(..., description="Job identifier"),
):
    """Get job processing status.
    
    Args:
        request: FastAPI request object
        job_id: Job identifier
        
    Returns:
        Job status information
    """
    try:
        tenant_id = get_current_tenant_id(request)
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Authentication required")
        
        queue_manager = get_queue_manager()
        job_data = queue_manager.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Verify job belongs to current tenant
        if job_data.get("tenant_id") != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return JobStatusResponse(**job_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job status")


@router.get("/queue/stats")
@require_scope("analytics:read")
async def get_queue_stats(request):
    """Get queue statistics.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Queue statistics
    """
    try:
        queue_manager = get_queue_manager()
        stats = queue_manager.get_queue_stats()
        
        return {
            "queues": stats,
            "timestamp": queue_manager.redis_conn.time()[0],  # Current timestamp
        }
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve queue statistics")
