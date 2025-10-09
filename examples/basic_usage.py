#!/usr/bin/env python3
"""Basic usage example for Engram API."""

import asyncio
import json
from typing import Dict, List

import httpx


class EngramClient:
    """Simple client for interacting with Engram API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_tenant(self, name: str) -> Dict:
        """Create a new tenant."""
        response = await self.client.post(
            f"{self.base_url}/v1/tenants",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()
    
    async def upsert_memories(
        self,
        tenant_id: str,
        user_id: str,
        texts: List[str],
        metadata: List[Dict] = None,
        importance: List[float] = None,
    ) -> Dict:
        """Upsert memories for a user."""
        payload = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "texts": texts,
        }
        
        if metadata:
            payload["metadata"] = metadata
        if importance:
            payload["importance"] = importance
        
        response = await self.client.post(
            f"{self.base_url}/v1/memories/upsert",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def retrieve_memories(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """Retrieve relevant memories."""
        response = await self.client.post(
            f"{self.base_url}/v1/memories/retrieve",
            json={
                "tenant_id": tenant_id,
                "user_id": user_id,
                "query": query,
                "top_k": top_k,
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def inject_context(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        prompt: str,
        max_memories: int = 3,
    ) -> Dict:
        """Inject context into a prompt."""
        response = await self.client.post(
            f"{self.base_url}/v1/context/inject",
            json={
                "tenant_id": tenant_id,
                "user_id": user_id,
                "query": query,
                "prompt": prompt,
                "max_memories": max_memories,
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Demonstrate basic Engram usage."""
    client = EngramClient()
    
    try:
        print("🧠 Engram Basic Usage Example")
        print("=" * 50)
        
        # 1. Create a tenant
        print("\n1. Creating tenant...")
        tenant = await client.create_tenant("demo-app")
        tenant_id = tenant["id"]
        user_id = "user123"
        print(f"✅ Created tenant: {tenant['name']} (ID: {tenant_id})")
        
        # 2. Store some memories
        print("\n2. Storing memories...")
        memories_data = {
            "texts": [
                "User prefers dark mode in applications",
                "User is interested in machine learning and AI",
                "User works as a software engineer at a tech company",
                "User enjoys hiking and outdoor activities",
                "User has a dog named Max",
            ],
            "metadata": [
                {"source": "preferences", "category": "ui"},
                {"source": "interests", "category": "tech"},
                {"source": "profile", "category": "work"},
                {"source": "interests", "category": "hobbies"},
                {"source": "personal", "category": "pets"},
            ],
            "importance": [0.8, 0.9, 0.7, 0.6, 0.5],
        }
        
        upsert_result = await client.upsert_memories(
            tenant_id=tenant_id,
            user_id=user_id,
            **memories_data
        )
        print(f"✅ Stored {upsert_result['count']} memories")
        
        # 3. Retrieve relevant memories
        print("\n3. Retrieving relevant memories...")
        queries = [
            "What does the user like?",
            "Tell me about their work",
            "What are their hobbies?",
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            memories = await client.retrieve_memories(
                tenant_id=tenant_id,
                user_id=user_id,
                query=query,
                top_k=3,
            )
            
            for i, memory in enumerate(memories, 1):
                print(f"  {i}. [{memory['score']:.3f}] {memory['text']}")
        
        # 4. Context injection
        print("\n4. Context injection example...")
        original_prompt = "Based on the user's preferences, suggest a new feature for our app."
        
        context_result = await client.inject_context(
            tenant_id=tenant_id,
            user_id=user_id,
            query="user preferences",
            prompt=original_prompt,
            max_memories=2,
        )
        
        print(f"\nOriginal prompt:\n{original_prompt}")
        print(f"\nInjected prompt:\n{context_result['injected_prompt']}")
        
        print(f"\nMemories used ({len(context_result['memories_used'])}):")
        for memory in context_result['memories_used']:
            print(f"  - {memory['text']}")
        
        # 5. Show statistics
        print("\n5. Getting service statistics...")
        try:
            stats_response = await client.client.get(f"{client.base_url}/v1/stats")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Service stats:")
                print(f"   Total tenants: {stats['total_tenants']}")
                print(f"   Total memories: {stats['total_memories']}")
                print(f"   Active memories: {stats['active_memories']}")
                print(f"   Vector provider: {stats['vector_provider']}")
                print(f"   Embeddings provider: {stats['embeddings_provider']}")
        except Exception as e:
            print(f"⚠️  Could not fetch stats: {e}")
        
        print("\n🎉 Basic usage example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
