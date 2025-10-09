"""Retrieval engine for semantic memory search and ranking."""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from engram.vectordb.base import VectorIndex, VectorHit
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

if TYPE_CHECKING:
    from engram.core.memory_store import MemoryStore

logger = get_logger(__name__)
settings = get_settings()


class RetrievalEngine:
    """Engine for retrieving and ranking memories based on semantic similarity."""

    def __init__(self, vector_index: Optional[VectorIndex] = None):
        """Initialize retrieval engine.
        
        Args:
            vector_index: Optional vector database interface
        """
        self.vector_index = vector_index
        self.alpha = settings.rank_alpha  # Cosine similarity weight
        self.beta = settings.rank_beta    # Recency boost weight
        self.gamma = settings.rank_gamma  # Importance weight
        self.delta = settings.rank_delta  # Decay penalty weight
        self.tau_days = settings.recency_tau_days

    def retrieve_memories(
        self,
        query_vector: List[float],
        tenant_id: str,
        user_id: str,
        top_k: Optional[int] = None,
        filter_dict: Optional[Dict[str, any]] = None,
    ) -> List[VectorHit]:
        """Retrieve and rank memories for a query.
        
        Args:
            query_vector: Query embedding vector
            tenant_id: Tenant identifier
            user_id: User identifier
            top_k: Number of top results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of ranked VectorHit objects
        """
        top_k = top_k or settings.default_max_memories
        namespace = f"{tenant_id}:{user_id}"
        
        try:
            logger.debug(f"Retrieving memories for tenant={tenant_id}, user={user_id}, top_k={top_k}")
            
            # Query vector database
            results = self.vector_index.query(
                vectors=[query_vector],
                top_k=top_k * 2,  # Get more results for re-ranking
                namespace=namespace,
                filter_dict=filter_dict,
            )
            
            if not results or not results[0]:
                logger.debug("No memories found in vector database")
                return []
            
            hits = results[0]
            
            # Re-rank results using composite scoring
            ranked_hits = self._rerank_hits(hits, query_vector)
            
            # Return top_k results
            final_results = ranked_hits[:top_k]
            
            logger.debug(f"Retrieved {len(final_results)} ranked memories")
            return final_results
            
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            raise ValueError(f"Memory retrieval failed: {e}")

    def _rerank_hits(
        self,
        hits: List[VectorHit],
        query_vector: List[float],
    ) -> List[VectorHit]:
        """Re-rank hits using composite scoring.
        
        Args:
            hits: List of vector hits from database
            query_vector: Original query vector
            
        Returns:
            List of re-ranked hits
        """
        scored_hits = []
        
        for hit in hits:
            # Extract metadata
            metadata = hit.metadata
            importance = metadata.get("importance", 0.5)
            last_accessed = metadata.get("last_accessed_at")
            created_at = metadata.get("created_at")
            
            # Calculate recency boost
            recency_boost = self._calculate_recency_boost(last_accessed, created_at)
            
            # Calculate decay penalty
            decay_penalty = self._calculate_decay_penalty(created_at, metadata.get("decay_weight", 1.0))
            
            # Composite score
            score = (
                self.alpha * hit.score +           # Cosine similarity
                self.beta * recency_boost +        # Recency boost
                self.gamma * importance -          # Importance weight
                self.delta * decay_penalty         # Decay penalty
            )
            
            # Create new hit with updated score
            scored_hit = VectorHit(
                id=hit.id,
                score=max(0.0, min(1.0, score)),  # Clamp to [0, 1]
                metadata={
                    **metadata,
                    "original_score": hit.score,
                    "recency_boost": recency_boost,
                    "decay_penalty": decay_penalty,
                    "composite_score": score,
                },
            )
            
            scored_hits.append(scored_hit)
        
        # Sort by composite score (descending)
        scored_hits.sort(key=lambda x: x.score, reverse=True)
        
        logger.debug(f"Re-ranked {len(scored_hits)} hits")
        return scored_hits

    def _calculate_recency_boost(
        self,
        last_accessed: Optional[str],
        created_at: Optional[str],
    ) -> float:
        """Calculate recency boost factor.
        
        Args:
            last_accessed: Last accessed timestamp (ISO string)
            created_at: Creation timestamp (ISO string)
            
        Returns:
            Recency boost factor (0.0 to 1.0)
        """
        try:
            # Use last_accessed if available, otherwise use created_at
            timestamp_str = last_accessed or created_at
            if not timestamp_str:
                return 0.0
            
            # Parse timestamp
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timestamp_str
            
            # Calculate days since last access
            now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
            days_since = (now - timestamp).total_seconds() / (24 * 3600)
            
            # Exponential decay: exp(-days / tau)
            boost = math.exp(-days_since / self.tau_days)
            
            return max(0.0, min(1.0, boost))
            
        except Exception as e:
            logger.debug(f"Failed to calculate recency boost: {e}")
            return 0.0

    def _calculate_decay_penalty(
        self,
        created_at: Optional[str],
        decay_weight: float,
    ) -> float:
        """Calculate decay penalty factor.
        
        Args:
            created_at: Creation timestamp (ISO string)
            decay_weight: Decay weight from metadata
            
        Returns:
            Decay penalty factor (0.0 to 1.0)
        """
        try:
            if not created_at:
                return 0.0
            
            # Parse timestamp
            if isinstance(created_at, str):
                timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                timestamp = created_at
            
            # Calculate age in days
            now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
            age_days = (now - timestamp).total_seconds() / (24 * 3600)
            
            # Linear decay with weight factor
            # Penalty increases with age but is modulated by decay_weight
            penalty = (age_days / 365.0) * (1.0 - decay_weight)  # Normalize to year
            
            return max(0.0, min(1.0, penalty))
            
        except Exception as e:
            logger.debug(f"Failed to calculate decay penalty: {e}")
            return 0.0

    def find_similar_memories(
        self,
        memory_vector: List[float],
        tenant_id: str,
        user_id: str,
        similarity_threshold: Optional[float] = None,
        exclude_id: Optional[str] = None,
    ) -> List[VectorHit]:
        """Find memories similar to a given memory.
        
        Args:
            memory_vector: Memory embedding vector
            tenant_id: Tenant identifier
            user_id: User identifier
            similarity_threshold: Minimum similarity threshold
            exclude_id: Memory ID to exclude from results
            
        Returns:
            List of similar memories
        """
        threshold = similarity_threshold or settings.similarity_threshold
        namespace = f"{tenant_id}:{user_id}"
        
        try:
            # Query vector database
            results = self.vector_index.query(
                vectors=[memory_vector],
                top_k=50,  # Get more results for filtering
                namespace=namespace,
            )
            
            if not results or not results[0]:
                return []
            
            hits = results[0]
            
            # Filter by similarity threshold and exclude ID
            similar_hits = []
            for hit in hits:
                if hit.score >= threshold:
                    if exclude_id and hit.id == exclude_id:
                        continue
                    similar_hits.append(hit)
            
            logger.debug(f"Found {len(similar_hits)} similar memories above threshold {threshold}")
            return similar_hits
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise ValueError(f"Similarity search failed: {e}")

    def get_retrieval_stats(self) -> Dict[str, any]:
        """Get retrieval engine statistics.
        
        Returns:
            Dictionary with retrieval configuration and stats
        """
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "delta": self.delta,
            "tau_days": self.tau_days,
            "default_top_k": settings.default_top_k,
            "default_max_memories": settings.default_max_memories,
            "similarity_threshold": settings.similarity_threshold,
            "vector_provider": self.vector_index.provider_name if self.vector_index else "none",
        }
    
    def retrieve(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        top_k: int = 10,
        modalities: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Hybrid retrieval across multiple modalities.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            query: Text query
            top_k: Number of results to return
            modalities: Optional list of modalities to search
            
        Returns:
            List of retrieved memories with metadata
        """
        try:
            from engram.providers.multimodal_registry import embeddings_registry
            
            # Generate query embedding for text search
            query_embedding = embeddings_registry.embed_texts([query], "text")[0]
            
            # Get memory store instance
            from engram.core.memory_store import MemoryStore
            memory_store = MemoryStore()
            
            # Retrieve from memory store with modality filtering
            filter_dict = {}
            if modalities:
                filter_dict["modality"] = {"$in": modalities}
            
            # Get memories from database
            memories = memory_store.get_memories(
                tenant_id=tenant_id,
                user_id=user_id,
                limit=top_k * 3,  # Get more for re-ranking
                filter_dict=filter_dict
            )
            
            if not memories:
                return []
            
            # Prepare for vector search
            memory_items = []
            for memory in memories:
                # Get embedding for this memory
                # In a real implementation, you'd store embeddings during ingestion
                # For now, we'll generate them on-the-fly (not ideal for performance)
                text_embedding = embeddings_registry.embed_texts([memory.text], memory.modality.value)[0]
                
                memory_items.append({
                    "memory": memory,
                    "embedding": text_embedding,
                })
            
            # Calculate similarities
            similarities = []
            for item in memory_items:
                similarity = self._cosine_similarity(query_embedding, item["embedding"])
                similarities.append({
                    "memory": item["memory"],
                    "similarity": similarity,
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Format results
            results = []
            for sim in similarities[:top_k]:
                memory = sim["memory"]
                results.append({
                    "memory_id": memory.id,
                    "text": memory.text,
                    "score": sim["similarity"],
                    "metadata": {
                        "modality": memory.modality.value,
                        "source_uri": memory.source_uri,
                        "chunk_idx": memory.chunk_idx,
                        "importance": memory.importance,
                    },
                    "importance": memory.importance,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None,
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        try:
            import numpy as np
            
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
