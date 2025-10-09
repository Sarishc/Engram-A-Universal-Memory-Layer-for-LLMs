#!/usr/bin/env python3
"""Example script demonstrating multimodal ingestion with Engram."""

import asyncio
import sys
import os

# Add the SDK to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python"))

from engram_client import EngramClient


async def main():
    """Demonstrate multimodal ingestion."""
    # Initialize client
    client = EngramClient(
        api_key="your-api-key-here",  # Replace with actual API key
        base_url="http://localhost:8000"
    )
    
    tenant_id = "tenant_123"
    user_id = "user_456"
    
    print("🚀 Engram Multimodal Ingestion Demo")
    print("=" * 50)
    
    # 1. Basic memory upsert
    print("\n1. Upserting a basic memory...")
    memory = await client.upsert(
        tenant_id=tenant_id,
        user_id=user_id,
        text="I learned about machine learning today. Neural networks are fascinating!",
        metadata={"source": "demo", "topic": "machine learning"},
        importance=0.8
    )
    print(f"✅ Created memory: {memory.id}")
    
    # 2. URL ingestion
    print("\n2. Ingesting content from URL...")
    url_job = await client.ingest_url(
        tenant_id=tenant_id,
        user_id=user_id,
        url="https://example.com/article",
        content_type="web"
    )
    print(f"✅ URL ingestion job queued: {url_job['job_id']}")
    
    # 3. Chat ingestion
    print("\n3. Ingesting chat messages...")
    chat_messages = [
        {
            "user": "alice",
            "text": "Hey team, I found this interesting article about AI",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "user": "bob", 
            "text": "Thanks Alice! That's really helpful for our project",
            "timestamp": "2024-01-15T10:05:00Z"
        }
    ]
    
    chat_job = await client.ingest_chat(
        tenant_id=tenant_id,
        user_id=user_id,
        platform="slack",
        messages=chat_messages,
        metadata={"channel": "general", "workspace": "demo"}
    )
    print(f"✅ Chat ingestion job queued: {chat_job['job_id']}")
    
    # 4. Check job status
    print("\n4. Checking job status...")
    status = await client.processing_status(url_job['job_id'])
    print(f"📊 Job status: {status['status']} (progress: {status.get('progress', 0):.1%})")
    
    # 5. Retrieve memories
    print("\n5. Retrieving memories...")
    memories = await client.retrieve(
        tenant_id=tenant_id,
        user_id=user_id,
        query="machine learning",
        top_k=5
    )
    print(f"🔍 Found {len(memories)} memories:")
    for memory in memories:
        print(f"  - {memory.text[:100]}... (importance: {memory.importance})")
    
    # 6. Chat with memories
    print("\n6. Chatting with memories...")
    chat_response = await client.chat(
        tenant_id=tenant_id,
        user_id=user_id,
        messages=[
            {"role": "user", "content": "What did I learn about machine learning?"}
        ]
    )
    print(f"💬 Assistant: {chat_response.reply}")
    print(f"📚 Used {len(chat_response.memories_used)} memories")
    
    # 7. Graph exploration
    print("\n7. Exploring knowledge graph...")
    try:
        graph = await client.graph_subgraph(
            tenant_id=tenant_id,
            user_id=user_id,
            seed_label="machine learning",
            radius=2
        )
        print(f"🕸️  Found {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        for node in graph.nodes[:3]:  # Show first 3 nodes
            print(f"  - {node.label} ({node.type})")
    except Exception as e:
        print(f"⚠️  Graph not available: {e}")
    
    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
