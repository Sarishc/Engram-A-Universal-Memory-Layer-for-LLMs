"""ChromaDB vector database implementation."""

from typing import Any, Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.errors import ChromaError

from engram.vectordb.base import VectorIndex, VectorHit, VectorDBError, cosine_similarity
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ChromaVectorIndex(VectorIndex):
    """ChromaDB implementation of VectorIndex."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "engram_memories",
        distance_metric: str = "cosine",
    ):
        """Initialize ChromaDB vector index.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
            distance_metric: Distance metric for similarity search
        """
        self.persist_directory = persist_directory or settings.chroma_persist_dir
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_metric},
            )
            
            logger.info(f"Initialized ChromaDB with collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise VectorDBError(
                f"Failed to initialize ChromaDB: {e}",
                provider_name=self.provider_name,
                operation="init",
                original_error=e,
            )

    def _get_namespace_collection(self, namespace: str) -> chromadb.Collection:
        """Get or create collection for namespace.
        
        Args:
            namespace: Namespace identifier
            
        Returns:
            ChromaDB collection for the namespace
        """
        collection_name = f"{self.collection_name}_{namespace.replace(':', '_')}"
        
        try:
            return self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": self.distance_metric},
            )
        except Exception as e:
            logger.error(f"Failed to get/create collection {collection_name}: {e}")
            raise VectorDBError(
                f"Failed to get/create collection: {e}",
                provider_name=self.provider_name,
                operation="get_collection",
                original_error=e,
            )

    def upsert(
        self,
        items: List[Tuple[str, List[float], Dict[str, Any]]],
        namespace: str,
    ) -> None:
        """Upsert vectors with metadata.
        
        Args:
            items: List of (id, vector, metadata) tuples
            namespace: Namespace/collection identifier
            
        Raises:
            VectorDBError: If upsert operation fails
        """
        if not items:
            return

        try:
            collection = self._get_namespace_collection(namespace)
            
            # Separate data
            ids = [item[0] for item in items]
            vectors = [item[1] for item in items]
            metadatas = [item[2] for item in items]
            
            # Add namespace to metadata
            for metadata in metadatas:
                metadata["namespace"] = namespace
            
            # Upsert to ChromaDB
            collection.upsert(
                ids=ids,
                embeddings=vectors,
                metadatas=metadatas,
            )
            
            logger.debug(f"Upserted {len(items)} vectors to namespace: {namespace}")
            
        except ChromaError as e:
            logger.error(f"ChromaDB upsert failed: {e}")
            raise VectorDBError(
                f"ChromaDB upsert failed: {e}",
                provider_name=self.provider_name,
                operation="upsert",
                original_error=e,
            )
        except Exception as e:
            logger.error(f"Unexpected error during upsert: {e}")
            raise VectorDBError(
                f"Unexpected error during upsert: {e}",
                provider_name=self.provider_name,
                operation="upsert",
                original_error=e,
            )

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
        if not vectors:
            return []

        try:
            collection = self._get_namespace_collection(namespace)
            
            # Add namespace filter
            where_filter = filter_dict or {}
            where_filter["namespace"] = namespace
            
            # Query ChromaDB
            results = collection.query(
                query_embeddings=vectors,
                n_results=top_k,
                where=where_filter if where_filter else None,
                include=["metadatas", "distances"],
            )
            
            # Convert to VectorHit objects
            hits_list = []
            for i, (ids, distances, metadatas) in enumerate(
                zip(results["ids"], results["distances"], results["metadatas"])
            ):
                hits = []
                for id_, distance, metadata in zip(ids, distances, metadatas):
                    # Convert distance to similarity score
                    if self.distance_metric == "cosine":
                        score = 1.0 - distance  # ChromaDB returns cosine distance
                    else:
                        score = 1.0 / (1.0 + distance)  # Convert distance to similarity
                    
                    hit = VectorHit(
                        id=id_,
                        score=max(0.0, min(1.0, score)),  # Clamp to [0, 1]
                        metadata=metadata or {},
                    )
                    hits.append(hit)
                
                hits_list.append(hits)
            
            logger.debug(f"Queried {len(vectors)} vectors, got {len(hits_list)} result sets")
            return hits_list
            
        except ChromaError as e:
            logger.error(f"ChromaDB query failed: {e}")
            raise VectorDBError(
                f"ChromaDB query failed: {e}",
                provider_name=self.provider_name,
                operation="query",
                original_error=e,
            )
        except Exception as e:
            logger.error(f"Unexpected error during query: {e}")
            raise VectorDBError(
                f"Unexpected error during query: {e}",
                provider_name=self.provider_name,
                operation="query",
                original_error=e,
            )

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
        if not ids:
            return

        try:
            collection = self._get_namespace_collection(namespace)
            
            # Delete from ChromaDB
            collection.delete(ids=ids)
            
            logger.debug(f"Deleted {len(ids)} vectors from namespace: {namespace}")
            
        except ChromaError as e:
            logger.error(f"ChromaDB delete failed: {e}")
            raise VectorDBError(
                f"ChromaDB delete failed: {e}",
                provider_name=self.provider_name,
                operation="delete",
                original_error=e,
            )
        except Exception as e:
            logger.error(f"Unexpected error during delete: {e}")
            raise VectorDBError(
                f"Unexpected error during delete: {e}",
                provider_name=self.provider_name,
                operation="delete",
                original_error=e,
            )

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
        return cosine_similarity(vector_a, vector_b)

    def get_stats(self, namespace: str) -> Dict[str, Any]:
        """Get collection statistics.
        
        Args:
            namespace: Namespace/collection identifier
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self._get_namespace_collection(namespace)
            
            # Get collection count
            count = collection.count()
            
            return {
                "namespace": namespace,
                "total_vectors": count,
                "collection_name": collection.name,
                "distance_metric": self.distance_metric,
                "provider": self.provider_name,
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for namespace {namespace}: {e}")
            return {
                "namespace": namespace,
                "total_vectors": 0,
                "error": str(e),
                "provider": self.provider_name,
            }

    @property
    def provider_name(self) -> str:
        """Get the name of this vector database provider.
        
        Returns:
            Provider name string
        """
        return "chromadb"

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on ChromaDB.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Try to get collection info
            count = self.collection.count()
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "total_vectors": count,
                "persist_directory": self.persist_directory,
            }
            
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e),
            }
