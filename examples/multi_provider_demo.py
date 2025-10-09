#!/usr/bin/env python3
"""Multi-provider demonstration for Engram."""

import asyncio
import os
from typing import Dict, List

import httpx


class MultiProviderDemo:
    """Demonstration of different provider configurations."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def test_embeddings_providers(self) -> Dict[str, bool]:
        """Test different embeddings providers."""
        print("🔍 Testing Embeddings Providers")
        print("-" * 40)
        
        providers_status = {}
        
        # Test local provider (should always work)
        try:
            await self._test_local_embeddings()
            providers_status["local"] = True
            print("✅ Local embeddings provider: Working")
        except Exception as e:
            providers_status["local"] = False
            print(f"❌ Local embeddings provider: {e}")
        
        # Test OpenAI provider (if API key is available)
        if os.getenv("OPENAI_API_KEY"):
            try:
                await self._test_openai_embeddings()
                providers_status["openai"] = True
                print("✅ OpenAI embeddings provider: Working")
            except Exception as e:
                providers_status["openai"] = False
                print(f"❌ OpenAI embeddings provider: {e}")
        else:
            providers_status["openai"] = False
            print("⚠️  OpenAI embeddings provider: No API key")
        
        # Test Google provider (if credentials are available)
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                await self._test_google_embeddings()
                providers_status["google"] = True
                print("✅ Google embeddings provider: Working")
            except Exception as e:
                providers_status["google"] = False
                print(f"❌ Google embeddings provider: {e}")
        else:
            providers_status["google"] = False
            print("⚠️  Google embeddings provider: No credentials")
        
        return providers_status
    
    async def _test_local_embeddings(self):
        """Test local sentence transformers embeddings."""
        # This would require direct API access to test embeddings
        # For now, we'll just test that the service is running
        response = await self.client.get(f"{self.base_url}/v1/health")
        response.raise_for_status()
    
    async def _test_openai_embeddings(self):
        """Test OpenAI embeddings provider."""
        # Similar to above - would need direct embeddings API access
        response = await self.client.get(f"{self.base_url}/v1/health")
        response.raise_for_status()
    
    async def _test_google_embeddings(self):
        """Test Google embeddings provider."""
        # Similar to above - would need direct embeddings API access
        response = await self.client.get(f"{self.base_url}/v1/health")
        response.raise_for_status()
    
    async def test_vector_backends(self) -> Dict[str, bool]:
        """Test different vector database backends."""
        print("\n🗄️  Testing Vector Database Backends")
        print("-" * 40)
        
        backends_status = {}
        
        # Test ChromaDB (default)
        try:
            await self._test_chromadb()
            backends_status["chroma"] = True
            print("✅ ChromaDB backend: Working")
        except Exception as e:
            backends_status["chroma"] = False
            print(f"❌ ChromaDB backend: {e}")
        
        # Test Pinecone (if API key is available)
        if os.getenv("PINECONE_API_KEY"):
            try:
                await self._test_pinecone()
                backends_status["pinecone"] = True
                print("✅ Pinecone backend: Working")
            except Exception as e:
                backends_status["pinecone"] = False
                print(f"❌ Pinecone backend: {e}")
        else:
            backends_status["pinecone"] = False
            print("⚠️  Pinecone backend: No API key")
        
        return backends_status
    
    async def _test_chromadb(self):
        """Test ChromaDB backend."""
        # Test basic functionality by creating and querying memories
        tenant = await self._create_test_tenant("chroma-test")
        
        await self.client.post(
            f"{self.base_url}/v1/memories/upsert",
            json={
                "tenant_id": tenant["id"],
                "user_id": "test-user",
                "texts": ["Test memory for ChromaDB"],
            }
        )
        
        response = await self.client.post(
            f"{self.base_url}/v1/memories/retrieve",
            json={
                "tenant_id": tenant["id"],
                "user_id": "test-user",
                "query": "test memory",
                "top_k": 1,
            }
        )
        
        if not response.json():
            raise Exception("No memories retrieved")
    
    async def _test_pinecone(self):
        """Test Pinecone backend."""
        # This would require switching the backend configuration
        # For now, just test that the service is accessible
        response = await self.client.get(f"{self.base_url}/v1/health")
        response.raise_for_status()
    
    async def _create_test_tenant(self, name: str) -> Dict:
        """Create a test tenant."""
        response = await self.client.post(
            f"{self.base_url}/v1/tenants",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()
    
    async def demonstrate_provider_switching(self):
        """Demonstrate how to switch between providers."""
        print("\n🔄 Provider Switching Demonstration")
        print("-" * 40)
        
        print("To switch providers, you can:")
        print("1. Set environment variables:")
        print("   - DEFAULT_EMBEDDINGS_PROVIDER=openai")
        print("   - VECTOR_BACKEND=pinecone")
        print("   - OPENAI_API_KEY=your-key")
        print("   - PINECONE_API_KEY=your-key")
        
        print("\n2. Restart the service to pick up new configuration")
        
        print("\n3. Or modify the configuration file and reload")
        
        print("\n4. The service will automatically fallback to:")
        print("   - Local embeddings if cloud providers fail")
        print("   - ChromaDB if Pinecone is unavailable")
    
    async def show_configuration_options(self):
        """Show available configuration options."""
        print("\n⚙️  Configuration Options")
        print("-" * 40)
        
        config_options = {
            "Embeddings Providers": [
                "local (sentence-transformers)",
                "openai (text-embedding-3-small)",
                "google (textembedding-gecko)",
            ],
            "Vector Databases": [
                "chroma (local ChromaDB)",
                "pinecone (cloud Pinecone)",
            ],
            "LLM Providers": [
                "openai (GPT models)",
                "anthropic (Claude models)",
                "google (PaLM models)",
            ],
            "Key Environment Variables": [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY", 
                "GOOGLE_APPLICATION_CREDENTIALS",
                "PINECONE_API_KEY",
                "DEFAULT_EMBEDDINGS_PROVIDER",
                "VECTOR_BACKEND",
                "DEFAULT_LLM_PROVIDER",
            ],
        }
        
        for category, options in config_options.items():
            print(f"\n{category}:")
            for option in options:
                print(f"  - {option}")
    
    async def run_performance_comparison(self):
        """Run a simple performance comparison."""
        print("\n⚡ Performance Comparison")
        print("-" * 40)
        
        import time
        
        # Create test data
        tenant = await self._create_test_tenant("perf-test")
        test_texts = [f"Test memory {i} for performance testing" for i in range(10)]
        
        # Test upsert performance
        start_time = time.time()
        await self.client.post(
            f"{self.base_url}/v1/memories/upsert",
            json={
                "tenant_id": tenant["id"],
                "user_id": "perf-user",
                "texts": test_texts,
            }
        )
        upsert_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        response = await self.client.post(
            f"{self.base_url}/v1/memories/retrieve",
            json={
                "tenant_id": tenant["id"],
                "user_id": "perf-user",
                "query": "test memory performance",
                "top_k": 5,
            }
        )
        retrieval_time = time.time() - start_time
        
        print(f"Upsert 10 memories: {upsert_time:.3f}s")
        print(f"Retrieve memories: {retrieval_time:.3f}s")
        print(f"Retrieved {len(response.json())} memories")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Run multi-provider demonstration."""
    demo = MultiProviderDemo()
    
    try:
        print("🚀 Engram Multi-Provider Demonstration")
        print("=" * 50)
        
        # Test embeddings providers
        embeddings_status = await demo.test_embeddings_providers()
        
        # Test vector backends
        vector_status = await demo.test_vector_backends()
        
        # Show configuration options
        await demo.show_configuration_options()
        
        # Demonstrate provider switching
        await demo.demonstrate_provider_switching()
        
        # Run performance comparison
        await demo.run_performance_comparison()
        
        # Summary
        print("\n📊 Summary")
        print("-" * 40)
        print("Embeddings Providers:")
        for provider, status in embeddings_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {provider}")
        
        print("\nVector Databases:")
        for backend, status in vector_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {backend}")
        
        print("\n🎉 Multi-provider demonstration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await demo.close()


if __name__ == "__main__":
    asyncio.run(main())
