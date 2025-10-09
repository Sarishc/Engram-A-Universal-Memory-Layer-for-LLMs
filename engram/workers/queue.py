"""RQ queue management for background job processing."""

import json
from functools import lru_cache
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import redis
from rq import Queue, Worker, Connection
from rq.job import Job as RQJob

from engram.utils.config import get_settings
from engram.utils.logger import get_logger
from engram.database.jobs import Job, JobStatus, JobType
from engram.database.postgres import get_db_session
from engram.utils.ids import generate_ulid

logger = get_logger(__name__)
settings = get_settings()


class QueueManager:
    """Manages RQ queues and job processing."""

    def __init__(self):
        """Initialize queue manager."""
        self.redis_conn = redis.from_url(settings.redis_url)
        self.ingest_queue = Queue("ingest", connection=self.redis_conn)
        self.maintenance_queue = Queue("maintenance", connection=self.redis_conn)
        
    def enqueue_ingest_job(
        self,
        tenant_id: str,
        user_id: str,
        job_type: JobType,
        payload: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> str:
        """Enqueue an ingest job.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            job_type: Type of ingest job
            payload: Job payload data
            timeout: Job timeout in seconds
            
        Returns:
            Job ID
        """
        try:
            # Create job record in database
            job_id = generate_ulid()
            job = Job(
                id=job_id,
                tenant_id=tenant_id,
                user_id=user_id,
                job_type=job_type,
                status=JobStatus.PENDING,
                payload=payload
            )
            
            with get_db_session() as session:
                session.add(job)
                session.commit()
                
            # Enqueue RQ job
            rq_job = self.ingest_queue.enqueue(
                "engram.workers.worker.process_ingest_job",
                job_id,
                timeout=timeout or settings.job_timeout,
                job_timeout=timeout or settings.job_timeout,
                result_ttl=86400,  # Keep results for 24 hours
                failure_ttl=86400,  # Keep failures for 24 hours
            )
            
            logger.info(
                "Enqueued ingest job",
                extra={
                    "job_id": job_id,
                    "rq_job_id": rq_job.id,
                    "job_type": job_type.value,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                }
            )
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue ingest job: {e}")
            raise

    def enqueue_maintenance_job(
        self,
        tenant_id: str,
        user_id: str,
        job_type: JobType,
        payload: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> str:
        """Enqueue a maintenance job.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            job_type: Type of maintenance job
            payload: Job payload data
            timeout: Job timeout in seconds
            
        Returns:
            Job ID
        """
        try:
            # Create job record in database
            job_id = generate_ulid()
            job = Job(
                id=job_id,
                tenant_id=tenant_id,
                user_id=user_id,
                job_type=job_type,
                status=JobStatus.PENDING,
                payload=payload
            )
            
            with get_db_session() as session:
                session.add(job)
                session.commit()
                
            # Enqueue RQ job
            rq_job = self.maintenance_queue.enqueue(
                "engram.workers.worker.process_maintenance_job",
                job_id,
                timeout=timeout or settings.job_timeout,
                job_timeout=timeout or settings.job_timeout,
                result_ttl=86400,
                failure_ttl=86400,
            )
            
            logger.info(
                "Enqueued maintenance job",
                extra={
                    "job_id": job_id,
                    "rq_job_id": rq_job.id,
                    "job_type": job_type.value,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                }
            )
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue maintenance job: {e}")
            raise

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status from database.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dict or None if not found
        """
        try:
            with get_db_session() as session:
                job = session.query(Job).filter(Job.id == job_id).first()
                if job:
                    return job.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[float] = None,
        error: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update job status in database.
        
        Args:
            job_id: Job ID
            status: New status
            progress: Progress (0.0 to 1.0)
            error: Error message if failed
            result: Job result data
            
        Returns:
            True if updated successfully
        """
        try:
            with get_db_session() as session:
                job = session.query(Job).filter(Job.id == job_id).first()
                if not job:
                    logger.warning(f"Job not found: {job_id}")
                    return False
                    
                job.status = status
                if progress is not None:
                    job.progress = progress
                if error is not None:
                    job.error = error
                if result is not None:
                    job.result = result
                    
                if status == JobStatus.RUNNING and not job.started_at:
                    job.started_at = datetime.utcnow()
                elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    job.completed_at = datetime.utcnow()
                    
                session.commit()
                
                logger.debug(
                    "Updated job status",
                    extra={
                        "job_id": job_id,
                        "status": status.value,
                        "progress": progress,
                    }
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return False

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics.
        
        Returns:
            Queue statistics
        """
        try:
            return {
                "ingest_queue": {
                    "pending": len(self.ingest_queue),
                    "failed": len(self.ingest_queue.failed_job_registry),
                    "workers": len(Worker.all(connection=self.redis_conn)),
                },
                "maintenance_queue": {
                    "pending": len(self.maintenance_queue),
                    "failed": len(self.maintenance_queue.failed_job_registry),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}


@lru_cache()
def get_queue_manager() -> QueueManager:
    """Get cached queue manager instance."""
    return QueueManager()
