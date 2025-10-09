"""Pinecone vector database implementation."""

from typing import Any, Dict, List, Optional, Tuple

import pinecone

from engram.vectordb.base import VectorIndex, VectorHit, VectorDBError, cosine_similarity
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PineconeVectorIndex(VectorIndex):
    """Pinecone implementation of VectorIndex."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: Optional[str] = None,
        dimension: Optional[int] = None,
        metric: str = "cosine",
    ):
        """Initialize Pinecone vector index.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment (deprecated, not used in v3+)
            index_name: Name of the Pinecone index
            dimension: Vector dimension (required for new indexes)
            metric: Distance metric for similarity search
        """
        self.api_key = api_key or settings.pinecone_api_key
        self.environment = environment or settings.pinecone_environment
        self.index_name = index_name or settings.pinecone_index
        self.dimension = dimension
        self.metric = metric
        
        if not self.api_key:
            raise VectorDBError(
                "Pinecone API key not provided",
                provider_name=self.provider_name,
                operation="init",
            )
        
        try:
            # Initialize Pinecone client
            pinecone.init(api_key=self.api_key)
            
            # Get or create index
            if self.index_name not in [idx.name for idx in pinecone.list_indexes()]:
                if not self.dimension:
                    raise VectorDBError(
                        "Dimension required for new Pinecone index",
                        provider_name=self.provider_name,
                        operation="create_index",
                    )
                
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                )
                logger.info(f"Created new Pinecone index: {self.index_name}")
            else:
                logger.info(f"Using existing Pinecone index: {self.index_name}")
            
            # Get index instance
            self.index = pinecone.Index(self.index_name)
            
            # Get index stats to determine dimension if not provided
            if not self.dimension:
                stats = self.index.describe_index_stats()
                self.dimension = stats.dimension
            
            logger.info(f"Initialized Pinecone with index: {self.index_name}, dimension: {self.dimension}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise VectorDBError(
                f"Failed to initialize Pinecone: {e}",
                provider_name=self.provider_name,
                operation="init",
                original_error=e,
            )

    def _get_namespace_key(self, namespace: str) -> str:
        """Convert namespace to Pinecone namespace format.
        
        Args:
            namespace: Namespace identifier
            
        Returns:
            Pinecone namespace string
        """
        # Pinecone namespaces are limited to 45 characters and alphanumeric + hyphen
        # Convert colons to hyphens and ensure valid format
        safe_namespace = namespace.replace(":", "-").replace("_", "-")
        
        # Ensure it's not empty and within length limit
        if not safe_namespace:
            safe_namespace = "default"
        
        if len(safe_namespace) > 45:
            safe_namespace = safe_namespace[:45]
        
        return safe_namespace

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
            pinecone_namespace = self._get_namespace_key(namespace)
            
            # Prepare vectors for Pinecone
            vectors_to_upsert = []
            for memory_id, vector, metadata in items:
                # Add namespace to metadata
                metadata["namespace"] = namespace
                
                # Create unique ID with namespace prefix
                pinecone_id = f"{namespace}:{memory_id}"
                
                vectors_to_upsert.append({
                    "id": pinecone_id,
                    "values": vector,
                    "metadata": metadata,
                })
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=vectors_to_upsert,
                namespace=pinecone_namespace,
            )
            
            logger.debug(f"Upserted {len(items)} vectors to namespace: {namespace}")
            
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")
            raise VectorDBError(
                f"Pinecone upsert failed: {e}",
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
            pinecone_namespace = self._get_namespace_key(namespace)
            
            # Add namespace filter
            where_filter = filter_dict or {}
            where_filter["namespace"] = namespace
            
            # Query Pinecone
            results = self.index.query(
                vector=vectors,
                top_k=top_k,
                namespace=pinecone_namespace,
                filter=where_filter if where_filter else None,
                include_metadata=True,
            )
            
            # Convert to VectorHit objects
            hits_list = []
            for query_result in results.matches:
                hits = []
                for match in query_result:
                    # Extract original memory ID from Pinecone ID
                    pinecone_id = match.id
                    memory_id = pinecone_id.split(":", 1)[1] if ":" in pinecone_id else pinecone_id
                    
                    hit = VectorHit(
                        id=memory_id,
                        score=match.score or 0.0,
                        metadata=match.metadata or {},
                    )
                    hits.append(hit)
                
                hits_list.append(hits)
            
            logger.debug(f"Queried {len(vectors)} vectors, got {len(hits_list)} result sets")
            return hits_list
            
        except Exception as e:
            logger.error(f"Pinecone query failed: {e}")
            raise VectorDBError(
                f"Pinecone query failed: {e}",
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
            pinecone_namespace = self._get_namespace_key(namespace)
            
            # Create Pinecone IDs with namespace prefix
            pinecone_ids = [f"{namespace}:{memory_id}" for memory_id in ids]
            
            # Delete from Pinecone
            self.index.delete(
                ids=pinecone_ids,
                namespace=pinecone_namespace,
            )
            
            logger.debug(f"Deleted {len(ids)} vectors from namespace: {namespace}")
            
        except Exception as e:
            logger.error(f"Pinecone delete failed: {e}")
            raise VectorDBError(
                f"Pinecone delete failed: {e}",
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
            pinecone_namespace = self._get_namespace_key(namespace)
            
            # Get index stats
            stats = self.index.describe_index_stats()
            
            # Get namespace-specific stats
            namespace_stats = stats.namespaces.get(pinecone_namespace, {})
            
            return {
                "namespace": namespace,
                "total_vectors": namespace_stats.get("vector_count", 0),
                "index_name": self.index_name,
                "dimension": self.dimension,
                "metric": self.metric,
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
        return "pinecone"

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Pinecone.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Try to get index stats
            stats = self.index.describe_index_stats()
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "index_name": self.index_name,
                "total_vectors": stats.total_vector_count,
                "dimension": self.dimension,
            }
            
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e),
            }
