#!/usr/bin/env python3
"""Example script demonstrating knowledge graph exploration with Engram."""

import asyncio
import sys
import os

# Add the SDK to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python"))

from engram_client import EngramClient


async def main():
    """Demonstrate knowledge graph exploration."""
    # Initialize client
    client = EngramClient(
        api_key="your-api-key-here",  # Replace with actual API key
        base_url="http://localhost:8000"
    )
    
    tenant_id = "tenant_123"
    user_id = "user_456"
    
    print("🕸️  Engram Knowledge Graph Demo")
    print("=" * 50)
    
    # First, let's add some sample memories with entities
    print("\n📝 Adding sample memories with entities...")
    
    sample_memories = [
        {
            "text": "Alice Johnson is the CEO of TechCorp. She founded the company in 2020 and has been leading the AI division.",
            "metadata": {"source": "company directory", "category": "people"},
            "importance": 0.9
        },
        {
            "text": "TechCorp is a leading AI company based in San Francisco. They specialize in machine learning and natural language processing.",
            "metadata": {"source": "company website", "category": "organization"},
            "importance": 0.8
        },
        {
            "text": "The AI division at TechCorp is working on a new project called Project Phoenix. It's focused on autonomous systems.",
            "metadata": {"source": "internal memo", "category": "project"},
            "importance": 0.7
        },
        {
            "text": "San Francisco is where our main office is located. We also have offices in New York and London.",
            "metadata": {"source": "company info", "category": "location"},
            "importance": 0.6
        },
        {
            "text": "Bob Smith is the lead engineer on Project Phoenix. He has 10 years of experience in machine learning.",
            "metadata": {"source": "team directory", "category": "people"},
            "importance": 0.8
        },
        {
            "text": "Machine learning is a core technology at TechCorp. We use TensorFlow and PyTorch for our models.",
            "metadata": {"source": "tech blog", "category": "technology"},
            "importance": 0.7
        }
    ]
    
    memory_ids = []
    for memory_data in sample_memories:
        memory = await client.upsert(
            tenant_id=tenant_id,
            user_id=user_id,
            text=memory_data["text"],
            metadata=memory_data["metadata"],
            importance=memory_data["importance"]
        )
        memory_ids.append(memory.id)
        print(f"✅ Added memory: {memory.id}")
    
    print(f"\n📊 Added {len(memory_ids)} memories")
    
    # Wait a moment for graph processing
    print("\n⏳ Waiting for graph processing...")
    await asyncio.sleep(2)
    
    # Explore the knowledge graph
    print("\n🔍 Exploring knowledge graph...")
    
    # 1. Search for entities
    search_terms = ["Alice Johnson", "TechCorp", "Project Phoenix", "San Francisco"]
    
    for term in search_terms:
        try:
            nodes = await client.graph_search(
                tenant_id=tenant_id,
                user_id=user_id,
                entity=term
            )
            
            print(f"\n🔎 Search for '{term}':")
            if nodes:
                for node in nodes:
                    print(f"  - {node.label} ({node.type})")
                    if node.description:
                        print(f"    Description: {node.description}")
            else:
                print("  No entities found")
                
        except Exception as e:
            print(f"❌ Search error for '{term}': {e}")
    
    # 2. Get subgraph around a specific entity
    print(f"\n🕸️  Getting subgraph around 'TechCorp'...")
    try:
        subgraph = await client.graph_subgraph(
            tenant_id=tenant_id,
            user_id=user_id,
            seed_label="TechCorp",
            radius=2
        )
        
        print(f"📊 Subgraph contains:")
        print(f"  - {len(subgraph.nodes)} nodes")
        print(f"  - {len(subgraph.edges)} edges")
        
        print(f"\n🏷️  Nodes:")
        for node in subgraph.nodes:
            print(f"  - {node.label} ({node.type})")
            if node.description:
                print(f"    Description: {node.description}")
        
        print(f"\n🔗 Edges:")
        for edge in subgraph.edges:
            # Find source and target node labels
            src_node = next((n for n in subgraph.nodes if n.id == edge.src_id), None)
            dst_node = next((n for n in subgraph.nodes if n.id == edge.dst_id), None)
            
            src_label = src_node.label if src_node else edge.src_id
            dst_label = dst_node.label if dst_node else edge.dst_id
            
            print(f"  - {src_label} --[{edge.relation}]--> {dst_label} (weight: {edge.weight})")
            
    except Exception as e:
        print(f"❌ Subgraph error: {e}")
    
    # 3. Demonstrate graph-based retrieval
    print(f"\n🧠 Graph-enhanced retrieval...")
    
    # Retrieve memories related to a specific entity
    related_memories = await client.retrieve(
        tenant_id=tenant_id,
        user_id=user_id,
        query="TechCorp employees and projects",
        top_k=5
    )
    
    print(f"🔍 Found {len(related_memories)} related memories:")
    for memory in related_memories:
        print(f"  - {memory.text[:100]}...")
        print(f"    Importance: {memory.importance}, Modality: {memory.modality}")
    
    # 4. Chat with graph context
    print(f"\n💬 Chat with graph context...")
    
    chat_response = await client.chat(
        tenant_id=tenant_id,
        user_id=user_id,
        messages=[
            {"role": "user", "content": "Tell me about the people and projects at TechCorp"}
        ],
        retrieval_hints={"k": 5}
    )
    
    print(f"🤖 Assistant: {chat_response.reply}")
    print(f"📚 Used {len(chat_response.memories_used)} memories for context")
    
    print(f"\n🎉 Graph demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
