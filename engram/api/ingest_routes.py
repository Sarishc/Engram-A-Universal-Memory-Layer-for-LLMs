"""Ingestion API routes for multimodal content."""

import os
import tempfile
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel, Field

from engram.utils.logger import get_logger
from engram.database.models import ModalityType
from engram.database.jobs import JobType
from engram.workers.queue import get_queue_manager
from engram.api.middleware import require_scope, get_current_tenant_id, get_current_user_id

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/ingest", tags=["ingestion"])
queue_manager = get_queue_manager()


class IngestURLRequest(BaseModel):
    """Request model for URL ingestion."""
    url: str = Field(..., description="URL to ingest")
    type: str = Field(..., description="Content type (web, pdf, image, video)")
    chunk_size: int = Field(default=512, description="Chunk size in tokens")
    chunk_overlap: int = Field(default=76, description="Chunk overlap in tokens")


class IngestChatRequest(BaseModel):
    """Request model for chat ingestion."""
    platform: str = Field(..., description="Chat platform (slack, discord, json, generic)")
    items: List[dict] = Field(..., description="List of chat messages")
    metadata: Optional[dict] = Field(default=None, description="Optional metadata")


class JobResponse(BaseModel):
    """Response model for job-based operations."""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")


@router.post("/url", response_model=JobResponse)
@require_scope("ingest:write")
async def ingest_url(request: IngestURLRequest):
    """Ingest content from a URL.
    
    Args:
        request: URL ingestion request
        
    Returns:
        Job information
    """
    try:
        # Validate content type
        try:
            modality = ModalityType(request.type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type: {request.type}. Must be one of: {[t.value for t in ModalityType]}"
            )
        
        # Get tenant and user from auth context
        tenant_id = get_current_tenant_id(request)
        user_id = get_current_user_id(request)
        
        if not tenant_id or not user_id:
            raise HTTPException(status_code=400, detail="Authentication required")
        
        logger.info(f"Queuing {modality.value} content ingestion from URL: {request.url}")
        
        # Create job payload
        payload = {
            "url": request.url,
            "type": request.type,
            "chunk_size": request.chunk_size,
            "chunk_overlap": request.chunk_overlap,
        }
        
        # Enqueue job
        job_id = queue_manager.enqueue_ingest_job(
            tenant_id=tenant_id,
            user_id=user_id,
            job_type=JobType.INGEST_URL,
            payload=payload
        )
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="URL ingestion job queued successfully"
        )
        
    except Exception as e:
        logger.error(f"Error queuing URL ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file", response_model=JobResponse)
@require_scope("ingest:write")
async def ingest_file(
    request,
    type: str = Form(...),
    file: UploadFile = File(...),
    chunk_size: int = Form(default=512),
    chunk_overlap: int = Form(default=76),
):
    """Ingest content from an uploaded file.
    
    Args:
        request: FastAPI request object
        type: Content type (pdf, image, video, chat)
        file: Uploaded file
        chunk_size: Chunk size in tokens
        chunk_overlap: Chunk overlap in tokens
        
    Returns:
        Job information
    """
    try:
        # Validate content type
        try:
            modality = ModalityType(type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type: {type}. Must be one of: {[t.value for t in ModalityType]}"
            )
        
        # Validate file type
        allowed_extensions = {
            ModalityType.PDF: ['.pdf'],
            ModalityType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            ModalityType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            ModalityType.CHAT: ['.json', '.txt'],
        }
        
        file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_extension not in allowed_extensions.get(modality, []):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for {type}: {file_extension}"
            )
        
        # Get tenant and user from auth context
        tenant_id = get_current_tenant_id(request)
        user_id = get_current_user_id(request)
        
        if not tenant_id or not user_id:
            raise HTTPException(status_code=400, detail="Authentication required")
        
        logger.info(f"Queuing {modality.value} file ingestion: {file.filename}")
        
        # Save file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Create job payload
        payload = {
            "file_path": tmp_file_path,
            "filename": file.filename,
            "type": type,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
        
        # Enqueue job
        job_id = queue_manager.enqueue_ingest_job(
            tenant_id=tenant_id,
            user_id=user_id,
            job_type=JobType.INGEST_FILE,
            payload=payload
        )
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="File ingestion job queued successfully"
        )
        
    except Exception as e:
        logger.error(f"Error queuing file ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=JobResponse)
@require_scope("ingest:write")
async def ingest_chat(request: IngestChatRequest):
    """Ingest chat content.
    
    Args:
        request: Chat ingestion request
        
    Returns:
        Job information
    """
    try:
        # Get tenant and user from auth context
        tenant_id = get_current_tenant_id(request)
        user_id = get_current_user_id(request)
        
        if not tenant_id or not user_id:
            raise HTTPException(status_code=400, detail="Authentication required")
        
        logger.info(f"Queuing {request.platform} chat ingestion with {len(request.items)} messages")
        
        # Create job payload
        payload = {
            "platform": request.platform,
            "items": request.items,
            "metadata": request.metadata or {},
        }
        
        # Enqueue job
        job_id = queue_manager.enqueue_ingest_job(
            tenant_id=tenant_id,
            user_id=user_id,
            job_type=JobType.INGEST_CHAT,
            payload=payload
        )
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="Chat ingestion job queued successfully"
        )
        
    except Exception as e:
        logger.error(f"Error queuing chat ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
