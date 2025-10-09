"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class TenantCreate(BaseModel):
    """Request model for creating a tenant."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Tenant name")


class TenantOut(BaseModel):
    """Response model for tenant information."""
    
    id: str = Field(..., description="Tenant ID")
    name: str = Field(..., description="Tenant name")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class MemoryUpsertRequest(BaseModel):
    """Request model for upserting memories."""
    
    tenant_id: str = Field(..., description="Tenant ID")
    user_id: str = Field(..., description="User ID")
    texts: List[str] = Field(..., min_items=1, max_items=100, description="Memory texts")
    metadata: Optional[List[Dict[str, Any]]] = Field(None, description="Memory metadata")
    importance: Optional[List[float]] = Field(None, description="Importance scores (0.0-1.0)")
    
    @validator("texts")
    def validate_texts(cls, v):
        """Validate text lengths."""
        for text in v:
            if len(text) > 2048:
                raise ValueError("Text length cannot exceed 2048 characters")
            if not text.strip():
                raise ValueError("Text cannot be empty")
        return v
    
    @validator("importance")
    def validate_importance(cls, v):
        """Validate importance scores."""
        if v:
            for score in v:
                if not 0.0 <= score <= 1.0:
                    raise ValueError("Importance scores must be between 0.0 and 1.0")
        return v


class RetrieveRequest(BaseModel):
    """Request model for retrieving memories."""
    
    tenant_id: str = Field(..., description="Tenant ID")
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., min_length=1, max_length=1000, description="Query text")
    top_k: Optional[int] = Field(12, ge=1, le=100, description="Number of results to return")


class RetrieveResult(BaseModel):
    """Result model for retrieved memories."""
    
    memory_id: str = Field(..., description="Memory ID")
    text: str = Field(..., description="Memory text")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Memory metadata")
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance score")
    created_at: str = Field(..., description="Creation timestamp")
    last_accessed_at: str = Field(..., description="Last accessed timestamp")


class InjectRequest(BaseModel):
    """Request model for context injection."""
    
    tenant_id: str = Field(..., description="Tenant ID")
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., min_length=1, max_length=1000, description="Query text")
    prompt: str = Field(..., min_length=1, description="Original prompt")
    max_memories: Optional[int] = Field(6, ge=1, le=20, description="Maximum memories to inject")
    provider: Optional[str] = Field(None, description="LLM provider for completion")


class InjectResponse(BaseModel):
    """Response model for context injection."""
    
    injected_prompt: str = Field(..., description="Prompt with injected context")
    memories_used: List[RetrieveResult] = Field(..., description="Memories used for injection")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Service status")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")


class AdminMemoryListRequest(BaseModel):
    """Request model for admin memory listing."""
    
    tenant_id: str = Field(..., description="Tenant ID")
    user_id: Optional[str] = Field(None, description="User ID (optional)")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Maximum results")
    offset: Optional[int] = Field(0, ge=0, description="Number of results to skip")
    active_only: Optional[bool] = Field(True, description="Only return active memories")


class AdminMemoryListResponse(BaseModel):
    """Response model for admin memory listing."""
    
    memories: List[RetrieveResult] = Field(..., description="List of memories")
    total_count: int = Field(..., description="Total number of memories")
    limit: int = Field(..., description="Requested limit")
    offset: int = Field(..., description="Requested offset")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    timestamp: datetime = Field(..., description="Error timestamp")


class StatsResponse(BaseModel):
    """Response model for statistics."""
    
    total_tenants: int = Field(..., description="Total number of tenants")
    total_memories: int = Field(..., description="Total number of memories")
    active_memories: int = Field(..., description="Number of active memories")
    vector_provider: str = Field(..., description="Vector database provider")
    embeddings_provider: str = Field(..., description="Embeddings provider")
