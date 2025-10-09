"""Router proxy API routes for LLM completion with memory context."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from engram.utils.logger import get_logger
from engram.core.retrieval import RetrievalEngine
from engram.providers.base_provider import LLMProvider
from engram.providers.openai_provider import OpenAILLMProvider
from engram.providers.anthropic_provider import AnthropicLLMProvider
from engram.providers.google_provider import GoogleLLMProvider
from engram.api.middleware import require_scope, get_current_tenant_id, get_current_user_id

logger = get_logger(__name__)
router = APIRouter(prefix="/v1/router", tags=["router"])


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")


class RetrievalHints(BaseModel):
    """Retrieval hints for memory search."""
    modalities: Optional[List[str]] = Field(None, description="Filter by modalities")
    k: int = Field(default=10, description="Number of memories to retrieve")
    importance_min: Optional[float] = Field(None, description="Minimum importance threshold")


class RouterCompleteRequest(BaseModel):
    """Request model for router completion."""
    provider: Optional[str] = Field(None, description="LLM provider (openai, anthropic, google)")
    model: Optional[str] = Field(None, description="Model name")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    retrieval_hints: Optional[RetrievalHints] = Field(None, description="Retrieval configuration")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")


class RouterCompleteResponse(BaseModel):
    """Response model for router completion."""
    output: str = Field(..., description="Generated response")
    memories_used: List[Dict[str, Any]] = Field(..., description="Memories used for context")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")
    trace_id: str = Field(..., description="Request trace identifier")


def get_llm_provider(provider_name: str, model: Optional[str] = None) -> LLMProvider:
    """Get LLM provider instance.
    
    Args:
        provider_name: Provider name
        model: Optional model name
        
    Returns:
        LLM provider instance
    """
    provider_name = provider_name.lower() if provider_name else "openai"
    
    if provider_name == "openai":
        return OpenAILLMProvider(model=model)
    elif provider_name == "anthropic":
        return AnthropicLLMProvider(model=model)
    elif provider_name == "google":
        return GoogleLLMProvider(model=model)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


@router.post("/complete", response_model=RouterCompleteResponse)
@require_scope("router:call")
async def router_complete(request: RouterCompleteRequest):
    """Complete chat using LLM provider with memory context.
    
    Args:
        request: Router completion request
        
    Returns:
        Completion result with memory context
    """
    try:
        # Get tenant and user from auth context
        tenant_id = get_current_tenant_id(request)
        user_id = get_current_user_id(request)
        
        if not tenant_id or not user_id:
            raise HTTPException(status_code=400, detail="Authentication required")
        
        # Extract last user message for retrieval
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user messages found")
        
        last_user_message = user_messages[-1].content
        
        # Retrieve relevant memories
        retrieval_engine = RetrievalEngine()
        retrieval_hints = request.retrieval_hints
        
        modalities = None
        top_k = 10
        if retrieval_hints:
            modalities = retrieval_hints.modalities
            top_k = retrieval_hints.k
        
        memories = retrieval_engine.retrieve(
            tenant_id=tenant_id,
            user_id=user_id,
            query=last_user_message,
            top_k=top_k,
            modalities=modalities
        )
        
        # Build memory context
        memory_context = ""
        if memories:
            memory_context = "\n\n[MEMORY CONTEXT START]\n"
            for i, memory in enumerate(memories, 1):
                modality = memory.get("modality", "text")
                text = memory.get("text", "")
                source = memory.get("source_uri", "")
                
                # Truncate long text
                if len(text) > 200:
                    text = text[:200] + "..."
                
                memory_context += f"- {i}. [{modality.upper()}] {text}"
                if source:
                    memory_context += f" (from: {source})"
                memory_context += "\n"
            
            memory_context += "[MEMORY CONTEXT END]\n"
        
        # Build system message with memory context
        system_message = "You are a helpful AI assistant with access to the user's personal memory bank. "
        system_message += "Use the provided memory context to give more relevant and personalized responses. "
        system_message += "If the memory context is not relevant to the current question, you can ignore it. "
        system_message += "Always be helpful, accurate, and respectful."
        
        if memory_context:
            system_message += memory_context
        
        # Prepare messages for LLM
        llm_messages = [
            {"role": "system", "content": system_message}
        ] + [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Get LLM provider
        llm_provider = get_llm_provider(request.provider, request.model)
        
        # Generate completion
        response = llm_provider.complete(
            messages=llm_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Extract response content and usage
        output = response.get("content", "")
        usage = response.get("usage", {})
        
        # Generate trace ID (simplified)
        import uuid
        trace_id = str(uuid.uuid4())
        
        logger.info(
            "Router completion completed",
            extra={
                "tenant_id": tenant_id,
                "user_id": user_id,
                "provider": request.provider,
                "model": request.model,
                "memories_used": len(memories),
                "trace_id": trace_id,
                "usage": usage,
            }
        )
        
        return RouterCompleteResponse(
            output=output,
            memories_used=memories,
            usage=usage,
            trace_id=trace_id,
        )
        
    except Exception as e:
        logger.error(f"Router completion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Completion failed: {str(e)}")
