"""Enhanced memory API routes for comprehensive memory operations."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_

from engram.api.deps import get_memory_store, get_db_session
from engram.api.models import (
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryAskRequest,
    MemoryAskResponse,
    ProcessingStatusRequest,
    ProcessingStatusResponse,
    AnalyticsOverviewResponse,
    RetrieveResult,
)
from engram.core.memory_store import MemoryStore
from engram.database.models import Memory, UserMemoryStats
from engram.utils.logger import get_logger
from engram.utils.config import get_settings
from engram.api.router_routes import get_llm_provider

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/v1/memories", tags=["memories"])


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    request: MemorySearchRequest,
    memory_store: MemoryStore = Depends(get_memory_store),
) -> MemorySearchResponse:
    """Advanced memory search with filters and modalities."""
    try:
        # Build search query
        memories = memory_store.retrieve_memories(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            query=request.query,
            top_k=request.top_k,
        )
        
        # Apply additional filters
        filtered_memories = _apply_search_filters(
            memories, request.filters, request.modalities, 
            request.date_range, request.importance_threshold
        )
        
        # Convert to RetrieveResult objects
        results = []
        for memory in filtered_memories:
            results.append(RetrieveResult(
                memory_id=memory.get("memory_id", ""),
                text=memory.get("text", ""),
                score=memory.get("score", 0.0),
                metadata=memory.get("metadata", {}),
                importance=memory.get("importance", 0.5),
                created_at=memory.get("created_at", ""),
                last_accessed_at=memory.get("last_accessed_at", ""),
            ))
        
        return MemorySearchResponse(
            memories=results,
            total_found=len(results),
            query=request.query,
            filters_applied={
                "modalities": request.modalities,
                "date_range": request.date_range,
                "importance_threshold": request.importance_threshold,
                "filters": request.filters,
            }
        )
        
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=MemoryAskResponse)
async def ask_memories(
    request: MemoryAskRequest,
    memory_store: MemoryStore = Depends(get_memory_store),
) -> MemoryAskResponse:
    """Ask questions using memory context with AI."""
    try:
        # Retrieve relevant memories
        memories = memory_store.retrieve_memories(
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            query=request.question,
            top_k=request.max_memories,
        )
        
        # Build context from memories
        context = _build_memory_context(memories, request.include_sources)
        
        # Generate AI response
        answer, confidence = await _generate_ai_response(
            question=request.question,
            context=context,
            memories=memories
        )
        
        # Convert memories to RetrieveResult objects
        sources = []
        for memory in memories:
            sources.append(RetrieveResult(
                memory_id=memory.get("memory_id", ""),
                text=memory.get("text", ""),
                score=memory.get("score", 0.0),
                metadata=memory.get("metadata", {}),
                importance=memory.get("importance", 0.5),
                created_at=memory.get("created_at", ""),
                last_accessed_at=memory.get("last_accessed_at", ""),
            ))
        
        return MemoryAskResponse(
            answer=answer,
            sources_used=sources,
            confidence=confidence,
            query=request.question,
        )
        
    except Exception as e:
        logger.error(f"Error asking memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db_session),
) -> AnalyticsOverviewResponse:
    """Get analytics overview for a user."""
    try:
        # Get memory statistics
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
        
        return AnalyticsOverviewResponse(
            total_memories=total_memories,
            total_requests=0,  # Would need request tracking
            requests_last_24h=0,  # Would need request tracking
            p95_latency_ms=0.0,  # Would need latency tracking
            memory_types=memory_types,
            top_sources=sources_list,
            recent_activity=activity_list,
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processing/status", response_model=ProcessingStatusResponse)
async def get_processing_status(
    job_id: str = Query(..., description="Job ID"),
) -> ProcessingStatusResponse:
    """Get processing status for a job."""
    try:
        # This would integrate with the job queue system
        # For now, return a mock response
        return ProcessingStatusResponse(
            job_id=job_id,
            status="completed",
            progress=100,
            message="Job completed successfully",
            result={"memories_created": 5, "processing_time": 2.3},
        )
        
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _apply_search_filters(
    memories: List[Dict[str, Any]],
    filters: Optional[Dict[str, Any]],
    modalities: Optional[List[str]],
    date_range: Optional[Dict[str, str]],
    importance_threshold: Optional[float],
) -> List[Dict[str, Any]]:
    """Apply search filters to memories."""
    filtered = memories
    
    # Apply modality filter
    if modalities:
        filtered = [
            m for m in filtered 
            if m.get("metadata", {}).get("modality") in modalities
        ]
    
    # Apply importance threshold
    if importance_threshold is not None:
        filtered = [
            m for m in filtered 
            if m.get("importance", 0.0) >= importance_threshold
        ]
    
    # Apply date range filter
    if date_range:
        from datetime import datetime
        start_date = datetime.fromisoformat(date_range.get("start", ""))
        end_date = datetime.fromisoformat(date_range.get("end", ""))
        
        filtered = [
            m for m in filtered
            if start_date <= datetime.fromisoformat(m.get("created_at", "")) <= end_date
        ]
    
    # Apply custom filters
    if filters:
        for key, value in filters.items():
            if key == "source_uri":
                filtered = [m for m in filtered if m.get("metadata", {}).get("source_uri") == value]
            elif key == "tags":
                filtered = [m for m in filtered if value in m.get("metadata", {}).get("tags", [])]
    
    return filtered


def _build_memory_context(memories: List[Dict[str, Any]], include_sources: bool) -> str:
    """Build context string from memories."""
    if not memories:
        return ""
    
    context_parts = ["[MEMORY CONTEXT START]"]
    
    for i, memory in enumerate(memories, 1):
        text = memory.get("text", "")
        modality = memory.get("metadata", {}).get("modality", "text")
        source_uri = memory.get("metadata", {}).get("source_uri", "")
        
        if include_sources and source_uri:
            context_parts.append(f"{i}. [{modality.upper()}] {text} (Source: {source_uri})")
        else:
            context_parts.append(f"{i}. [{modality.upper()}] {text}")
    
    context_parts.append("[MEMORY CONTEXT END]")
    
    return "\n".join(context_parts)


async def _generate_ai_response(
    question: str,
    context: str,
    memories: List[Dict[str, Any]]
) -> tuple[str, float]:
    """Generate AI response using LLM."""
    try:
        # Build prompt
        system_prompt = """You are a helpful AI assistant with access to the user's personal knowledge base. 
        Use the provided memory context to answer the user's question accurately and helpfully.
        If the memory context is relevant to the question, reference it appropriately.
        If you cannot find relevant information in the memories, say so clearly.
        Be conversational and helpful."""
        
        user_prompt = f"""Question: {question}

Memory Context:
{context}

Please provide a helpful answer based on the available memory context."""
        
        # Get LLM provider
        llm_provider = get_llm_provider(settings.default_llm_provider)
        
        # Generate response
        response = await llm_provider.generate(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        # Calculate confidence based on memory relevance
        avg_score = sum(m.get("score", 0.0) for m in memories) / len(memories) if memories else 0.0
        confidence = min(avg_score * 1.2, 1.0)  # Boost confidence slightly
        
        return response, confidence
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again.", 0.0
