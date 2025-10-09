"""Tests for retrieval engine functionality."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from engram.core.retrieval import RetrievalEngine
from engram.vectordb.base import VectorHit


class TestRetrievalEngine:
    """Test RetrievalEngine functionality."""

    @pytest.fixture
    def retrieval_engine(self, mock_vector_index):
        """Create a retrieval engine for testing."""
        return RetrievalEngine(mock_vector_index)

    def test_retrieve_memories(self, retrieval_engine: RetrievalEngine):
        """Test basic memory retrieval."""
        query_vector = [0.1, 0.2, 0.3, 0.4] * 10  # 40-dim vector
        
        hits = retrieval_engine.retrieve_memories(
            query_vector=query_vector,
            tenant_id="test-tenant",
            user_id="test-user",
            top_k=5,
        )
        
        assert len(hits) == 1  # From mock vector index
        assert hits[0].id == "test-id"
        assert hits[0].score == 0.9

    def test_retrieve_memories_empty_query(self, retrieval_engine: RetrievalEngine):
        """Test retrieval with empty query vector."""
        hits = retrieval_engine.retrieve_memories(
            query_vector=[],
            tenant_id="test-tenant",
            user_id="test-user",
        )
        
        assert len(hits) == 0

    def test_rerank_hits(self, retrieval_engine: RetrievalEngine):
        """Test hit re-ranking with composite scoring."""
        # Create mock hits with different metadata
        hits = [
            VectorHit(
                id="memory-1",
                score=0.9,
                metadata={
                    "importance": 0.8,
                    "last_accessed_at": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                }
            ),
            VectorHit(
                id="memory-2",
                score=0.7,
                metadata={
                    "importance": 0.9,
                    "last_accessed_at": (datetime.now() - timedelta(days=30)).isoformat(),
                    "created_at": (datetime.now() - timedelta(days=60)).isoformat(),
                }
            ),
        ]
        
        query_vector = [0.1, 0.2, 0.3, 0.4] * 10
        
        reranked_hits = retrieval_engine._rerank_hits(hits, query_vector)
        
        assert len(reranked_hits) == 2
        # First hit should have higher composite score due to recency
        assert reranked_hits[0].score >= reranked_hits[1].score

    def test_calculate_recency_boost_recent(self, retrieval_engine: RetrievalEngine):
        """Test recency boost calculation for recent access."""
        recent_time = datetime.now().isoformat()
        
        boost = retrieval_engine._calculate_recency_boost(recent_time, None)
        
        assert boost > 0.8  # Should be high for recent access

    def test_calculate_recency_boost_old(self, retrieval_engine: RetrievalEngine):
        """Test recency boost calculation for old access."""
        old_time = (datetime.now() - timedelta(days=100)).isoformat()
        
        boost = retrieval_engine._calculate_recency_boost(old_time, None)
        
        assert boost < 0.1  # Should be low for old access

    def test_calculate_recency_boost_no_timestamp(self, retrieval_engine: RetrievalEngine):
        """Test recency boost calculation with no timestamp."""
        boost = retrieval_engine._calculate_recency_boost(None, None)
        
        assert boost == 0.0

    def test_calculate_recency_boost_invalid_timestamp(self, retrieval_engine: RetrievalEngine):
        """Test recency boost calculation with invalid timestamp."""
        boost = retrieval_engine._calculate_recency_boost("invalid-timestamp", None)
        
        assert boost == 0.0

    def test_calculate_decay_penalty_recent(self, retrieval_engine: RetrievalEngine):
        """Test decay penalty calculation for recent memory."""
        recent_time = datetime.now().isoformat()
        
        penalty = retrieval_engine._calculate_decay_penalty(recent_time, 1.0)
        
        assert penalty < 0.1  # Should be low for recent memory with full decay weight

    def test_calculate_decay_penalty_old(self, retrieval_engine: RetrievalEngine):
        """Test decay penalty calculation for old memory."""
        old_time = (datetime.now() - timedelta(days=365)).isoformat()
        
        penalty = retrieval_engine._calculate_decay_penalty(old_time, 0.5)
        
        assert penalty > 0.0  # Should have some penalty for old memory

    def test_calculate_decay_penalty_no_timestamp(self, retrieval_engine: RetrievalEngine):
        """Test decay penalty calculation with no timestamp."""
        penalty = retrieval_engine._calculate_decay_penalty(None, 1.0)
        
        assert penalty == 0.0

    def test_find_similar_memories(self, retrieval_engine: RetrievalEngine):
        """Test finding similar memories."""
        memory_vector = [0.1, 0.2, 0.3, 0.4] * 10
        
        similar_hits = retrieval_engine.find_similar_memories(
            memory_vector=memory_vector,
            tenant_id="test-tenant",
            user_id="test-user",
            similarity_threshold=0.8,
        )
        
        assert len(similar_hits) == 1
        assert similar_hits[0].score >= 0.8

    def test_find_similar_memories_exclude_id(self, retrieval_engine: RetrievalEngine):
        """Test finding similar memories with excluded ID."""
        memory_vector = [0.1, 0.2, 0.3, 0.4] * 10
        
        similar_hits = retrieval_engine.find_similar_memories(
            memory_vector=memory_vector,
            tenant_id="test-tenant",
            user_id="test-user",
            exclude_id="test-id",  # Should exclude this ID
        )
        
        # Should still return results but without the excluded ID
        assert len(similar_hits) == 0  # Mock returns same ID, so excluded

    def test_get_retrieval_stats(self, retrieval_engine: RetrievalEngine):
        """Test getting retrieval engine statistics."""
        stats = retrieval_engine.get_retrieval_stats()
        
        assert "alpha" in stats
        assert "beta" in stats
        assert "gamma" in stats
        assert "delta" in stats
        assert "tau_days" in stats
        assert stats["vector_provider"] == "test"

    def test_score_clamping(self, retrieval_engine: RetrievalEngine):
        """Test that composite scores are properly clamped to [0, 1]."""
        # Create hits with extreme metadata values
        hits = [
            VectorHit(
                id="memory-1",
                score=1.5,  # Extreme score
                metadata={
                    "importance": 2.0,  # Extreme importance
                    "last_accessed_at": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                }
            ),
            VectorHit(
                id="memory-2",
                score=-0.5,  # Negative score
                metadata={
                    "importance": -1.0,  # Negative importance
                    "last_accessed_at": (datetime.now() - timedelta(days=1000)).isoformat(),
                    "created_at": (datetime.now() - timedelta(days=1000)).isoformat(),
                }
            ),
        ]
        
        query_vector = [0.1, 0.2, 0.3, 0.4] * 10
        
        reranked_hits = retrieval_engine._rerank_hits(hits, query_vector)
        
        for hit in reranked_hits:
            assert 0.0 <= hit.score <= 1.0

    def test_metadata_enrichment(self, retrieval_engine: RetrievalEngine):
        """Test that reranked hits have enriched metadata."""
        hits = [
            VectorHit(
                id="memory-1",
                score=0.8,
                metadata={
                    "importance": 0.7,
                    "last_accessed_at": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                }
            )
        ]
        
        query_vector = [0.1, 0.2, 0.3, 0.4] * 10
        
        reranked_hits = retrieval_engine._rerank_hits(hits, query_vector)
        
        assert len(reranked_hits) == 1
        hit = reranked_hits[0]
        
        # Check that metadata is enriched
        assert "original_score" in hit.metadata
        assert "recency_boost" in hit.metadata
        assert "decay_penalty" in hit.metadata
        assert "composite_score" in hit.metadata
        
        assert hit.metadata["original_score"] == 0.8

    def test_ranking_consistency(self, retrieval_engine: RetrievalEngine):
        """Test that ranking is consistent across multiple runs."""
        hits = [
            VectorHit(
                id="memory-1",
                score=0.8,
                metadata={
                    "importance": 0.9,
                    "last_accessed_at": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                }
            ),
            VectorHit(
                id="memory-2",
                score=0.7,
                metadata={
                    "importance": 0.6,
                    "last_accessed_at": (datetime.now() - timedelta(days=30)).isoformat(),
                    "created_at": (datetime.now() - timedelta(days=60)).isoformat(),
                }
            ),
        ]
        
        query_vector = [0.1, 0.2, 0.3, 0.4] * 10
        
        # Run ranking multiple times
        results = []
        for _ in range(3):
            reranked_hits = retrieval_engine._rerank_hits(hits, query_vector)
            results.append([hit.id for hit in reranked_hits])
        
        # All runs should produce the same ranking
        assert all(result == results[0] for result in results)

    def test_empty_hits_reranking(self, retrieval_engine: RetrievalEngine):
        """Test reranking with empty hits list."""
        hits = []
        query_vector = [0.1, 0.2, 0.3, 0.4] * 10
        
        reranked_hits = retrieval_engine._rerank_hits(hits, query_vector)
        
        assert len(reranked_hits) == 0

    def test_vector_index_error_handling(self, retrieval_engine: RetrievalEngine):
        """Test error handling when vector index fails."""
        retrieval_engine.vector_index.query.side_effect = Exception("Vector DB error")
        
        with pytest.raises(ValueError, match="Memory retrieval failed"):
            retrieval_engine.retrieve_memories(
                query_vector=[0.1, 0.2, 0.3, 0.4] * 10,
                tenant_id="test-tenant",
                user_id="test-user",
            )
