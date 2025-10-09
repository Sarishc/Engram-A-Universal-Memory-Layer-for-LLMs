"""Chat API routes for RAG-powered conversations."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from engram.utils.logger import get_logger
from engram.utils.config import get_settings
from engram.core.memory_store import MemoryStore
from engram.core.retrieval import RetrievalEngine
from engram.providers.multimodal_registry import embeddings_registry

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/v1/chat", tags=["chat"])

# Initialize services
memory_store = MemoryStore()
retrieval_engine = RetrievalEngine()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class RetrievalHints(BaseModel):
    """Retrieval hints for chat."""
    modalities: Optional[List[str]] = Field(default=None, description="Content modalities to search")
    k: int = Field(default=10, description="Number of memories to retrieve")


class ChatRequest(BaseModel):
    """Chat request model."""
    tenant_id: str = Field(..., description="Tenant identifier")
    user_id: str = Field(..., description="User identifier")
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    retrieval_hints: Optional[RetrievalHints] = Field(default=None, description="Retrieval configuration")


class ChatResponse(BaseModel):
    """Chat response model."""
    message: ChatMessage = Field(..., description="Assistant response")
    memories_used: List[Dict[str, Any]] = Field(..., description="Memories used for response")
    context_window_used: int = Field(..., description="Context window tokens used")
    retrieval_metadata: Dict[str, Any] = Field(..., description="Retrieval metadata")


class ChatAPI:
    """Chat API handler for RAG conversations."""
    
    def __init__(self):
        """Initialize chat API."""
        self.memory_store = memory_store
        self.retrieval_engine = retrieval_engine
    
    async def chat(
        self,
        tenant_id: str,
        user_id: str,
        messages: List[ChatMessage],
        retrieval_hints: Optional[RetrievalHints] = None
    ) -> ChatResponse:
        """Handle a chat request with RAG.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            messages: Conversation messages
            retrieval_hints: Optional retrieval configuration
            
        Returns:
            Chat response with assistant message and context
        """
        try:
            # Get the last user message
            user_messages = [msg for msg in messages if msg.role == "user"]
            if not user_messages:
                raise HTTPException(status_code=400, detail="No user messages found")
            
            last_user_message = user_messages[-1].content
            
            # Retrieve relevant memories
            memories = await self._retrieve_memories(
                tenant_id=tenant_id,
                user_id=user_id,
                query=last_user_message,
                retrieval_hints=retrieval_hints
            )
            
            # Build context from memories
            context = self._build_memory_context(memories)
            
            # Generate response using LLM
            assistant_message = await self._generate_response(
                messages=messages,
                memory_context=context
            )
            
            # Store the conversation turn as memory
            await self._store_conversation_memory(
                tenant_id=tenant_id,
                user_id=user_id,
                messages=messages[-2:]  # Store last exchange
            )
            
            return ChatResponse(
                message=assistant_message,
                memories_used=memories,
                context_window_used=len(context.split()),
                retrieval_metadata={
                    "query": last_user_message,
                    "memories_retrieved": len(memories),
                    "modalities": retrieval_hints.modalities if retrieval_hints else None,
                }
            )
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _retrieve_memories(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        retrieval_hints: Optional[RetrievalHints] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for the query.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            query: Search query
            retrieval_hints: Optional retrieval configuration
            
        Returns:
            List of relevant memories
        """
        try:
            # Get retrieval parameters
            top_k = retrieval_hints.k if retrieval_hints else settings.chat_max_memories
            modalities = retrieval_hints.modalities if retrieval_hints else None
            
            # Perform hybrid retrieval
            results = self.retrieval_engine.retrieve(
                tenant_id=tenant_id,
                user_id=user_id,
                query=query,
                top_k=top_k,
                modalities=modalities
            )
            
            # Format results
            memories = []
            for result in results:
                memories.append({
                    "memory_id": result["memory_id"],
                    "text": result["text"],
                    "score": result["score"],
                    "modality": result.get("metadata", {}).get("modality", "text"),
                    "source_uri": result.get("metadata", {}).get("source_uri"),
                    "importance": result.get("importance", 0.5),
                    "created_at": result.get("created_at"),
                })
            
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
    
    def _build_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Build memory context string from retrieved memories.
        
        Args:
            memories: List of retrieved memories
            
        Returns:
            Formatted memory context
        """
        if not memories:
            return ""
        
        context_parts = ["[MEMORY CONTEXT START]"]
        
        for i, memory in enumerate(memories, 1):
            modality = memory.get("modality", "text")
            source_uri = memory.get("source_uri", "")
            text = memory.get("text", "")
            
            # Format memory entry
            if source_uri:
                context_parts.append(f"- {modality.upper()}: {text} (Source: {source_uri})")
            else:
                context_parts.append(f"- {modality.upper()}: {text}")
        
        context_parts.append("[MEMORY CONTEXT END]")
        
        return "\n".join(context_parts)
    
    async def _generate_response(
        self,
        messages: List[ChatMessage],
        memory_context: str
    ) -> ChatMessage:
        """Generate assistant response using LLM.
        
        Args:
            messages: Conversation messages
            memory_context: Memory context string
            
        Returns:
            Assistant message
        """
        try:
            # Build prompt with memory context
            system_prompt = """You are a helpful AI assistant with access to the user's personal knowledge base. 
            Use the provided memory context to give informed, relevant responses. 
            If the memory context is relevant to the user's question, reference it appropriately.
            Be conversational and helpful."""
            
            # Add memory context to system prompt
            if memory_context:
                system_prompt += f"\n\nMemory Context:\n{memory_context}"
            
            # Format messages for LLM
            formatted_messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Get LLM provider
            from engram.providers import get_llm_provider
            llm_provider = get_llm_provider(settings.default_llm_provider)
            
            # Generate response
            response = await llm_provider.generate(
                messages=formatted_messages,
                temperature=settings.chat_temperature,
                max_tokens=settings.chat_context_window // 2,  # Leave room for context
            )
            
            return ChatMessage(
                role="assistant",
                content=response
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            return ChatMessage(
                role="assistant",
                content="I apologize, but I'm having trouble generating a response right now. Please try again."
            )
    
    async def _store_conversation_memory(
        self,
        tenant_id: str,
        user_id: str,
        messages: List[ChatMessage]
    ):
        """Store conversation turn as memory.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            messages: Recent conversation messages
        """
        try:
            # Create conversation text
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}" for msg in messages
            ])
            
            # Store as chat memory
            self.memory_store.upsert_memories(
                tenant_id=tenant_id,
                user_id=user_id,
                texts=[conversation_text],
                embeddings=[],  # Will be generated
                metadata_list=[{
                    "modality": "chat",
                    "source_type": "conversation",
                    "message_count": len(messages),
                }],
                importance=0.3,  # Lower importance for chat logs
            )
            
        except Exception as e:
            logger.warning(f"Error storing conversation memory: {e}")


# Initialize chat API
chat_api = ChatAPI()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle a chat request with RAG.
    
    Args:
        request: Chat request with messages and retrieval hints
        
    Returns:
        Chat response with assistant message and context
    """
    return await chat_api.chat(
        tenant_id=request.tenant_id,
        user_id=request.user_id,
        messages=request.messages,
        retrieval_hints=request.retrieval_hints
    )
