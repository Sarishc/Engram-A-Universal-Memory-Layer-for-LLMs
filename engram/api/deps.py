"""Dependency injection helpers for FastAPI."""

from functools import lru_cache
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from engram.core.memory_store import MemoryStore
from engram.core.embeddings import EmbeddingsFacade
from engram.database.postgres import get_db_session
from engram.utils.config import get_settings
from engram.utils.logger import get_logger
from engram.vectordb.chroma_db import ChromaVectorIndex
from engram.vectordb.pinecone_db import PineconeVectorIndex

logger = get_logger(__name__)
settings = get_settings()


@lru_cache()
def get_vector_index():
    """Get vector database index instance.
    
    Returns:
        VectorIndex instance
    """
    try:
        if settings.vector_backend == "pinecone":
            if not settings.pinecone_api_key:
                logger.warning("Pinecone API key not configured, falling back to ChromaDB")
                return ChromaVectorIndex()
            return PineconeVectorIndex()
        else:
            return ChromaVectorIndex()
    except Exception as e:
        logger.error(f"Failed to initialize vector index: {e}")
        # Fallback to ChromaDB
        logger.info("Falling back to ChromaDB")
        return ChromaVectorIndex()


@lru_cache()
def get_embeddings_facade():
    """Get embeddings facade instance.
    
    Returns:
        EmbeddingsFacade instance
    """
    return EmbeddingsFacade()


def get_memory_store(
    db: Session = Depends(get_db_session),
    vector_index = Depends(get_vector_index),
    embeddings_facade = Depends(get_embeddings_facade),
) -> Generator[MemoryStore, None, None]:
    """Get memory store instance.
    
    Args:
        db: Database session
        vector_index: Vector database index
        embeddings_facade: Embeddings facade
        
    Yields:
        MemoryStore instance
    """
    try:
        memory_store = MemoryStore(
            db_session=db,
            vector_index=vector_index,
            embeddings_facade=embeddings_facade,
        )
        yield memory_store
    except Exception as e:
        logger.error(f"Failed to create memory store: {e}")
        raise
    finally:
        # Cleanup if needed
        pass
