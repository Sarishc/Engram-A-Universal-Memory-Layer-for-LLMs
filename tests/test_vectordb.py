"""Tests for vector database functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from engram.vectordb.base import VectorHit, cosine_similarity, euclidean_distance, normalize_vector
from engram.vectordb.chroma_db import ChromaVectorIndex
from engram.vectordb.pinecone_db import PineconeVectorIndex


class TestVectorHit:
    """Test VectorHit functionality."""

    def test_vector_hit_creation(self):
        """Test VectorHit creation."""
        hit = VectorHit(
            id="test-id",
            score=0.95,
            metadata={"test": "data"}
        )
        
        assert hit.id == "test-id"
        assert hit.score == 0.95
        assert hit.metadata == {"test": "data"}

    def test_vector_hit_invalid_score(self):
        """Test VectorHit with invalid score."""
        with pytest.raises(ValueError, match="Score must be numeric"):
            VectorHit(
                id="test-id",
                score="invalid",
                metadata={"test": "data"}
            )

    def test_vector_hit_invalid_metadata(self):
        """Test VectorHit with invalid metadata."""
        with pytest.raises(ValueError, match="Metadata must be dict"):
            VectorHit(
                id="test-id",
                score=0.95,
                metadata="invalid"
            )


class TestVectorMath:
    """Test vector mathematical operations."""

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        vector_a = [1.0, 0.0, 0.0]
        vector_b = [0.0, 1.0, 0.0]
        
        similarity = cosine_similarity(vector_a, vector_b)
        
        assert similarity == 0.0  # Orthogonal vectors

    def test_cosine_similarity_identical(self):
        """Test cosine similarity with identical vectors."""
        vector_a = [1.0, 2.0, 3.0]
        vector_b = [1.0, 2.0, 3.0]
        
        similarity = cosine_similarity(vector_a, vector_b)
        
        assert abs(similarity - 1.0) < 1e-10  # Should be 1.0

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity with opposite vectors."""
        vector_a = [1.0, 2.0, 3.0]
        vector_b = [-1.0, -2.0, -3.0]
        
        similarity = cosine_similarity(vector_a, vector_b)
        
        assert abs(similarity - (-1.0)) < 1e-10  # Should be -1.0

    def test_cosine_similarity_empty_vectors(self):
        """Test cosine similarity with empty vectors."""
        with pytest.raises(ValueError, match="Vectors cannot be empty"):
            cosine_similarity([], [1.0, 2.0])

    def test_cosine_similarity_different_dimensions(self):
        """Test cosine similarity with different dimension vectors."""
        with pytest.raises(ValueError, match="Vectors must have same dimension"):
            cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0])

    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        vector_a = [0.0, 0.0]
        vector_b = [3.0, 4.0]
        
        distance = euclidean_distance(vector_a, vector_b)
        
        assert abs(distance - 5.0) < 1e-10  # Should be 5.0 (3-4-5 triangle)

    def test_euclidean_distance_identical(self):
        """Test Euclidean distance with identical vectors."""
        vector_a = [1.0, 2.0, 3.0]
        vector_b = [1.0, 2.0, 3.0]
        
        distance = euclidean_distance(vector_a, vector_b)
        
        assert distance == 0.0

    def test_normalize_vector(self):
        """Test vector normalization."""
        vector = [3.0, 4.0, 0.0]
        
        normalized = normalize_vector(vector)
        
        # Should be normalized to unit length
        magnitude = sum(x * x for x in normalized) ** 0.5
        assert abs(magnitude - 1.0) < 1e-10
        
        # Should preserve direction
        assert abs(normalized[0] - 0.6) < 1e-10  # 3/5
        assert abs(normalized[1] - 0.8) < 1e-10  # 4/5
        assert normalized[2] == 0.0

    def test_normalize_zero_vector(self):
        """Test normalization of zero vector."""
        with pytest.raises(ValueError, match="Cannot normalize zero vector"):
            normalize_vector([0.0, 0.0, 0.0])

    def test_normalize_empty_vector(self):
        """Test normalization of empty vector."""
        with pytest.raises(ValueError, match="Vector cannot be empty"):
            normalize_vector([])


