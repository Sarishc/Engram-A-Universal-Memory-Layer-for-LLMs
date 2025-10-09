"""Tests for memory store functionality."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from engram.core.memory_store import MemoryStore
from engram.database.models import Tenant, Memory, UserMemoryStats
from engram.vectordb.base import VectorHit


class TestMemoryStore:
    """Test MemoryStore functionality."""

    def test_create_tenant(self, memory_store: MemoryStore, sample_tenant_data):
        """Test tenant creation."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            with patch.object(memory_store.db, 'add') as mock_add:
                with patch.object(memory_store.db, 'commit') as mock_commit:
                    with patch.object(memory_store.db, 'refresh') as mock_refresh:
                        tenant = memory_store.create_tenant(sample_tenant_data["name"])
                        
                        assert tenant.name == sample_tenant_data["name"]
                        mock_add.assert_called_once()
                        mock_commit.assert_called_once()

    def test_create_tenant_duplicate(self, memory_store: MemoryStore, sample_tenant_data):
        """Test tenant creation with duplicate name."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_existing = Mock()
            mock_existing.name = sample_tenant_data["name"]
            mock_query.return_value.filter.return_value.first.return_value = mock_existing
            
            with pytest.raises(ValueError, match="already exists"):
                memory_store.create_tenant(sample_tenant_data["name"])

    def test_get_tenant(self, memory_store: MemoryStore):
        """Test getting tenant by ID."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_tenant = Mock()
            mock_tenant.id = "test-tenant-id"
            mock_tenant.name = "test-tenant"
            mock_query.return_value.filter.return_value.first.return_value = mock_tenant
            
            tenant = memory_store.get_tenant("test-tenant-id")
            
            assert tenant.id == "test-tenant-id"
            assert tenant.name == "test-tenant"

    def test_get_tenant_not_found(self, memory_store: MemoryStore):
        """Test getting non-existent tenant."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            tenant = memory_store.get_tenant("non-existent-id")
            
            assert tenant is None

    def test_upsert_memories(self, memory_store: MemoryStore, sample_memory_data):
        """Test memory upsert."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_tenant = Mock()
            mock_tenant.id = sample_memory_data["tenant_id"]
            mock_query.return_value.filter.return_value.first.return_value = mock_tenant
            
            with patch.object(memory_store.db, 'add_all') as mock_add_all:
                with patch.object(memory_store.db, 'commit') as mock_commit:
                    memories = memory_store.upsert_memories(
                        tenant_id=sample_memory_data["tenant_id"],
                        user_id=sample_memory_data["user_id"],
                        texts=sample_memory_data["texts"],
                        metadata_list=sample_memory_data["metadata"],
                        importance_list=sample_memory_data["importance"],
                    )
                    
                    assert len(memories) == len(sample_memory_data["texts"])
                    mock_add_all.assert_called_once()
                    mock_commit.assert_called_once()
                    memory_store.vector_index.upsert.assert_called_once()

    def test_upsert_memories_tenant_not_found(self, memory_store: MemoryStore, sample_memory_data):
        """Test memory upsert with non-existent tenant."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            with pytest.raises(ValueError, match="not found"):
                memory_store.upsert_memories(
                    tenant_id=sample_memory_data["tenant_id"],
                    user_id=sample_memory_data["user_id"],
                    texts=sample_memory_data["texts"],
                )

    def test_retrieve_memories(self, memory_store: MemoryStore, sample_retrieval_data):
        """Test memory retrieval."""
        mock_memories = [
            Mock(
                id="memory-1",
                text="User prefers dark mode",
                metadata={"category": "preferences"},
                importance=0.8,
                created_at=datetime.now(),
                last_accessed_at=datetime.now(),
            )
        ]
        
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = mock_memories
            
            results = memory_store.retrieve_memories(
                tenant_id=sample_retrieval_data["tenant_id"],
                user_id=sample_retrieval_data["user_id"],
                query=sample_retrieval_data["query"],
                top_k=sample_retrieval_data["top_k"],
            )
            
            assert len(results) == 1
            assert results[0]["memory_id"] == "memory-1"
            assert results[0]["text"] == "User prefers dark mode"
            assert results[0]["score"] == 0.9  # From mock vector index

    def test_retrieve_memories_empty(self, memory_store: MemoryStore, sample_retrieval_data):
        """Test memory retrieval with no results."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = []
            
            results = memory_store.retrieve_memories(
                tenant_id=sample_retrieval_data["tenant_id"],
                user_id=sample_retrieval_data["user_id"],
                query=sample_retrieval_data["query"],
                top_k=sample_retrieval_data["top_k"],
            )
            
            assert len(results) == 0

    def test_delete_memory(self, memory_store: MemoryStore):
        """Test memory deletion."""
        mock_memory = Mock()
        mock_memory.id = "memory-1"
        mock_memory.active = True
        
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_memory
            
            with patch.object(memory_store.db, 'commit') as mock_commit:
                success = memory_store.delete_memory(
                    memory_id="memory-1",
                    tenant_id="test-tenant-id",
                    user_id="test-user-id",
                )
                
                assert success is True
                assert mock_memory.active is False
                mock_commit.assert_called_once()
                memory_store.vector_index.delete.assert_called_once()

    def test_delete_memory_not_found(self, memory_store: MemoryStore):
        """Test memory deletion with non-existent memory."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            success = memory_store.delete_memory(
                memory_id="non-existent-memory",
                tenant_id="test-tenant-id",
                user_id="test-user-id",
            )
            
            assert success is False

    def test_list_memories(self, memory_store: MemoryStore):
        """Test memory listing."""
        mock_memories = [
            Mock(id="memory-1", text="Test memory 1"),
            Mock(id="memory-2", text="Test memory 2"),
        ]
        
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_memories
            
            memories = memory_store.list_memories(
                tenant_id="test-tenant-id",
                user_id="test-user-id",
                limit=10,
                offset=0,
            )
            
            assert len(memories) == 2
            assert memories[0].id == "memory-1"

    def test_get_user_stats(self, memory_store: MemoryStore):
        """Test getting user statistics."""
        mock_stats = Mock()
        mock_stats.tenant_id = "test-tenant-id"
        mock_stats.user_id = "test-user-id"
        mock_stats.total_memories = 10
        mock_stats.active_memories = 8
        
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_stats
            
            stats = memory_store.get_user_stats(
                tenant_id="test-tenant-id",
                user_id="test-user-id",
            )
            
            assert stats.tenant_id == "test-tenant-id"
            assert stats.total_memories == 10

    def test_get_store_stats(self, memory_store: MemoryStore):
        """Test getting store statistics."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_query.return_value.scalar.side_effect = [5, 100, 95]  # tenants, total, active
            
            stats = memory_store.get_store_stats()
            
            assert stats["total_tenants"] == 5
            assert stats["total_memories"] == 100
            assert stats["active_memories"] == 95
            assert stats["vector_provider"] == "test"

    def test_upsert_memories_text_truncation(self, memory_store: MemoryStore):
        """Test memory upsert with text truncation."""
        long_text = "x" * 3000  # Exceeds max_text_length
        
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_tenant = Mock()
            mock_query.return_value.filter.return_value.first.return_value = mock_tenant
            
            with patch.object(memory_store.db, 'add_all') as mock_add_all:
                with patch.object(memory_store.db, 'commit') as mock_commit:
                    memories = memory_store.upsert_memories(
                        tenant_id="test-tenant-id",
                        user_id="test-user-id",
                        texts=[long_text],
                    )
                    
                    assert len(memories) == 1
                    assert len(memories[0].text) <= 2048
                    assert "original" in memories[0].metadata

    def test_upsert_memories_embedding_error(self, memory_store: MemoryStore):
        """Test memory upsert with embedding generation error."""
        memory_store.embeddings_facade.embed_texts.side_effect = ValueError("Embedding error")
        
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_tenant = Mock()
            mock_query.return_value.filter.return_value.first.return_value = mock_tenant
            
            with pytest.raises(ValueError, match="Memory upsert failed"):
                memory_store.upsert_memories(
                    tenant_id="test-tenant-id",
                    user_id="test-user-id",
                    texts=["test text"],
                )

    def test_retrieve_memories_embedding_error(self, memory_store: MemoryStore, sample_retrieval_data):
        """Test memory retrieval with embedding generation error."""
        memory_store.embeddings_facade.embed_texts.side_effect = ValueError("Embedding error")
        
        with pytest.raises(ValueError, match="Memory retrieval failed"):
            memory_store.retrieve_memories(
                tenant_id=sample_retrieval_data["tenant_id"],
                user_id=sample_retrieval_data["user_id"],
                query=sample_retrieval_data["query"],
            )

    def test_database_rollback_on_error(self, memory_store: MemoryStore, sample_memory_data):
        """Test database rollback on upsert error."""
        with patch.object(memory_store.db, 'query') as mock_query:
            mock_tenant = Mock()
            mock_query.return_value.filter.return_value.first.return_value = mock_tenant
            
            with patch.object(memory_store.db, 'add_all') as mock_add_all:
                mock_add_all.side_effect = Exception("Database error")
                
                with patch.object(memory_store.db, 'rollback') as mock_rollback:
                    with pytest.raises(ValueError):
                        memory_store.upsert_memories(
                            tenant_id=sample_memory_data["tenant_id"],
                            user_id=sample_memory_data["user_id"],
                            texts=sample_memory_data["texts"],
                        )
                    
                    mock_rollback.assert_called_once()
