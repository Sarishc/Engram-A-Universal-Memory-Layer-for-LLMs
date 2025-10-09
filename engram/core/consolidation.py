"""Memory consolidation engine for merging similar memories and managing forgetting."""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from engram.vectordb.base import VectorHit
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ConsolidationEngine:
    """Engine for consolidating similar memories and managing memory lifecycle."""

    def __init__(self, retrieval_engine):
        """Initialize consolidation engine.
        
        Args:
            retrieval_engine: Retrieval engine instance for similarity search
        """
        self.retrieval_engine = retrieval_engine
        self.consolidation_threshold = settings.consolidation_threshold
        self.similarity_threshold = settings.similarity_threshold
        self.importance_threshold = settings.importance_threshold
        self.forgetting_days = settings.forgetting_days
        self.max_text_length = settings.max_text_length

    def consolidate_memories(
        self,
        tenant_id: str,
        user_id: str,
        memory_vectors: Dict[str, List[float]],
        dry_run: bool = False,
    ) -> Dict[str, List[str]]:
        """Consolidate similar memories by merging them.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            memory_vectors: Dict mapping memory_id to embedding vector
            dry_run: If True, only identify consolidation candidates without merging
            
        Returns:
            Dictionary with consolidation results: {
                "merged": [(source_ids, target_id)],
                "deleted": [memory_ids],
                "updated": [memory_ids]
            }
        """
        if not memory_vectors:
            return {"merged": [], "deleted": [], "updated": []}

        try:
            logger.info(f"Starting consolidation for tenant={tenant_id}, user={user_id}, memories={len(memory_vectors)}")
            
            # Find similar memory clusters
            clusters = self._find_memory_clusters(memory_vectors, tenant_id, user_id)
            
            consolidation_results = {
                "merged": [],
                "deleted": [],
                "updated": [],
            }
            
            for cluster in clusters:
                if len(cluster) < 2:
                    continue
                
                # Sort cluster by creation time (oldest first for merging)
                sorted_cluster = self._sort_cluster_by_age(cluster)
                
                if dry_run:
                    logger.info(f"Would merge cluster: {[m['id'] for m in sorted_cluster]}")
                    consolidation_results["merged"].append([m["id"] for m in sorted_cluster])
                else:
                    # Perform actual consolidation
                    merge_result = self._merge_memory_cluster(sorted_cluster, tenant_id, user_id)
                    if merge_result:
                        consolidation_results["merged"].extend(merge_result["merged"])
                        consolidation_results["deleted"].extend(merge_result["deleted"])
                        consolidation_results["updated"].extend(merge_result["updated"])
            
            logger.info(f"Consolidation completed: {len(consolidation_results['merged'])} merged, "
                       f"{len(consolidation_results['deleted'])} deleted")
            
            return consolidation_results
            
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            raise ValueError(f"Memory consolidation failed: {e}")

    def _find_memory_clusters(
        self,
        memory_vectors: Dict[str, List[float]],
        tenant_id: str,
        user_id: str,
    ) -> List[List[Dict]]:
        """Find clusters of similar memories.
        
        Args:
            memory_vectors: Dict mapping memory_id to embedding vector
            tenant_id: Tenant identifier
            user_id: User identifier
            
        Returns:
            List of memory clusters (lists of memory dictionaries)
        """
        clusters = []
        processed_ids: Set[str] = set()
        
        for memory_id, vector in memory_vectors.items():
            if memory_id in processed_ids:
                continue
            
            # Find similar memories
            similar_hits = self.retrieval_engine.find_similar_memories(
                memory_vector=vector,
                tenant_id=tenant_id,
                user_id=user_id,
                similarity_threshold=self.consolidation_threshold,
                exclude_id=memory_id,
            )
            
            if not similar_hits:
                continue
            
            # Create cluster with original memory
            cluster = [{"id": memory_id, "vector": vector}]
            processed_ids.add(memory_id)
            
            # Add similar memories to cluster
            for hit in similar_hits:
                if hit.id in memory_vectors and hit.id not in processed_ids:
                    cluster.append({
                        "id": hit.id,
                        "vector": memory_vectors[hit.id],
                    })
                    processed_ids.add(hit.id)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        logger.debug(f"Found {len(clusters)} memory clusters")
        return clusters

    def _sort_cluster_by_age(self, cluster: List[Dict]) -> List[Dict]:
        """Sort memory cluster by creation time (oldest first).
        
        Args:
            cluster: List of memory dictionaries
            
        Returns:
            Sorted cluster with oldest memories first
        """
        # For now, sort by ID (ULIDs are time-ordered)
        # In a real implementation, you'd fetch creation times from database
        return sorted(cluster, key=lambda x: x["id"])

    def _merge_memory_cluster(
        self,
        cluster: List[Dict],
        tenant_id: str,
        user_id: str,
    ) -> Optional[Dict[str, List[str]]]:
        """Merge a cluster of similar memories.
        
        Args:
            cluster: List of memory dictionaries to merge
            tenant_id: Tenant identifier
            user_id: User identifier
            
        Returns:
            Dictionary with merge results or None if merge failed
        """
        if len(cluster) < 2:
            return None
        
        try:
            # Keep the oldest memory as the target
            target_memory = cluster[0]
            source_memories = cluster[1:]
            
            # Merge metadata and text
            merged_result = self._merge_memory_content(target_memory, source_memories)
            
            if not merged_result:
                return None
            
            return {
                "merged": [[m["id"] for m in cluster]],
                "deleted": [m["id"] for m in source_memories],
                "updated": [target_memory["id"]],
            }
            
        except Exception as e:
            logger.error(f"Failed to merge memory cluster: {e}")
            return None

    def _merge_memory_content(
        self,
        target_memory: Dict,
        source_memories: List[Dict],
    ) -> Optional[Dict]:
        """Merge content from source memories into target memory.
        
        Args:
            target_memory: Target memory dictionary
            source_memories: List of source memory dictionaries
            
        Returns:
            Merged memory content or None if merge failed
        """
        try:
            # In a real implementation, you would:
            # 1. Fetch full memory records from database
            # 2. Merge text content intelligently
            # 3. Merge metadata
            # 4. Recompute embedding
            # 5. Update target memory in database
            # 6. Delete source memories
            
            # For now, return a placeholder
            logger.info(f"Merging {len(source_memories)} memories into {target_memory['id']}")
            
            return {
                "target_id": target_memory["id"],
                "source_ids": [m["id"] for m in source_memories],
                "merged_text": "Merged content placeholder",
                "merged_metadata": {"merge_count": len(source_memories) + 1},
            }
            
        except Exception as e:
            logger.error(f"Failed to merge memory content: {e}")
            return None

    def identify_forgotten_memories(
        self,
        memories: List[Dict],
        current_time: Optional[datetime] = None,
    ) -> List[str]:
        """Identify memories that should be forgotten based on importance and recency.
        
        Args:
            memories: List of memory dictionaries with metadata
            current_time: Current time for calculations (defaults to now)
            
        Returns:
            List of memory IDs to forget
        """
        if not memories:
            return []
        
        current_time = current_time or datetime.now()
        forgotten_ids = []
        
        try:
            for memory in memories:
                memory_id = memory.get("id")
                metadata = memory.get("metadata", {})
                
                if not memory_id:
                    continue
                
                # Check importance threshold
                importance = metadata.get("importance", 0.5)
                if importance < self.importance_threshold:
                    # Check last accessed time
                    last_accessed = metadata.get("last_accessed_at")
                    if last_accessed:
                        try:
                            if isinstance(last_accessed, str):
                                last_accessed_dt = datetime.fromisoformat(
                                    last_accessed.replace('Z', '+00:00')
                                )
                            else:
                                last_accessed_dt = last_accessed
                            
                            days_since_access = (current_time - last_accessed_dt).days
                            
                            if days_since_access > self.forgetting_days:
                                forgotten_ids.append(memory_id)
                                logger.debug(f"Memory {memory_id} marked for forgetting: "
                                           f"importance={importance}, days_since={days_since_access}")
                        
                        except Exception as e:
                            logger.debug(f"Failed to parse last_accessed for memory {memory_id}: {e}")
            
            logger.info(f"Identified {len(forgotten_ids)} memories for forgetting")
            return forgotten_ids
            
        except Exception as e:
            logger.error(f"Failed to identify forgotten memories: {e}")
            return []

    def calculate_memory_importance(
        self,
        memory: Dict,
        access_frequency: int = 0,
        recency_days: int = 0,
    ) -> float:
        """Calculate importance score for a memory.
        
        Args:
            memory: Memory dictionary with metadata
            access_frequency: Number of times memory was accessed
            recency_days: Days since last access
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        try:
            metadata = memory.get("metadata", {})
            current_importance = metadata.get("importance", 0.5)
            
            # Base importance from metadata
            base_importance = current_importance
            
            # Boost based on access frequency (logarithmic)
            frequency_boost = min(0.3, math.log(1 + access_frequency) * 0.1)
            
            # Boost based on recency (exponential decay)
            recency_boost = math.exp(-recency_days / 30.0) * 0.2
            
            # Combine factors
            new_importance = min(1.0, base_importance + frequency_boost + recency_boost)
            
            return max(0.0, new_importance)
            
        except Exception as e:
            logger.error(f"Failed to calculate memory importance: {e}")
            return 0.5  # Default importance

    def get_consolidation_stats(self) -> Dict[str, any]:
        """Get consolidation engine statistics.
        
        Returns:
            Dictionary with consolidation configuration and stats
        """
        return {
            "consolidation_threshold": self.consolidation_threshold,
            "similarity_threshold": self.similarity_threshold,
            "importance_threshold": self.importance_threshold,
            "forgetting_days": self.forgetting_days,
            "max_text_length": self.max_text_length,
            "consolidation_enabled": settings.consolidation_enabled,
            "forgetting_enabled": settings.forgetting_enabled,
        }
