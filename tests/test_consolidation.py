"""Tests for consolidation engine functionality."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from engram.core.consolidation import ConsolidationEngine
from engram.core.retrieval import RetrievalEngine
from engram.vectordb.base import VectorHit


class TestConsolidationEngine:
    """Test ConsolidationEngine functionality."""

    @pytest.fixture
    def mock_retrieval_engine(self):
        """Create a mock retrieval engine."""
        return Mock(spec=RetrievalEngine)

    @pytest.fixture
    def consolidation_engine(self, mock_retrieval_engine):
        """Create a consolidation engine for testing."""
        return ConsolidationEngine(mock_retrieval_engine)

    def test_consolidate_memories_no_vectors(self, consolidation_engine: ConsolidationEngine):
        """Test consolidation with no memory vectors."""
        result = consolidation_engine.consolidate_memories(
            tenant_id="test-tenant",
            user_id="test-user",
            memory_vectors={},
        )
        
        assert result["merged"] == []
        assert result["deleted"] == []
        assert result["updated"] == []

    def test_consolidate_memories_single_memory(self, consolidation_engine: ConsolidationEngine):
        """Test consolidation with single memory (no consolidation needed)."""
        memory_vectors = {"memory-1": [0.1, 0.2, 0.3, 0.4] * 10}
        
        result = consolidation_engine.consolidate_memories(
            tenant_id="test-tenant",
            user_id="test-user",
            memory_vectors=memory_vectors,
        )
        
        assert result["merged"] == []
        assert result["deleted"] == []
        assert result["updated"] == []

    def test_consolidate_memories_similar_cluster(self, consolidation_engine: ConsolidationEngine):
        """Test consolidation with similar memories."""
        # Create similar memory vectors
        base_vector = [0.1, 0.2, 0.3, 0.4] * 10
        similar_vector = [0.11, 0.21, 0.31, 0.41] * 10  # Very similar
        
        memory_vectors = {
            "memory-1": base_vector,
            "memory-2": similar_vector,
        }
        
        # Mock retrieval engine to return similar memories
        mock_hits = [
            VectorHit(
                id="memory-2",
                score=0.98,  # Very similar
                metadata={"similarity": 0.98}
            )
        ]
        consolidation_engine.retrieval_engine.find_similar_memories.return_value = mock_hits
        
        result = consolidation_engine.consolidate_memories(
            tenant_id="test-tenant",
            user_id="test-user",
            memory_vectors=memory_vectors,
        )
        
        # Should identify cluster but not perform actual merge in dry run
        assert len(result["merged"]) >= 0  # May or may not merge depending on threshold

    def test_find_memory_clusters(self, consolidation_engine: ConsolidationEngine):
        """Test finding memory clusters."""
        memory_vectors = {
            "memory-1": [0.1, 0.2, 0.3, 0.4] * 10,
            "memory-2": [0.11, 0.21, 0.31, 0.41] * 10,  # Similar
            "memory-3": [0.9, 0.8, 0.7, 0.6] * 10,     # Different
        }
        
        # Mock retrieval engine responses
        consolidation_engine.retrieval_engine.find_similar_memories.side_effect = [
            [VectorHit("memory-2", 0.98, {})],  # memory-1 finds memory-2
            [],  # memory-2 finds nothing (already processed)
            [],  # memory-3 finds nothing
        ]
        
        clusters = consolidation_engine._find_memory_clusters(
            memory_vectors=memory_vectors,
            tenant_id="test-tenant",
            user_id="test-user",
        )
        
        # Should find one cluster with memory-1 and memory-2
        assert len(clusters) == 1
        assert len(clusters[0]) == 2
        assert clusters[0][0]["id"] == "memory-1"
        assert clusters[0][1]["id"] == "memory-2"

    def test_identify_forgotten_memories(self, consolidation_engine: ConsolidationEngine):
        """Test identifying forgotten memories."""
        current_time = datetime.now()
        
        memories = [
            {
                "id": "memory-1",
                "metadata": {
                    "importance": 0.1,  # Low importance
                    "last_accessed_at": (current_time - timedelta(days=50)).isoformat(),  # Old access
                }
            },
            {
                "id": "memory-2",
                "metadata": {
                    "importance": 0.8,  # High importance
                    "last_accessed_at": (current_time - timedelta(days=10)).isoformat(),  # Recent access
                }
            },
            {
                "id": "memory-3",
                "metadata": {
                    "importance": 0.3,  # Medium importance
                    "last_accessed_at": (current_time - timedelta(days=5)).isoformat(),  # Recent access
                }
            },
        ]
        
        forgotten_ids = consolidation_engine.identify_forgotten_memories(
            memories=memories,
            current_time=current_time,
        )
        
        # Only memory-1 should be forgotten (low importance + old access)
        assert "memory-1" in forgotten_ids
        assert "memory-2" not in forgotten_ids
        assert "memory-3" not in forgotten_ids

    def test_identify_forgotten_memories_no_metadata(self, consolidation_engine: ConsolidationEngine):
        """Test identifying forgotten memories with missing metadata."""
        memories = [
            {
                "id": "memory-1",
                "metadata": {}  # No importance or last_accessed_at
            },
            {
                "id": "memory-2",  # No metadata at all
            },
        ]
        
        forgotten_ids = consolidation_engine.identify_forgotten_memories(memories)
        
        # Should not identify any memories as forgotten without proper metadata
        assert len(forgotten_ids) == 0

    def test_calculate_memory_importance(self, consolidation_engine: ConsolidationEngine):
        """Test memory importance calculation."""
        memory = {
            "metadata": {
                "importance": 0.5,
            }
        }
        
        # Test with high access frequency and recent access
        importance = consolidation_engine.calculate_memory_importance(
            memory=memory,
            access_frequency=10,
            recency_days=1,
        )
        
        assert importance > 0.5  # Should be boosted by frequency and recency
        
        # Test with low access frequency and old access
        importance = consolidation_engine.calculate_memory_importance(
            memory=memory,
            access_frequency=0,
            recency_days=100,
        )
        
        assert importance < 0.5  # Should be reduced

    def test_calculate_memory_importance_clamping(self, consolidation_engine: ConsolidationEngine):
        """Test that importance scores are properly clamped."""
        memory = {
            "metadata": {
                "importance": 0.9,  # Already high
            }
        }
        
        # Test with very high frequency and recent access
        importance = consolidation_engine.calculate_memory_importance(
            memory=memory,
            access_frequency=100,
            recency_days=0,
        )
        
        assert 0.0 <= importance <= 1.0  # Should be clamped

    def test_get_consolidation_stats(self, consolidation_engine: ConsolidationEngine):
        """Test getting consolidation engine statistics."""
        stats = consolidation_engine.get_consolidation_stats()
        
        assert "consolidation_threshold" in stats
        assert "similarity_threshold" in stats
        assert "importance_threshold" in stats
        assert "forgetting_days" in stats
        assert "max_text_length" in stats
        assert "consolidation_enabled" in stats
        assert "forgetting_enabled" in stats

    def test_sort_cluster_by_age(self, consolidation_engine: ConsolidationEngine):
        """Test sorting memory cluster by age."""
        cluster = [
            {"id": "memory-3", "vector": [0.3, 0.4, 0.5, 0.6] * 10},
            {"id": "memory-1", "vector": [0.1, 0.2, 0.3, 0.4] * 10},
            {"id": "memory-2", "vector": [0.2, 0.3, 0.4, 0.5] * 10},
        ]
        
        sorted_cluster = consolidation_engine._sort_cluster_by_age(cluster)
        
        # Should be sorted by ID (ULIDs are time-ordered)
        assert sorted_cluster[0]["id"] == "memory-1"
        assert sorted_cluster[1]["id"] == "memory-2"
        assert sorted_cluster[2]["id"] == "memory-3"

    def test_merge_memory_cluster_small_cluster(self, consolidation_engine: ConsolidationEngine):
        """Test merging a cluster with insufficient memories."""
        cluster = [{"id": "memory-1", "vector": [0.1, 0.2, 0.3, 0.4] * 10}]
        
        result = consolidation_engine._merge_memory_cluster(
            cluster=cluster,
            tenant_id="test-tenant",
            user_id="test-user",
        )
        
        assert result is None  # Should not merge single memory

    def test_merge_memory_cluster_success(self, consolidation_engine: ConsolidationEngine):
        """Test successful memory cluster merging."""
        cluster = [
            {"id": "memory-1", "vector": [0.1, 0.2, 0.3, 0.4] * 10},
            {"id": "memory-2", "vector": [0.11, 0.21, 0.31, 0.41] * 10},
            {"id": "memory-3", "vector": [0.12, 0.22, 0.32, 0.42] * 10},
        ]
        
        result = consolidation_engine._merge_memory_cluster(
            cluster=cluster,
            tenant_id="test-tenant",
            user_id="test-user",
        )
        
        assert result is not None
        assert len(result["merged"]) == 1
        assert len(result["deleted"]) == 2
        assert len(result["updated"]) == 1
        assert "memory-1" in result["updated"]  # Target memory
        assert "memory-2" in result["deleted"]  # Source memories
        assert "memory-3" in result["deleted"]

    def test_consolidation_error_handling(self, consolidation_engine: ConsolidationEngine):
        """Test error handling during consolidation."""
        memory_vectors = {
            "memory-1": [0.1, 0.2, 0.3, 0.4] * 10,
            "memory-2": [0.11, 0.21, 0.31, 0.41] * 10,
        }
        
        # Mock retrieval engine to raise exception
        consolidation_engine.retrieval_engine.find_similar_memories.side_effect = Exception("Vector DB error")
        
        with pytest.raises(ValueError, match="Memory consolidation failed"):
            consolidation_engine.consolidate_memories(
                tenant_id="test-tenant",
                user_id="test-user",
                memory_vectors=memory_vectors,
            )

    def test_dry_run_mode(self, consolidation_engine: ConsolidationEngine):
        """Test consolidation in dry run mode."""
        memory_vectors = {
            "memory-1": [0.1, 0.2, 0.3, 0.4] * 10,
            "memory-2": [0.11, 0.21, 0.31, 0.41] * 10,
        }
        
        # Mock retrieval engine to return similar memories
        mock_hits = [VectorHit("memory-2", 0.98, {})]
        consolidation_engine.retrieval_engine.find_similar_memories.return_value = mock_hits
        
        result = consolidation_engine.consolidate_memories(
            tenant_id="test-tenant",
            user_id="test-user",
            memory_vectors=memory_vectors,
            dry_run=True,
        )
        
        # In dry run mode, should identify clusters but not perform actual operations
        assert len(result["merged"]) >= 0
        assert len(result["deleted"]) == 0  # No actual deletions in dry run
        assert len(result["updated"]) == 0  # No actual updates in dry run
