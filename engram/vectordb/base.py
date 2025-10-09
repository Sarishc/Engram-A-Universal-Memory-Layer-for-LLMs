"""Base vector database interface and types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class VectorHit:
    """Represents a vector search result hit."""
    
    id: str
    score: float
    metadata: Dict[str, Any]
    
    def __post_init__(self) -> None:
        """Validate hit data."""
        if not isinstance(self.score, (int, float)):
            raise ValueError(f"Score must be numeric, got {type(self.score)}")
        if not isinstance(self.metadata, dict):
            raise ValueError(f"Metadata must be dict, got {type(self.metadata)}")


class VectorIndex(ABC):
    """Abstract interface for vector database operations."""

    @abstractmethod
    def upsert(
        self,
        items: List[Tuple[str, List[float], Dict[str, Any]]],
        namespace: str,
    ) -> None:
        """Upsert vectors with metadata.
        
        Args:
            items: List of (id, vector, metadata) tuples
            namespace: Namespace/collection identifier (e.g., "tenant:user")
            
        Raises:
            VectorDBError: If upsert operation fails
        """
        pass

    @abstractmethod
    def query(
        self,
        vectors: List[List[float]],
        top_k: int,
        namespace: str,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[List[VectorHit]]:
        """Query similar vectors.
        
        Args:
            vectors: List of query vectors
            top_k: Number of top results to return
            namespace: Namespace/collection identifier
            filter_dict: Optional metadata filters
            
        Returns:
            List of hit lists (one per query vector)
            
        Raises:
            VectorDBError: If query operation fails
        """
        pass

    @abstractmethod
    def delete(
        self,
        ids: List[str],
        namespace: str,
    ) -> None:
        """Delete vectors by IDs.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Namespace/collection identifier
            
        Raises:
            VectorDBError: If delete operation fails
        """
        pass

    @abstractmethod
    def similarity_threshold(
        self,
        vector_a: List[float],
        vector_b: List[float],
    ) -> float:
        """Calculate similarity between two vectors.
        
        Args:
            vector_a: First vector
            vector_b: Second vector
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        pass

    @abstractmethod
    def get_stats(self, namespace: str) -> Dict[str, Any]:
        """Get collection statistics.
        
        Args:
            namespace: Namespace/collection identifier
            
        Returns:
            Dictionary with collection statistics
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this vector database provider.
        
        Returns:
            Provider name string
        """
        pass


class VectorDBError(Exception):
    """Base exception for vector database operations."""

    def __init__(
        self,
        message: str,
        provider_name: str,
        operation: str,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.provider_name = provider_name
        self.operation = operation
        self.original_error = original_error


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vector_a: First vector
        vector_b: Second vector
        
    Returns:
        Cosine similarity score (0.0 to 1.0)
        
    Raises:
        ValueError: If vectors have different dimensions or are empty
    """
    if not vector_a or not vector_b:
        raise ValueError("Vectors cannot be empty")
    
    if len(vector_a) != len(vector_b):
        raise ValueError(f"Vectors must have same dimension: {len(vector_a)} vs {len(vector_b)}")
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    
    # Calculate magnitudes
    magnitude_a = sum(a * a for a in vector_a) ** 0.5
    magnitude_b = sum(b * b for b in vector_b) ** 0.5
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    # Return cosine similarity
    return dot_product / (magnitude_a * magnitude_b)


def euclidean_distance(vector_a: List[float], vector_b: List[float]) -> float:
    """Calculate Euclidean distance between two vectors.
    
    Args:
        vector_a: First vector
        vector_b: Second vector
        
    Returns:
        Euclidean distance
        
    Raises:
        ValueError: If vectors have different dimensions or are empty
    """
    if not vector_a or not vector_b:
        raise ValueError("Vectors cannot be empty")
    
    if len(vector_a) != len(vector_b):
        raise ValueError(f"Vectors must have same dimension: {len(vector_a)} vs {len(vector_b)}")
    
    # Calculate squared differences
    squared_diffs = [(a - b) ** 2 for a, b in zip(vector_a, vector_b)]
    
    # Return Euclidean distance
    return sum(squared_diffs) ** 0.5


def normalize_vector(vector: List[float]) -> List[float]:
    """Normalize a vector to unit length.
    
    Args:
        vector: Input vector
        
    Returns:
        Normalized vector
        
    Raises:
        ValueError: If vector is empty or has zero magnitude
    """
    if not vector:
        raise ValueError("Vector cannot be empty")
    
    magnitude = sum(x * x for x in vector) ** 0.5
    
    if magnitude == 0:
        raise ValueError("Cannot normalize zero vector")
    
    return [x / magnitude for x in vector]
