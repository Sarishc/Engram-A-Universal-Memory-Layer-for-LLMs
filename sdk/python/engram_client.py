"""Engram Python SDK client."""

import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

import httpx
from pydantic import BaseModel


class MemoryResponse(BaseModel):
    """Memory response model."""
    id: str
    tenant_id: str
    user_id: str
    text: str
    metadata: Dict[str, Any]
    modality: str
    source_uri: Optional[str]
    importance: float
    created_at: str


class ChatResponse(BaseModel):
    """Chat response model."""
    reply: str
    memories_used: List[Dict[str, Any]]
    trace_id: str


class GraphNode(BaseModel):
    """Graph node model."""
    id: str
    label: str
    type: str
    description: Optional[str]


class GraphEdge(BaseModel):
    """Graph edge model."""
    id: str
    src_id: str
    dst_id: str
    relation: str
    weight: float


class GraphResponse(BaseModel):
    """Graph response model."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class EngramClient:
    """Engram Python SDK client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        """Initialize Engram client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of the Engram API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Engram API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data
        """
        url = f"{self.base_url}/v1{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self._headers,
                json=data,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def upsert(
        self,
        tenant_id: str,
        user_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> MemoryResponse:
        """Upsert a memory.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            text: Memory text
            metadata: Optional metadata
            importance: Memory importance (0.0 to 1.0)
            
        Returns:
            Created memory
        """
        data = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "text": text,
            "metadata": metadata or {},
            "importance": importance,
        }
        
        response = await self._request("POST", "/memories/upsert", data)
        return MemoryResponse(**response)

    async def ingest_url(
        self,
        tenant_id: str,
        user_id: str,
        url: str,
        content_type: str = "web"
    ) -> Dict[str, str]:
        """Ingest content from URL.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            url: URL to ingest
            content_type: Content type (web, pdf, image, video)
            
        Returns:
            Job information
        """
        data = {
            "url": url,
            "type": content_type,
        }
        
        response = await self._request("POST", "/ingest/url", data)
        return response

    async def ingest_file(
        self,
        tenant_id: str,
        user_id: str,
        file_path: str,
        content_type: str = "text"
    ) -> Dict[str, str]:
        """Ingest content from file.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            file_path: Path to file
            content_type: Content type (pdf, image, video, chat)
            
        Returns:
            Job information
        """
        # This is a simplified implementation
        # In a real implementation, you would handle file uploads
        raise NotImplementedError("File upload not implemented in this example")

    async def ingest_chat(
        self,
        tenant_id: str,
        user_id: str,
        platform: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Ingest chat messages.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            platform: Chat platform (slack, discord, json, generic)
            messages: List of chat messages
            metadata: Optional metadata
            
        Returns:
            Job information
        """
        data = {
            "platform": platform,
            "items": messages,
            "metadata": metadata or {},
        }
        
        response = await self._request("POST", "/ingest/chat", data)
        return response

    async def retrieve(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        top_k: int = 10,
        modalities: Optional[List[str]] = None
    ) -> List[MemoryResponse]:
        """Retrieve memories.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            query: Search query
            top_k: Number of results to return
            modalities: Filter by modalities
            
        Returns:
            List of memories
        """
        data = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "query": query,
            "top_k": top_k,
            "modalities": modalities,
        }
        
        response = await self._request("POST", "/memories/retrieve", data)
        return [MemoryResponse(**memory) for memory in response.get("memories", [])]

    async def chat(
        self,
        tenant_id: str,
        user_id: str,
        messages: List[Dict[str, str]],
        retrieval_hints: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Chat with memories.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            messages: Chat messages
            retrieval_hints: Optional retrieval configuration
            
        Returns:
            Chat response
        """
        data = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "messages": messages,
            "retrieval_hints": retrieval_hints,
        }
        
        response = await self._request("POST", "/chat", data)
        return ChatResponse(**response)

    async def router_complete(
        self,
        tenant_id: str,
        user_id: str,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        retrieval_hints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Complete chat using router proxy.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            messages: Chat messages
            provider: LLM provider
            model: Model name
            retrieval_hints: Optional retrieval configuration
            
        Returns:
            Completion response
        """
        data = {
            "provider": provider,
            "model": model,
            "messages": messages,
            "retrieval_hints": retrieval_hints,
        }
        
        response = await self._request("POST", "/router/complete", data)
        return response

    async def graph_subgraph(
        self,
        tenant_id: str,
        user_id: str,
        seed_label: str,
        radius: int = 2
    ) -> GraphResponse:
        """Get graph subgraph.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            seed_label: Seed node label
            radius: Graph radius
            
        Returns:
            Graph data
        """
        params = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "seed_label": seed_label,
            "radius": radius,
        }
        
        response = await self._request("GET", "/graph/subgraph", params=params)
        return GraphResponse(**response)

    async def graph_search(
        self,
        tenant_id: str,
        user_id: str,
        entity: str
    ) -> List[GraphNode]:
        """Search graph entities.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            entity: Entity to search for
            
        Returns:
            List of matching nodes
        """
        params = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity": entity,
        }
        
        response = await self._request("GET", "/graph/search", params=params)
        return [GraphNode(**node) for node in response.get("nodes", [])]

    async def list_memories(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MemoryResponse]:
        """List memories.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            limit: Maximum number of memories
            offset: Number of memories to skip
            
        Returns:
            List of memories
        """
        params = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
        }
        
        response = await self._request("GET", "/admin/memories", params=params)
        return [MemoryResponse(**memory) for memory in response.get("memories", [])]

    async def processing_status(self, job_id: str) -> Dict[str, Any]:
        """Get processing job status.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status
        """
        params = {"job_id": job_id}
        response = await self._request("GET", "/processing/status", params=params)
        return response


# Synchronous wrapper for convenience
class EngramClientSync(EngramClient):
    """Synchronous wrapper for EngramClient."""

    def __init__(self, *args, **kwargs):
        """Initialize synchronous client."""
        super().__init__(*args, **kwargs)
        self._loop = None

    def _get_loop(self):
        """Get or create event loop."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _run_async(self, coro):
        """Run async coroutine synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(coro)

    def upsert(self, *args, **kwargs):
        """Synchronous upsert."""
        return self._run_async(super().upsert(*args, **kwargs))

    def ingest_url(self, *args, **kwargs):
        """Synchronous URL ingestion."""
        return self._run_async(super().ingest_url(*args, **kwargs))

    def ingest_chat(self, *args, **kwargs):
        """Synchronous chat ingestion."""
        return self._run_async(super().ingest_chat(*args, **kwargs))

    def retrieve(self, *args, **kwargs):
        """Synchronous retrieve."""
        return self._run_async(super().retrieve(*args, **kwargs))

    def chat(self, *args, **kwargs):
        """Synchronous chat."""
        return self._run_async(super().chat(*args, **kwargs))

    def router_complete(self, *args, **kwargs):
        """Synchronous router completion."""
        return self._run_async(super().router_complete(*args, **kwargs))

    def graph_subgraph(self, *args, **kwargs):
        """Synchronous graph subgraph."""
        return self._run_async(super().graph_subgraph(*args, **kwargs))

    def graph_search(self, *args, **kwargs):
        """Synchronous graph search."""
        return self._run_async(super().graph_search(*args, **kwargs))

    def list_memories(self, *args, **kwargs):
        """Synchronous list memories."""
        return self._run_async(super().list_memories(*args, **kwargs))

    def processing_status(self, *args, **kwargs):
        """Synchronous processing status."""
        return self._run_async(super().processing_status(*args, **kwargs))