class TestChromaVectorIndex:
    """Test ChromaDB vector index."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Create a mock ChromaDB client."""
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

    @patch('engram.vectordb.chroma_db.chromadb.PersistentClient')
    def test_chroma_initialization(self, mock_chroma_client_class, temp_dir):
        """Test ChromaDB initialization."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)
        mock_chroma_client_class.return_value = mock_client
        
        index = ChromaVectorIndex(persist_directory=temp_dir)
        
        assert index.provider_name == "chromadb"
        mock_chroma_client_class.assert_called_once()

    @patch('engram.vectordb.chroma_db.chromadb.PersistentClient')
    def test_chroma_upsert(self, mock_chroma_client_class, temp_dir):
        """Test ChromaDB upsert operation."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)
        mock_chroma_client_class.return_value = mock_client
        
        index = ChromaVectorIndex(persist_directory=temp_dir)
        
        items = [
            ("id-1", [0.1, 0.2, 0.3, 0.4], {"test": "data1"}),
            ("id-2", [0.5, 0.6, 0.7, 0.8], {"test": "data2"}),
        ]
        
        index.upsert(items, "test:namespace")
        
        mock_collection.upsert.assert_called_once()
        call_args = mock_collection.upsert.call_args
        assert len(call_args[1]["ids"]) == 2
        assert len(call_args[1]["embeddings"]) == 2

    @patch('engram.vectordb.chroma_db.chromadb.PersistentClient')
    def test_chroma_query(self, mock_chroma_client_class, temp_dir):
        """Test ChromaDB query operation."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query = Mock(return_value={
            "ids": [["id-1", "id-2"]],
            "distances": [[0.1, 0.2]],
            "metadatas": [[{"test": "data1"}, {"test": "data2"}]],
        })
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)
        mock_chroma_client_class.return_value = mock_client
        
        index = ChromaVectorIndex(persist_directory=temp_dir)
        
        query_vectors = [[0.1, 0.2, 0.3, 0.4]]
        results = index.query(query_vectors, top_k=2, namespace="test:namespace")
        
        assert len(results) == 1
        assert len(results[0]) == 2
        assert results[0][0].id == "id-1"
        assert results[0][1].id == "id-2"

    @patch('engram.vectordb.chroma_db.chromadb.PersistentClient')
    def test_chroma_delete(self, mock_chroma_client_class, temp_dir):
        """Test ChromaDB delete operation."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)
        mock_chroma_client_class.return_value = mock_client
        
        index = ChromaVectorIndex(persist_directory=temp_dir)
        
        index.delete(["id-1", "id-2"], "test:namespace")
        
        mock_collection.delete.assert_called_once_with(ids=["id-1", "id-2"])

    @patch('engram.vectordb.chroma_db.chromadb.PersistentClient')
    def test_chroma_get_stats(self, mock_chroma_client_class, temp_dir):
        """Test ChromaDB statistics."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count = Mock(return_value=25)
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)
        mock_chroma_client_class.return_value = mock_client
        
        index = ChromaVectorIndex(persist_directory=temp_dir)
        
        stats = index.get_stats("test:namespace")
        
        assert stats["total_vectors"] == 25
        assert stats["namespace"] == "test:namespace"
        assert stats["provider"] == "chromadb"

    @patch('engram.vectordb.chroma_db.chromadb.PersistentClient')
    def test_chroma_health_check(self, mock_chroma_client_class, temp_dir):
        """Test ChromaDB health check."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count = Mock(return_value=10)
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)
        mock_chroma_client_class.return_value = mock_client
        
        index = ChromaVectorIndex(persist_directory=temp_dir)
        
        health = index.health_check()
        
        assert health["status"] == "healthy"
        assert health["provider"] == "chromadb"
        assert health["total_vectors"] == 10


