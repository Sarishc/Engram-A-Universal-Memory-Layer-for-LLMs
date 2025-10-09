"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from engram.api.server import app
from engram.database.models import Tenant, Memory


class TestTenantAPI:
    """Test tenant-related API endpoints."""

    def test_create_tenant(self, test_client: TestClient, sample_tenant_data):
        """Test tenant creation."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_tenant = Mock()
            mock_tenant.id = "test-tenant-id"
            mock_tenant.name = sample_tenant_data["name"]
            mock_tenant.created_at = "2024-01-01T00:00:00Z"
            mock_store.create_tenant.return_value = mock_tenant
            mock_get_store.return_value = mock_store
            
            response = test_client.post("/v1/tenants", json=sample_tenant_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test-tenant-id"
            assert data["name"] == sample_tenant_data["name"]
            mock_store.create_tenant.assert_called_once_with(sample_tenant_data["name"])

    def test_create_tenant_duplicate(self, test_client: TestClient, sample_tenant_data):
        """Test tenant creation with duplicate name."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_store.create_tenant.side_effect = ValueError("Tenant with name 'test-tenant' already exists")
            mock_get_store.return_value = mock_store
            
            response = test_client.post("/v1/tenants", json=sample_tenant_data)
            
            assert response.status_code == 400
            assert "already exists" in response.json()["detail"]

    def test_get_tenant(self, test_client: TestClient):
        """Test getting tenant information."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_tenant = Mock()
            mock_tenant.id = "test-tenant-id"
            mock_tenant.name = "test-tenant"
            mock_tenant.created_at = "2024-01-01T00:00:00Z"
            mock_store.get_tenant.return_value = mock_tenant
            mock_get_store.return_value = mock_store
            
            response = test_client.get("/v1/tenants/test-tenant-id")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test-tenant-id"
            assert data["name"] == "test-tenant"

    def test_get_tenant_not_found(self, test_client: TestClient):
        """Test getting non-existent tenant."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_store.get_tenant.return_value = None
            mock_get_store.return_value = mock_store
            
            response = test_client.get("/v1/tenants/non-existent-id")
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]


