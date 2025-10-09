#!/usr/bin/env python3
"""Example script demonstrating chat with memories using Engram."""

import asyncio
import sys
import os

# Add the SDK to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python"))

from engram_client import EngramClient


async def main():
    """Demonstrate chat with memories."""
    # Initialize client
    client = EngramClient(
        api_key="your-api-key-here",  # Replace with actual API key
        base_url="http://localhost:8000"
    )
    
    tenant_id = "tenant_123"
    user_id = "user_456"
    
    print("💬 Engram Chat with Memories Demo")
    print("=" * 50)
    
    # First, let's add some sample memories
    print("\n📝 Adding sample memories...")
    
    sample_memories = [
        {
            "text": "I attended a conference about AI and machine learning last week. The keynote speaker discussed the future of autonomous systems.",
            "metadata": {"event": "AI Conference 2024", "date": "2024-01-10"},
            "importance": 0.9
        },
        {
            "text": "My team is working on a new feature for our mobile app. We're using React Native and it's going well.",
            "metadata": {"project": "Mobile App", "tech": "React Native"},
            "importance": 0.7
        },
        {
            "text": "I read an article about quantum computing. It mentioned that quantum computers could solve certain problems exponentially faster.",
            "metadata": {"source": "article", "topic": "quantum computing"},
            "importance": 0.6
        },
        {
            "text": "Had a great meeting with the design team about user experience improvements. We decided to focus on accessibility.",
            "metadata": {"meeting": "Design Team", "focus": "accessibility"},
            "importance": 0.8
        }
    ]
    
    for memory_data in sample_memories:
        memory = await client.upsert(
            tenant_id=tenant_id,
            user_id=user_id,
            text=memory_data["text"],
            metadata=memory_data["metadata"],
            importance=memory_data["importance"]
        )
        print(f"✅ Added memory: {memory.id}")
    
    print("\n💭 Starting chat conversation...")
    print("Type 'quit' to exit\n")
    
    # Interactive chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Chat with memories
            response = await client.chat(
                tenant_id=tenant_id,
                user_id=user_id,
                messages=[
                    {"role": "user", "content": user_input}
                ],
                retrieval_hints={
                    "k": 5,  # Retrieve top 5 most relevant memories
                    "modalities": ["text"]  # Focus on text memories
                }
            )
            
            print(f"\n🤖 Assistant: {response.reply}")
            
            # Show which memories were used
            if response.memories_used:
                print(f"\n📚 Referenced memories:")
                for i, memory in enumerate(response.memories_used[:3], 1):
                    memory_text = memory.get("text", "")[:100]
                    print(f"  {i}. {memory_text}...")
                if len(response.memories_used) > 3:
                    print(f"  ... and {len(response.memories_used) - 3} more")
            
            print(f"\n🔍 Trace ID: {response.trace_id}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.\n")


async def demonstrate_router_proxy():
    """Demonstrate router proxy functionality."""
    client = EngramClient(
        api_key="your-api-key-here",
        base_url="http://localhost:8000"
    )
    
    tenant_id = "tenant_123"
    user_id = "user_456"
    
    print("\n🔄 Router Proxy Demo")
    print("=" * 30)
    
    # Use router proxy with different providers
    providers = [
        {"provider": "openai", "model": "gpt-3.5-turbo"},
        {"provider": "anthropic", "model": "claude-3-sonnet"},
    ]
    
    question = "What projects am I working on?"
    
    for config in providers:
        try:
            response = await client.router_complete(
                tenant_id=tenant_id,
                user_id=user_id,
                messages=[
                    {"role": "user", "content": question}
                ],
                provider=config["provider"],
                model=config["model"],
                retrieval_hints={"k": 3}
            )
            
            print(f"\n🤖 {config['provider'].title()} ({config['model']}):")
            print(f"   {response['output']}")
            print(f"   📊 Used {len(response.get('memories_used', []))} memories")
            
        except Exception as e:
            print(f"❌ {config['provider']} error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Engram Chat Demo")
    parser.add_argument("--router", action="store_true", help="Run router proxy demo")
    args = parser.parse_args()
    
    if args.router:
        asyncio.run(demonstrate_router_proxy())
    else:
        asyncio.run(main())