class TestPineconeVectorIndex:
    """Test Pinecone vector index."""

    @pytest.fixture
    def mock_pinecone_client(self):
        """Create a mock Pinecone client."""
        mock_client = Mock()
        mock_index = Mock()
        mock_index.upsert = Mock()
        mock_index.query = Mock(return_value={
            "matches": [
                {"id": "test-namespace:id-1", "score": 0.95, "metadata": {"test": "data1"}},
                {"id": "test-namespace:id-2", "score": 0.87, "metadata": {"test": "data2"}},
            ]
        })
        mock_index.delete = Mock()
        mock_index.describe_index_stats = Mock(return_value={
            "total_vector_count": 20,
            "namespaces": {"test-namespace": {"vector_count": 15}}
        })
        mock_client.Index = Mock(return_value=mock_index)
        mock_client.list_indexes = Mock(return_value=Mock(names=Mock(return_value=["test-index"])))
        return mock_client

    @patch('engram.vectordb.pinecone_db.Pinecone')
    def test_pinecone_initialization_existing_index(self, mock_pinecone_class, mock_pinecone_client):
        """Test Pinecone initialization with existing index."""
        mock_pinecone_class.return_value = mock_pinecone_client
        
        index = PineconeVectorIndex(
            api_key="test-key",
            index_name="test-index",
            dimension=384,
        )
        
        assert index.provider_name == "pinecone"
        assert index.index_name == "test-index"
        assert index.dimension == 384

    @patch('engram.vectordb.pinecone_db.Pinecone')
    def test_pinecone_upsert(self, mock_pinecone_class, mock_pinecone_client):
        """Test Pinecone upsert operation."""
        mock_pinecone_class.return_value = mock_pinecone_client
        
        index = PineconeVectorIndex(
            api_key="test-key",
            index_name="test-index",
            dimension=384,
        )
        
        items = [
            ("id-1", [0.1, 0.2, 0.3, 0.4], {"test": "data1"}),
            ("id-2", [0.5, 0.6, 0.7, 0.8], {"test": "data2"}),
        ]
        
        index.upsert(items, "test:namespace")
        
        mock_pinecone_client.Index.return_value.upsert.assert_called_once()
        call_args = mock_pinecone_client.Index.return_value.upsert.call_args
        vectors = call_args[1]["vectors"]
        assert len(vectors) == 2
        assert vectors[0]["id"] == "test:namespace:id-1"
        assert vectors[1]["id"] == "test:namespace:id-2"

    @patch('engram.vectordb.pinecone_db.Pinecone')
    def test_pinecone_query(self, mock_pinecone_class, mock_pinecone_client):
        """Test Pinecone query operation."""
        mock_pinecone_class.return_value = mock_pinecone_client
        
        index = PineconeVectorIndex(
            api_key="test-key",
            index_name="test-index",
            dimension=384,
        )
        
        query_vectors = [[0.1, 0.2, 0.3, 0.4]]
        results = index.query(query_vectors, top_k=2, namespace="test:namespace")
        
        assert len(results) == 1
        assert len(results[0]) == 2
        assert results[0][0].id == "id-1"  # Should extract original ID
        assert results[0][1].id == "id-2"

    @patch('engram.vectordb.pinecone_db.Pinecone')
    def test_pinecone_delete(self, mock_pinecone_class, mock_pinecone_client):
        """Test Pinecone delete operation."""
        mock_pinecone_class.return_value = mock_pinecone_client
        
        index = PineconeVectorIndex(
            api_key="test-key",
            index_name="test-index",
            dimension=384,
        )
        
        index.delete(["id-1", "id-2"], "test:namespace")
        
        mock_pinecone_client.Index.return_value.delete.assert_called_once()
        call_args = mock_pinecone_client.Index.return_value.delete.call_args
        assert call_args[1]["ids"] == ["test:namespace:id-1", "test:namespace:id-2"]

    @patch('engram.vectordb.pinecone_db.Pinecone')
    def test_pinecone_get_stats(self, mock_pinecone_class, mock_pinecone_client):
        """Test Pinecone statistics."""
        mock_pinecone_class.return_value = mock_pinecone_client
        
        index = PineconeVectorIndex(
            api_key="test-key",
            index_name="test-index",
            dimension=384,
        )
        
        stats = index.get_stats("test:namespace")
        
        assert stats["total_vectors"] == 15  # From namespace stats
        assert stats["namespace"] == "test:namespace"
        assert stats["provider"] == "pinecone"

    @patch('engram.vectordb.pinecone_db.Pinecone')
    def test_pinecone_health_check(self, mock_pinecone_class, mock_pinecone_client):
        """Test Pinecone health check."""
        mock_pinecone_class.return_value = mock_pinecone_client
        
        index = PineconeVectorIndex(
            api_key="test-key",
            index_name="test-index",
            dimension=384,
        )
        
        health = index.health_check()
        
        assert health["status"] == "healthy"
        assert health["provider"] == "pinecone"
        assert health["total_vectors"] == 20

    @patch('engram.vectordb.pinecone_db.Pinecone')
    def test_pinecone_namespace_key_conversion(self, mock_pinecone_class, mock_pinecone_client):
        """Test namespace key conversion for Pinecone."""
        mock_pinecone_class.return_value = mock_pinecone_client
        
        index = PineconeVectorIndex(
            api_key="test-key",
            index_name="test-index",
            dimension=384,
        )
        
        # Test normal namespace
        key = index._get_namespace_key("tenant:user")
        assert key == "tenant-user"
        
        # Test long namespace (should be truncated)
        long_namespace = "very-long-tenant-name-that-exceeds-limit:" + "x" * 50
        key = index._get_namespace_key(long_namespace)
        assert len(key) <= 45
        
        # Test empty namespace (should default)
        key = index._get_namespace_key("")
        assert key == "default"
