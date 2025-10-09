"""API routes for the Engram service."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from engram.api.deps import get_memory_store
from engram.api.models import (
    TenantCreate,
    TenantOut,
    MemoryUpsertRequest,
    RetrieveRequest,
    RetrieveResult,
    InjectRequest,
    InjectResponse,
    AdminMemoryListRequest,
    AdminMemoryListResponse,
    StatsResponse,
)
from engram.core.memory_store import MemoryStore
from engram.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/tenants", response_model=TenantOut, tags=["tenants"])
async def create_tenant(
    tenant_data: TenantCreate,
    memory_store: MemoryStore = Depends(get_memory_store),
) -> TenantOut:
    """Create a new tenant."""
    try:
        tenant = memory_store.create_tenant(tenant_data.name)
        return TenantOut.from_orm(tenant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create tenant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tenants/{tenant_id}", response_model=TenantOut, tags=["tenants"])
async def get_tenant(
    tenant_id: str,
    memory_store: MemoryStore = Depends(get_memory_store),
) -> TenantOut:
    """Get tenant information."""
    tenant = memory_store.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return TenantOut.from_orm(tenant)


@router.post("/memories/upsert", tags=["memories"])
async def upsert_memories(
    request: MemoryUpsertRequest,
    memory_store: MemoryStore = Depends(get_memory_store),
) -> dict:
    """Upsert memories for a user."""
    try:
        memories = memory_store.upsert_memories(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            texts=request.texts,
            metadata_list=request.metadata,
            importance_list=request.importance,
        )
        
        return {
            "message": f"Successfully upserted {len(memories)} memories",
            "memory_ids": [memory.id for memory in memories],
            "count": len(memories),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upsert memories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/memories/retrieve", response_model=List[RetrieveResult], tags=["memories"])
async def retrieve_memories(
    request: RetrieveRequest,
    memory_store: MemoryStore = Depends(get_memory_store),
) -> List[RetrieveResult]:
    """Retrieve relevant memories for a query."""
    try:
        results = memory_store.retrieve_memories(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            query=request.query,
            top_k=request.top_k,
        )
        
        return [RetrieveResult(**result) for result in results]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve memories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/context/inject", response_model=InjectResponse, tags=["context"])
async def inject_context(
    request: InjectRequest,
    memory_store: MemoryStore = Depends(get_memory_store),
) -> InjectResponse:
    """Inject relevant memories into a prompt."""
    try:
        # Retrieve relevant memories
        memories = memory_store.retrieve_memories(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            query=request.query,
            top_k=request.max_memories,
        )
        
        # Create context block
        if memories:
            context_lines = []
            for memory in memories:
                context_lines.append(f"- {memory['text']}")
            
            context_block = "\n".join([
                "[MEMORY CONTEXT START]",
                *context_lines,
                "[MEMORY CONTEXT END]",
                "",
                request.prompt,
            ])
        else:
            context_block = request.prompt
        
        # Convert memories to RetrieveResult objects
        memory_results = [RetrieveResult(**memory) for memory in memories]
        
        return InjectResponse(
            injected_prompt=context_block,
            memories_used=memory_results,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to inject context: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/admin/memories", response_model=AdminMemoryListResponse, tags=["admin"])
async def list_memories(
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(None, description="User ID (optional)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    active_only: bool = Query(True, description="Only return active memories"),
    memory_store: MemoryStore = Depends(get_memory_store),
) -> AdminMemoryListResponse:
    """List memories (admin endpoint)."""
    try:
        memories = memory_store.list_memories(
            tenant_id=tenant_id,
            user_id=user_id,
            active_only=active_only,
            limit=limit,
            offset=offset,
        )
        
        # Convert to response format
        memory_results = []
        for memory in memories:
            memory_results.append(RetrieveResult(
                memory_id=memory.id,
                text=memory.text,
                score=0.0,  # No relevance score for listing
                metadata=memory.memory_metadata,
                importance=memory.importance,
                created_at=memory.created_at.isoformat(),
                last_accessed_at=memory.last_accessed_at.isoformat(),
            ))
        
        # Get total count (simplified - in production you'd want a separate count query)
        total_count = len(memory_results) + offset
        
        return AdminMemoryListResponse(
            memories=memory_results,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/admin/memories/{memory_id}", tags=["admin"])
async def delete_memory(
    memory_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
    memory_store: MemoryStore = Depends(get_memory_store),
) -> dict:
    """Delete a memory (admin endpoint)."""
    try:
        success = memory_store.delete_memory(
            memory_id=memory_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "message": "Memory deleted successfully",
            "memory_id": memory_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats", response_model=StatsResponse, tags=["admin"])
async def get_stats(
    memory_store: MemoryStore = Depends(get_memory_store),
) -> StatsResponse:
    """Get service statistics."""
    try:
        stats = memory_store.get_store_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
