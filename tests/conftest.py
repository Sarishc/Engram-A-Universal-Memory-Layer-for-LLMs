"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from engram.database.models import Base
from engram.database.postgres import get_db_session
from engram.core.memory_store import MemoryStore
from engram.core.embeddings import EmbeddingsFacade
from engram.vectordb.base import VectorIndex, VectorHit
from engram.utils.config import get_settings


@pytest.fixture(scope="session")
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_vector_index() -> VectorIndex:
    """Create a mock vector index."""
    mock_index = Mock(spec=VectorIndex)
    mock_index.provider_name = "test"
    
    # Mock methods
    mock_index.upsert = Mock()
    mock_index.query = Mock(return_value=[[VectorHit("test-id", 0.9, {"test": "data"})]])
    mock_index.delete = Mock()
    mock_index.similarity_threshold = Mock(return_value=0.85)
    mock_index.get_stats = Mock(return_value={"total_vectors": 10})
    
    return mock_index


@pytest.fixture
def mock_embeddings_facade() -> EmbeddingsFacade:
    """Create a mock embeddings facade."""
    mock_facade = Mock(spec=EmbeddingsFacade)
    mock_facade.embed_texts = Mock(return_value=[[0.1, 0.2, 0.3, 0.4] * 10])  # 40-dim vector
    mock_facade.get_embedding_dimension = Mock(return_value=40)
    return mock_facade


@pytest.fixture
def memory_store(test_session, mock_vector_index, mock_embeddings_facade) -> MemoryStore:
    """Create a memory store for testing."""
    return MemoryStore(
        db_session=test_session,
        vector_index=mock_vector_index,
        embeddings_facade=mock_embeddings_facade,
    )


@pytest.fixture
def sample_tenant_data() -> Dict[str, Any]:
    """Sample tenant data for testing."""
    return {
        "name": "test-tenant",
    }


@pytest.fixture
def sample_memory_data() -> Dict[str, Any]:
    """Sample memory data for testing."""
    return {
        "tenant_id": "test-tenant-id",
        "user_id": "test-user-id",
        "texts": [
            "User prefers dark mode in applications",
            "User is interested in machine learning",
            "User works as a software engineer",
        ],
        "metadata": [
            {"category": "preferences", "source": "ui"},
            {"category": "interests", "source": "profile"},
            {"category": "work", "source": "profile"},
        ],
        "importance": [0.8, 0.9, 0.7],
    }


@pytest.fixture
def sample_retrieval_data() -> Dict[str, Any]:
    """Sample retrieval data for testing."""
    return {
        "tenant_id": "test-tenant-id",
        "user_id": "test-user-id",
        "query": "What does the user prefer?",
        "top_k": 5,
    }


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return {
        "max_text_length": 2048,
        "default_top_k": 12,
        "default_max_memories": 6,
        "similarity_threshold": 0.92,
        "consolidation_threshold": 0.97,
        "importance_threshold": 0.2,
        "forgetting_days": 30,
        "rank_alpha": 0.70,
        "rank_beta": 0.20,
        "rank_gamma": 0.15,
        "rank_delta": 0.05,
        "recency_tau_days": 14.0,
    }


@pytest.fixture(autouse=True)
def mock_get_settings(mock_settings):
    """Mock get_settings function."""
    original_get_settings = get_settings
    
    def mock_settings_func():
        mock_config = Mock()
        for key, value in mock_settings.items():
            setattr(mock_config, key, value)
        mock_config.is_production = False
        mock_config.is_development = True
        return mock_config
    
    # Replace get_settings temporarily
    import engram.utils.config
    engram.utils.config.get_settings = mock_settings_func
    
    yield mock_settings_func
    
    # Restore original function
    engram.utils.config.get_settings = original_get_settings


@pytest.fixture
def test_client():
    """Create a test client for API testing."""
    from fastapi.testclient import TestClient
    from engram.api.server import app
    
    return TestClient(app)


@pytest.fixture
def sample_vector_hits() -> list[VectorHit]:
    """Sample vector hits for testing."""
    return [
        VectorHit("memory-1", 0.95, {"text": "User prefers dark mode", "importance": 0.8}),
        VectorHit("memory-2", 0.87, {"text": "User likes Python", "importance": 0.9}),
        VectorHit("memory-3", 0.82, {"text": "User works remotely", "importance": 0.7}),
    ]


@pytest.fixture
def sample_embeddings() -> list[list[float]]:
    """Sample embeddings for testing."""
    return [
        [0.1, 0.2, 0.3, 0.4] * 10,  # 40 dimensions
        [0.2, 0.3, 0.4, 0.5] * 10,
        [0.3, 0.4, 0.5, 0.6] * 10,
    ]


@pytest.fixture
def sample_texts() -> list[str]:
    """Sample texts for testing."""
    return [
        "User prefers dark mode in applications",
        "User is interested in machine learning and AI",
        "User works as a software engineer at a tech company",
    ]


# Async fixtures for async tests
@pytest.fixture
async def async_test_client():
    """Create an async test client for API testing."""
    from httpx import AsyncClient
    from engram.api.server import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    mock_logger = Mock()
    mock_logger.info = Mock()
    mock_logger.debug = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()
    return mock_logger


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = Mock()
    mock_redis.get = Mock(return_value=None)
    mock_redis.set = Mock(return_value=True)
    mock_redis.incr = Mock(return_value=1)
    mock_redis.expire = Mock(return_value=True)
    return mock_redis


@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client for testing."""
    mock_client = Mock()
    mock_collection = Mock()
    mock_collection.upsert = Mock()
    mock_collection.query = Mock(return_value={
        "ids": [["test-id"]],
        "distances": [[0.1]],
        "metadatas": [[{"test": "data"}]],
    })
    mock_collection.delete = Mock()
    mock_collection.count = Mock(return_value=10)
    mock_client.get_or_create_collection = Mock(return_value=mock_collection)
    return mock_client


@pytest.fixture
def mock_pinecone_client():
    """Mock Pinecone client for testing."""
    mock_client = Mock()
    mock_index = Mock()
    mock_index.upsert = Mock()
    mock_index.query = Mock(return_value={
        "matches": [{"id": "test-id", "score": 0.9, "metadata": {"test": "data"}}]
    })
    mock_index.delete = Mock()
    mock_index.describe_index_stats = Mock(return_value={"total_vector_count": 10})
    mock_client.Index = Mock(return_value=mock_index)
    mock_client.list_indexes = Mock(return_value=Mock(names=Mock(return_value=["test-index"])))
    return mock_client
