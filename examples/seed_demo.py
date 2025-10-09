#!/usr/bin/env python3
"""Seed demo data for Engram."""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List

import httpx


class DemoDataSeeder:
    """Seeder for demo data."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_demo_tenant(self) -> Dict:
        """Create a demo tenant."""
        print("Creating demo tenant...")
        response = await self.client.post(
            f"{self.base_url}/v1/tenants",
            json={"name": "engram-demo"}
        )
        response.raise_for_status()
        tenant = response.json()
        print(f"✅ Created tenant: {tenant['name']} (ID: {tenant['id']})")
        return tenant
    
    async def seed_user_memories(
        self,
        tenant_id: str,
        user_id: str,
        user_profile: Dict,
        num_memories: int = 30,
    ) -> List[str]:
        """Seed memories for a user based on their profile."""
        print(f"Seeding {num_memories} memories for user {user_id}...")
        
        # Generate memories based on user profile
        memories = self._generate_user_memories(user_profile, num_memories)
        
        # Upsert memories
        response = await self.client.post(
            f"{self.base_url}/v1/memories/upsert",
            json={
                "tenant_id": tenant_id,
                "user_id": user_id,
                "texts": [memory["text"] for memory in memories],
                "metadata": [memory["metadata"] for memory in memories],
                "importance": [memory["importance"] for memory in memories],
            }
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Seeded {result['count']} memories for user {user_id}")
        return result["memory_ids"]
    
    def _generate_user_memories(self, profile: Dict, count: int) -> List[Dict]:
        """Generate realistic memories based on user profile."""
        memories = []
        
        # Core profile memories
        core_memories = [
            f"User works as a {profile['profession']} at {profile['company']}",
            f"User is interested in {', '.join(profile['interests'][:3])}",
            f"User prefers {profile['ui_preference']} mode in applications",
            f"User is {profile['experience_level']} level in their field",
            f"User's favorite programming language is {profile['favorite_language']}",
        ]
        
        for text in core_memories:
            memories.append({
                "text": text,
                "metadata": {
                    "category": "profile",
                    "source": "user_input",
                    "created_at": datetime.now().isoformat(),
                },
                "importance": random.uniform(0.7, 0.9),
            })
        
        # Work-related memories
        work_memories = [
            f"User is working on a project involving {random.choice(profile['interests'])}",
            f"User has experience with {random.choice(profile['technologies'])}",
            f"User's team uses {random.choice(['Agile', 'Scrum', 'Kanban'])} methodology",
            f"User prefers {random.choice(['morning', 'afternoon', 'evening'])} meetings",
            f"User's current focus is on {random.choice(['frontend', 'backend', 'full-stack', 'DevOps'])} development",
        ]
        
        for text in work_memories:
            memories.append({
                "text": text,
                "metadata": {
                    "category": "work",
                    "source": "conversation",
                    "created_at": datetime.now().isoformat(),
                },
                "importance": random.uniform(0.6, 0.8),
            })
        
        # Personal preferences
        personal_memories = [
            f"User enjoys {random.choice(profile['hobbies'])} in their free time",
            f"User prefers {random.choice(['tea', 'coffee', 'water'])} while working",
            f"User likes {random.choice(['quiet', 'background music', 'white noise'])} environments",
            f"User is a {random.choice(['morning person', 'night owl'])}",
            f"User prefers {random.choice(['text', 'voice', 'video'])} communication",
        ]
        
        for text in personal_memories:
            memories.append({
                "text": text,
                "metadata": {
                    "category": "personal",
                    "source": "observation",
                    "created_at": datetime.now().isoformat(),
                },
                "importance": random.uniform(0.4, 0.7),
            })
        
        # Technology preferences
        tech_memories = [
            f"User prefers {random.choice(['VS Code', 'PyCharm', 'Vim', 'Sublime Text'])} as their editor",
            f"User uses {random.choice(['GitHub', 'GitLab', 'Bitbucket'])} for version control",
            f"User prefers {random.choice(['Linux', 'macOS', 'Windows'])} as their development OS",
            f"User likes {random.choice(['Docker', 'Kubernetes', 'Vagrant'])} for containerization",
            f"User prefers {random.choice(['REST APIs', 'GraphQL', 'gRPC'])} for API design",
        ]
        
        for text in tech_memories:
            memories.append({
                "text": text,
                "metadata": {
                    "category": "technology",
                    "source": "usage_patterns",
                    "created_at": datetime.now().isoformat(),
                },
                "importance": random.uniform(0.5, 0.8),
            })
        
        # Fill remaining with random memories
        remaining = count - len(memories)
        random_memories = [
            "User mentioned they're learning a new technology",
            "User has been working on improving their productivity",
            "User is interested in automation and efficiency",
            "User prefers clean and minimal interfaces",
            "User values good documentation and examples",
            "User likes to experiment with new tools and frameworks",
            "User is concerned about security and best practices",
            "User enjoys collaborating with other developers",
            "User prefers iterative development approaches",
            "User is interested in performance optimization",
        ]
        
        for i in range(remaining):
            text = random.choice(random_memories)
            memories.append({
                "text": text,
                "metadata": {
                    "category": "general",
                    "source": "inference",
                    "created_at": datetime.now().isoformat(),
                },
                "importance": random.uniform(0.3, 0.6),
            })
        
        # Shuffle and return requested count
        random.shuffle(memories)
        return memories[:count]
    
    async def seed_multiple_users(self, tenant_id: str) -> List[Dict]:
        """Seed memories for multiple demo users."""
        print("\nSeeding memories for multiple users...")
        
        users = [
            {
                "user_id": "alice_dev",
                "profile": {
                    "profession": "Software Engineer",
                    "company": "TechCorp Inc",
                    "interests": ["machine learning", "web development", "data science"],
                    "technologies": ["Python", "JavaScript", "TensorFlow", "React"],
                    "ui_preference": "dark",
                    "experience_level": "senior",
                    "favorite_language": "Python",
                    "hobbies": ["reading", "hiking", "cooking"],
                }
            },
            {
                "user_id": "bob_designer",
                "profile": {
                    "profession": "UX Designer",
                    "company": "DesignStudio",
                    "interests": ["user experience", "visual design", "accessibility"],
                    "technologies": ["Figma", "Sketch", "Adobe Creative Suite"],
                    "ui_preference": "light",
                    "experience_level": "mid",
                    "favorite_language": "JavaScript",
                    "hobbies": ["photography", "drawing", "traveling"],
                }
            },
            {
                "user_id": "carol_manager",
                "profile": {
                    "profession": "Product Manager",
                    "company": "StartupXYZ",
                    "interests": ["product strategy", "user research", "analytics"],
                    "technologies": ["SQL", "Tableau", "Jira", "Confluence"],
                    "ui_preference": "dark",
                    "experience_level": "senior",
                    "favorite_language": "Python",
                    "hobbies": ["running", "yoga", "wine tasting"],
                }
            },
        ]
        
        seeded_users = []
        for user_data in users:
            user_id = user_data["user_id"]
            profile = user_data["profile"]
            
            memory_ids = await self.seed_user_memories(
                tenant_id=tenant_id,
                user_id=user_id,
                user_profile=profile,
                num_memories=25,
            )
            
            seeded_users.append({
                "user_id": user_id,
                "profile": profile,
                "memory_count": len(memory_ids),
            })
        
        return seeded_users
    
    async def demonstrate_retrieval(self, tenant_id: str, users: List[Dict]):
        """Demonstrate memory retrieval across users."""
        print("\n🔍 Demonstrating memory retrieval...")
        
        test_queries = [
            "What does the user prefer for development?",
            "Tell me about their work experience",
            "What are their hobbies and interests?",
            "What technologies do they use?",
            "How do they like to communicate?",
        ]
        
        for user_data in users:
            user_id = user_data["user_id"]
            print(f"\n--- User: {user_id} ---")
            
            for query in test_queries[:2]:  # Limit to 2 queries per user
                print(f"\nQuery: '{query}'")
                
                response = await self.client.post(
                    f"{self.base_url}/v1/memories/retrieve",
                    json={
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "query": query,
                        "top_k": 3,
                    }
                )
                response.raise_for_status()
                
                memories = response.json()
                for i, memory in enumerate(memories, 1):
                    print(f"  {i}. [{memory['score']:.3f}] {memory['text']}")
    
    async def show_tenant_stats(self, tenant_id: str):
        """Show statistics for the seeded tenant."""
        print("\n📊 Tenant Statistics")
        print("-" * 30)
        
        try:
            response = await self.client.get(f"{self.base_url}/v1/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"Total tenants: {stats['total_tenants']}")
                print(f"Total memories: {stats['total_memories']}")
                print(f"Active memories: {stats['active_memories']}")
                print(f"Vector provider: {stats['vector_provider']}")
                print(f"Embeddings provider: {stats['embeddings_provider']}")
        except Exception as e:
            print(f"Could not fetch stats: {e}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Run the demo data seeder."""
    seeder = DemoDataSeeder()
    
    try:
        print("🌱 Engram Demo Data Seeder")
        print("=" * 40)
        
        # Create demo tenant
        tenant = await seeder.create_demo_tenant()
        tenant_id = tenant["id"]
        
        # Seed multiple users
        users = await seeder.seed_multiple_users(tenant_id)
        
        # Show user summary
        print(f"\n📋 Seeded Users Summary:")
        for user in users:
            print(f"  - {user['user_id']}: {user['memory_count']} memories")
        
        # Demonstrate retrieval
        await seeder.demonstrate_retrieval(tenant_id, users)
        
        # Show statistics
        await seeder.show_tenant_stats(tenant_id)
        
        print(f"\n🎉 Demo data seeding completed!")
        print(f"Tenant ID: {tenant_id}")
        print(f"API Base URL: http://localhost:8000")
        print(f"OpenAPI Docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await seeder.close()


if __name__ == "__main__":
    asyncio.run(main())
