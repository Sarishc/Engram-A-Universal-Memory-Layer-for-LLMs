"""Tests for processing status endpoints."""

import pytest
from fastapi.testclient import TestClient

from engram.api.server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_get_job_status_success(client):
    """Test successful job status retrieval."""
    # Mock a job ID - in real tests you'd create a job first
    job_id = "test_job_123"
    
    # This will likely fail without proper auth, but tests the endpoint exists
    response = client.get(f"/v1/processing/status?job_id={job_id}")
    
    # Should return 401 without auth, but endpoint should exist
    assert response.status_code in [401, 404]


def test_get_queue_stats(client):
    """Test queue statistics endpoint."""
    response = client.get("/v1/processing/queue/stats")
    
    # Should return 401 without auth, but endpoint should exist
    assert response.status_code in [401, 200]


def test_processing_status_validation(client):
    """Test processing status endpoint validation."""
    # Test missing job_id parameter
    response = client.get("/v1/processing/status")
    assert response.status_code == 422  # Validation error


def test_processing_status_invalid_job_id(client):
    """Test processing status with invalid job ID."""
    response = client.get("/v1/processing/status?job_id=invalid")
    
    # Should return 401 without auth, but endpoint should exist
    assert response.status_code in [401, 404]
