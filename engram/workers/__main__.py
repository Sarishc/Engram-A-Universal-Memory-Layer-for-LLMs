"""RQ worker entrypoint."""

import os
import sys
from rq import Worker, Connection
import redis

from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def main():
    """Main worker entrypoint."""
    logger.info("Starting RQ worker")
    
    # Connect to Redis
    redis_conn = redis.from_url(settings.redis_url)
    
    # Create worker for ingest and maintenance queues
    worker = Worker(['ingest', 'maintenance'], connection=redis_conn)
    
    logger.info("Worker ready, listening for jobs...")
    worker.work()


if __name__ == "__main__":
    main()