class TestMemoryAPI:
    """Test memory-related API endpoints."""

    def test_upsert_memories(self, test_client: TestClient, sample_memory_data):
        """Test memory upsert."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_memories = [
                Mock(id="memory-1"),
                Mock(id="memory-2"),
                Mock(id="memory-3"),
            ]
            mock_store.upsert_memories.return_value = mock_memories
            mock_get_store.return_value = mock_store
            
            response = test_client.post("/v1/memories/upsert", json=sample_memory_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3
            assert len(data["memory_ids"]) == 3
            mock_store.upsert_memories.assert_called_once()

    def test_upsert_memories_validation_error(self, test_client: TestClient):
        """Test memory upsert with validation error."""
        invalid_data = {
            "tenant_id": "test-tenant-id",
            "user_id": "test-user-id",
            "texts": [""],  # Empty text should fail validation
        }
        
        response = test_client.post("/v1/memories/upsert", json=invalid_data)
        
        assert response.status_code == 422

    def test_retrieve_memories(self, test_client: TestClient, sample_retrieval_data):
        """Test memory retrieval."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_results = [
                {
                    "memory_id": "memory-1",
                    "text": "User prefers dark mode",
                    "score": 0.95,
                    "metadata": {"category": "preferences"},
                    "importance": 0.8,
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_accessed_at": "2024-01-01T00:00:00Z",
                }
            ]
            mock_store.retrieve_memories.return_value = mock_results
            mock_get_store.return_value = mock_store
            
            response = test_client.post("/v1/memories/retrieve", json=sample_retrieval_data)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["memory_id"] == "memory-1"
            assert data[0]["score"] == 0.95

    def test_retrieve_memories_empty(self, test_client: TestClient, sample_retrieval_data):
        """Test memory retrieval with no results."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_store.retrieve_memories.return_value = []
            mock_get_store.return_value = mock_store
            
            response = test_client.post("/v1/memories/retrieve", json=sample_retrieval_data)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

    def test_context_injection(self, test_client: TestClient):
        """Test context injection."""
        inject_data = {
            "tenant_id": "test-tenant-id",
            "user_id": "test-user-id",
            "query": "user preferences",
            "prompt": "Based on user preferences, suggest a feature.",
            "max_memories": 3,
        }
        
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_memories = [
                {
                    "memory_id": "memory-1",
                    "text": "User prefers dark mode",
                    "score": 0.95,
                    "metadata": {"category": "preferences"},
                    "importance": 0.8,
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_accessed_at": "2024-01-01T00:00:00Z",
                }
            ]
            mock_store.retrieve_memories.return_value = mock_memories
            mock_get_store.return_value = mock_store
            
            response = test_client.post("/v1/context/inject", json=inject_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "injected_prompt" in data
            assert "memories_used" in data
            assert "[MEMORY CONTEXT START]" in data["injected_prompt"]
            assert len(data["memories_used"]) == 1

    def test_context_injection_no_memories(self, test_client: TestClient):
        """Test context injection with no memories."""
        inject_data = {
            "tenant_id": "test-tenant-id",
            "user_id": "test-user-id",
            "query": "user preferences",
            "prompt": "Based on user preferences, suggest a feature.",
            "max_memories": 3,
        }
        
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_store.retrieve_memories.return_value = []
            mock_get_store.return_value = mock_store
            
            response = test_client.post("/v1/context/inject", json=inject_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["injected_prompt"] == inject_data["prompt"]
            assert len(data["memories_used"]) == 0


class TestAdminAPI:
    """Test admin API endpoints."""

    def test_list_memories(self, test_client: TestClient):
        """Test admin memory listing."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_memories = [
                Mock(
                    id="memory-1",
                    text="User prefers dark mode",
                    metadata={"category": "preferences"},
                    importance=0.8,
                    created_at="2024-01-01T00:00:00Z",
                    last_accessed_at="2024-01-01T00:00:00Z",
                )
            ]
            mock_store.list_memories.return_value = mock_memories
            mock_get_store.return_value = mock_store
            
            response = test_client.get(
                "/v1/admin/memories",
                params={
                    "tenant_id": "test-tenant-id",
                    "user_id": "test-user-id",
                    "limit": 10,
                    "offset": 0,
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "memories" in data
            assert "total_count" in data
            assert len(data["memories"]) == 1

    def test_delete_memory(self, test_client: TestClient):
        """Test admin memory deletion."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_store.delete_memory.return_value = True
            mock_get_store.return_value = mock_store
            
            response = test_client.delete(
                "/v1/admin/memories/memory-1",
                params={
                    "tenant_id": "test-tenant-id",
                    "user_id": "test-user-id",
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data["message"]

    def test_delete_memory_not_found(self, test_client: TestClient):
        """Test admin memory deletion with non-existent memory."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_store.delete_memory.return_value = False
            mock_get_store.return_value = mock_store
            
            response = test_client.delete(
                "/v1/admin/memories/non-existent-memory",
                params={
                    "tenant_id": "test-tenant-id",
                    "user_id": "test-user-id",
                }
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    def test_get_stats(self, test_client: TestClient):
        """Test getting service statistics."""
        with patch('engram.api.routes.get_memory_store') as mock_get_store:
            mock_store = Mock()
            mock_stats = {
                "total_tenants": 5,
                "total_memories": 100,
                "active_memories": 95,
                "vector_provider": "chromadb",
                "embeddings_provider": "local",
            }
            mock_store.get_store_stats.return_value = mock_stats
            mock_get_store.return_value = mock_store
            
            response = test_client.get("/v1/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_tenants"] == 5
            assert data["total_memories"] == 100
            assert data["vector_provider"] == "chromadb"


class TestHealthAPI:
    """Test health check endpoint."""

    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint."""
        response = test_client.get("/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "uptime_seconds" in data
        assert data["version"] == "0.1.0"

    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Engram"
        assert data["version"] == "0.1.0"
        assert "/docs" in data["docs"]


class TestErrorHandling:
    """Test error handling."""

    def test_404_error(self, test_client: TestClient):
        """Test 404 error handling."""
        response = test_client.get("/v1/non-existent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "Not found"
        assert "error_code" in data

    def test_422_validation_error(self, test_client: TestClient):
        """Test validation error handling."""
        response = test_client.post("/v1/tenants", json={"name": ""})
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "details" in data
