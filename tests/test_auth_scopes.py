"""Tests for API key authentication and scopes."""

import pytest
from fastapi.testclient import TestClient

from engram.api.server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_missing_auth_header(client):
    """Test endpoints without authentication header."""
    # Test a protected endpoint
    response = client.get("/v1/admin/memories")
    assert response.status_code == 401
    assert "authorization" in response.json()["detail"].lower()


def test_invalid_auth_header(client):
    """Test endpoints with invalid authentication header."""
    headers = {"Authorization": "Bearer invalid_key"}
    
    response = client.get("/v1/admin/memories", headers=headers)
    assert response.status_code == 401


def test_malformed_auth_header(client):
    """Test endpoints with malformed authentication header."""
    headers = {"Authorization": "InvalidFormat key"}
    
    response = client.get("/v1/admin/memories", headers=headers)
    assert response.status_code == 401


def test_public_endpoints_no_auth(client):
    """Test that public endpoints work without authentication."""
    # Health endpoint should be public
    response = client.get("/v1/health")
    assert response.status_code == 200
    
    # Docs should be public
    response = client.get("/docs")
    assert response.status_code == 200


def test_ingest_endpoints_require_auth(client):
    """Test that ingest endpoints require authentication."""
    # URL ingestion
    response = client.post("/v1/ingest/url", json={"url": "https://example.com"})
    assert response.status_code == 401
    
    # Chat ingestion
    response = client.post("/v1/ingest/chat", json={
        "platform": "test",
        "items": []
    })
    assert response.status_code == 401


def test_analytics_endpoints_require_auth(client):
    """Test that analytics endpoints require authentication."""
    response = client.get("/v1/analytics/overview")
    assert response.status_code == 401


def test_connector_endpoints_require_auth(client):
    """Test that connector endpoints require authentication."""
    response = client.get("/v1/connectors/sources")
    assert response.status_code == 401
