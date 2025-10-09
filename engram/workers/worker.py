"""RQ worker functions for processing background jobs."""

import traceback
from typing import Dict, Any, Optional

from engram.utils.logger import get_logger
from engram.workers.queue import get_queue_manager
from engram.database.jobs import Job, JobStatus, JobType
from engram.database.postgres import get_db_session
from engram.ingest.pipeline import IngestionPipeline
from engram.core.consolidation import ConsolidationEngine
from engram.core.forgetting import ForgettingEngine

logger = get_logger(__name__)


def process_ingest_job(job_id: str) -> Dict[str, Any]:
    """Process an ingest job.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job result
    """
    queue_manager = get_queue_manager()
    
    try:
        # Update job status to running
        queue_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.0)
        
        # Get job details from database
        with get_db_session() as session:
            job = session.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")
                
            job_type = job.job_type
            payload = job.payload
            tenant_id = job.tenant_id
            user_id = job.user_id
            
        logger.info(
            "Processing ingest job",
            extra={
                "job_id": job_id,
                "job_type": job_type.value,
                "tenant_id": tenant_id,
                "user_id": user_id,
            }
        )
        
        # Initialize ingest pipeline
        pipeline = IngestionPipeline()
        
        # Process based on job type
        result = {}
        if job_type == JobType.INGEST_URL:
            queue_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            result = pipeline.ingest_url(
                tenant_id=tenant_id,
                user_id=user_id,
                url=payload["url"],
                content_type=payload.get("type", "web")
            )
            
        elif job_type == JobType.INGEST_FILE:
            queue_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            result = pipeline.ingest_file(
                tenant_id=tenant_id,
                user_id=user_id,
                file_path=payload["file_path"],
                content_type=payload.get("type", "text"),
                filename=payload.get("filename", "unknown")
            )
            
        elif job_type == JobType.INGEST_CHAT:
            queue_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            result = pipeline.ingest_chat(
                tenant_id=tenant_id,
                user_id=user_id,
                platform=payload["platform"],
                items=payload["items"],
                metadata=payload.get("metadata", {})
            )
            
        else:
            raise ValueError(f"Unsupported job type: {job_type}")
            
        # Update job as completed
        queue_manager.update_job_status(
            job_id, 
            JobStatus.COMPLETED, 
            progress=1.0, 
            result=result
        )
        
        logger.info(
            "Completed ingest job",
            extra={
                "job_id": job_id,
                "job_type": job_type.value,
                "memories_created": result.get("memories_created", 0),
            }
        )
        
        return result
        
    except Exception as e:
        error_msg = f"Job failed: {str(e)}\n{traceback.format_exc()}"
        logger.error(
            "Ingest job failed",
            extra={
                "job_id": job_id,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        )
        
        queue_manager.update_job_status(
            job_id, 
            JobStatus.FAILED, 
            error=error_msg
        )
        
        raise


def process_maintenance_job(job_id: str) -> Dict[str, Any]:
    """Process a maintenance job.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job result
    """
    queue_manager = get_queue_manager()
    
    try:
        # Update job status to running
        queue_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.0)
        
        # Get job details from database
        with get_db_session() as session:
            job = session.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job not found: {job_id}")
                
            job_type = job.job_type
            payload = job.payload
            tenant_id = job.tenant_id
            user_id = job.user_id
            
        logger.info(
            "Processing maintenance job",
            extra={
                "job_id": job_id,
                "job_type": job_type.value,
                "tenant_id": tenant_id,
                "user_id": user_id,
            }
        )
        
        result = {}
        
        if job_type == JobType.CONSOLIDATION:
            queue_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            consolidation_engine = ConsolidationEngine()
            result = consolidation_engine.consolidate_user_memories(tenant_id, user_id)
            
        elif job_type == JobType.FORGETTING:
            queue_manager.update_job_status(job_id, JobStatus.RUNNING, progress=0.2)
            forgetting_engine = ForgettingEngine()
            result = forgetting_engine.forget_user_memories(tenant_id, user_id)
            
        else:
            raise ValueError(f"Unsupported maintenance job type: {job_type}")
            
        # Update job as completed
        queue_manager.update_job_status(
            job_id, 
            JobStatus.COMPLETED, 
            progress=1.0, 
            result=result
        )
        
        logger.info(
            "Completed maintenance job",
            extra={
                "job_id": job_id,
                "job_type": job_type.value,
                "result": result,
            }
        )
        
        return result
        
    except Exception as e:
        error_msg = f"Job failed: {str(e)}\n{traceback.format_exc()}"
        logger.error(
            "Maintenance job failed",
            extra={
                "job_id": job_id,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        )
        
        queue_manager.update_job_status(
            job_id, 
            JobStatus.FAILED, 
            error=error_msg
        )
        
        raise


# Alias for backward compatibility
process_consolidation_job = process_maintenance_job
process_forgetting_job = process_maintenance_job
