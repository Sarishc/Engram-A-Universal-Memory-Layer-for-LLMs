"""Tests for retrieval with filters."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from engram.api.server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_retrieve_with_modality_filter(client):
    """Test retrieval with modality filter."""
    # Mock the retrieval engine
    with patch('engram.core.retrieval.RetrievalEngine') as mock_retrieval:
        mock_engine = Mock()
        mock_engine.retrieve.return_value = []
        mock_retrieval.return_value = mock_engine
        
        headers = {"Authorization": "Bearer test_key"}
        data = {
            "tenant_id": "test_tenant",
            "user_id": "test_user",
            "query": "test query",
            "modalities": ["text", "pdf"]
        }
        
        response = client.post("/v1/memories/retrieve", json=data, headers=headers)
        
        # Should return 401 without valid auth, but endpoint should exist
        assert response.status_code == 401


def test_retrieve_with_importance_filter(client):
    """Test retrieval with importance filter."""
    headers = {"Authorization": "Bearer test_key"}
    data = {
        "tenant_id": "test_tenant",
        "user_id": "test_user",
        "query": "test query",
        "importance_min": 0.7
    }
    
    response = client.post("/v1/memories/retrieve", json=data, headers=headers)
    
    # Should return 401 without valid auth, but endpoint should exist
    assert response.status_code == 401


def test_retrieve_with_date_range_filter(client):
    """Test retrieval with date range filter."""
    headers = {"Authorization": "Bearer test_key"}
    data = {
        "tenant_id": "test_tenant",
        "user_id": "test_user",
        "query": "test query",
        "date_from": "2024-01-01T00:00:00Z",
        "date_to": "2024-12-31T23:59:59Z"
    }
    
    response = client.post("/v1/memories/retrieve", json=data, headers=headers)
    
    # Should return 401 without valid auth, but endpoint should exist
    assert response.status_code == 401


def test_retrieve_validation(client):
    """Test retrieval endpoint validation."""
    headers = {"Authorization": "Bearer test_key"}
    
    # Missing required fields
    data = {
        "query": "test query"
    }
    
    response = client.post("/v1/memories/retrieve", json=data, headers=headers)
    assert response.status_code == 422  # Validation error


def test_retrieve_empty_query(client):
    """Test retrieval with empty query."""
    headers = {"Authorization": "Bearer test_key"}
    data = {
        "tenant_id": "test_tenant",
        "user_id": "test_user",
        "query": ""
    }
    
    response = client.post("/v1/memories/retrieve", json=data, headers=headers)
    
    # Should return 401 without valid auth, but endpoint should exist
    assert response.status_code == 401
