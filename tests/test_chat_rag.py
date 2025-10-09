"""Tests for RAG chat functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from engram.api.chat_routes import ChatAPI, ChatMessage, RetrievalHints


class TestChatAPI:
    """Test chat API functionality."""
    
    def test_chat_api_init(self):
        """Test chat API initialization."""
        chat_api = ChatAPI()
        assert chat_api.memory_store is not None
        assert chat_api.retrieval_engine is not None
    
    def test_build_memory_context_empty(self):
        """Test building memory context with no memories."""
        chat_api = ChatAPI()
        context = chat_api._build_memory_context([])
        assert context == ""
    
    def test_build_memory_context_with_memories(self):
        """Test building memory context with memories."""
        chat_api = ChatAPI()
        
        memories = [
            {
                "text": "Test memory 1",
                "modality": "text",
                "source_uri": "test.pdf",
                "score": 0.8
            },
            {
                "text": "Test memory 2",
                "modality": "image",
                "source_uri": None,
                "score": 0.7
            }
        ]
        
        context = chat_api._build_memory_context(memories)
        
        assert "[MEMORY CONTEXT START]" in context
        assert "[MEMORY CONTEXT END]" in context
        assert "Test memory 1" in context
        assert "Test memory 2" in context
        assert "test.pdf" in context
        assert "TEXT:" in context
        assert "IMAGE:" in context
    
    @pytest.mark.asyncio
    async def test_retrieve_memories_empty(self):
        """Test retrieving memories with empty result."""
        chat_api = ChatAPI()
        
        with patch.object(chat_api.retrieval_engine, 'retrieve', return_value=[]):
            memories = await chat_api._retrieve_memories(
                tenant_id="test-tenant",
                user_id="test-user",
                query="test query"
            )
            
            assert memories == []
    
    @pytest.mark.asyncio
    async def test_retrieve_memories_with_results(self):
        """Test retrieving memories with results."""
        chat_api = ChatAPI()
        
        mock_results = [
            {
                "memory_id": "mem1",
                "text": "Test memory",
                "score": 0.8,
                "metadata": {"modality": "text", "source_uri": "test.pdf"},
                "importance": 0.5,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        with patch.object(chat_api.retrieval_engine, 'retrieve', return_value=mock_results):
            memories = await chat_api._retrieve_memories(
                tenant_id="test-tenant",
                user_id="test-user",
                query="test query"
            )
            
            assert len(memories) == 1
            assert memories[0]["memory_id"] == "mem1"
            assert memories[0]["text"] == "Test memory"
            assert memories[0]["score"] == 0.8


class TestChatMessage:
    """Test chat message model."""
    
    def test_chat_message_creation(self):
        """Test creating chat messages."""
        message = ChatMessage(role="user", content="Hello")
        
        assert message.role == "user"
        assert message.content == "Hello"
    
    def test_chat_message_validation(self):
        """Test chat message validation."""
        with pytest.raises(ValueError):
            ChatMessage(role="invalid", content="Hello")


class TestRetrievalHints:
    """Test retrieval hints model."""
    
    def test_retrieval_hints_default(self):
        """Test default retrieval hints."""
        hints = RetrievalHints()
        
        assert hints.modalities is None
        assert hints.k == 10
    
    def test_retrieval_hints_custom(self):
        """Test custom retrieval hints."""
        hints = RetrievalHints(
            modalities=["text", "image"],
            k=5
        )
        
        assert hints.modalities == ["text", "image"]
        assert hints.k == 5
