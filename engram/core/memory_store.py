"""Memory store for CRUD operations and orchestration."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from engram.core.embeddings import EmbeddingsFacade
from engram.core.retrieval import RetrievalEngine
from engram.core.consolidation import ConsolidationEngine
from engram.database.models import Memory, Tenant, UserMemoryStats
from engram.utils.config import get_settings
from engram.utils.ids import generate_memory_id, generate_tenant_id
from engram.utils.logger import get_logger
from engram.vectordb.base import VectorIndex

logger = get_logger(__name__)
settings = get_settings()


class MemoryStore:
    """Main memory store for CRUD operations and orchestration."""

    def __init__(
        self,
        db_session: Optional[Session] = None,
        vector_index: Optional[VectorIndex] = None,
        embeddings_facade: Optional[EmbeddingsFacade] = None,
    ):
        """Initialize memory store.
        
        Args:
            db_session: Database session (optional, creates default if None)
            vector_index: Vector database interface (optional)
            embeddings_facade: Embeddings facade (optional, creates default if None)
        """
        self.db = db_session
        self.vector_index = vector_index
        self.embeddings_facade = embeddings_facade or EmbeddingsFacade()
        
        # Initialize engines
        self.retrieval_engine = RetrievalEngine(vector_index)
        self.consolidation_engine = ConsolidationEngine(self.retrieval_engine)

    def create_tenant(self, name: str) -> Tenant:
        """Create a new tenant.
        
        Args:
            name: Tenant name
            
        Returns:
            Created tenant
            
        Raises:
            ValueError: If tenant creation fails
        """
        try:
            # Check if tenant already exists
            existing = self.db.query(Tenant).filter(Tenant.name == name).first()
            if existing:
                raise ValueError(f"Tenant with name '{name}' already exists")
            
            # Create new tenant
            tenant = Tenant(
                id=generate_tenant_id(),
                name=name,
            )
            
            self.db.add(tenant)
            self.db.commit()
            self.db.refresh(tenant)
            
            logger.info(f"Created tenant: {tenant.id} ({tenant.name})")
            return tenant
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create tenant: {e}")
            raise ValueError(f"Tenant creation failed: {e}")

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant if found, None otherwise
        """
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()

    def upsert_memories(
        self,
        tenant_id: str,
        user_id: str,
        texts: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        importance: float = 0.5,
        modality: str = "text",
        source_uri: Optional[str] = None,
        chunk_indices: Optional[List[int]] = None,
        mime_types: Optional[List[str]] = None,
        captions: Optional[List[str]] = None,
    ) -> List[Memory]:
        """Upsert memories for a user.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            texts: List of memory texts
            embeddings: Optional list of embeddings
            metadata_list: List of metadata dictionaries
            importance: Importance score (default 0.5)
            modality: Content modality (default "text")
            source_uri: Optional source URI
            chunk_indices: Optional list of chunk indices
            mime_types: Optional list of MIME types
            captions: Optional list of captions/transcripts
            
        Returns:
            List of created/updated memories
            
        Raises:
            ValueError: If memory upsert fails
        """
        if not texts:
            return []
        
        try:
            # Validate tenant exists
            tenant = self.get_tenant(tenant_id)
            if not tenant:
                raise ValueError(f"Tenant {tenant_id} not found")
            
            # Prepare lists
            metadata_list = metadata_list or [{}] * len(texts)
            chunk_indices = chunk_indices or [i for i in range(len(texts))]
            mime_types = mime_types or [None] * len(texts)
            captions = captions or [None] * len(texts)
            
            # Ensure lists have same length
            while len(metadata_list) < len(texts):
                metadata_list.append({})
            while len(chunk_indices) < len(texts):
                chunk_indices.append(len(chunk_indices))
            while len(mime_types) < len(texts):
                mime_types.append(None)
            while len(captions) < len(texts):
                captions.append(None)
            
            # Truncate texts if needed
            truncated_texts = []
            original_texts = []
            for text in texts:
                if len(text) > settings.max_text_length:
                    truncated_texts.append(text[:settings.max_text_length])
                    original_texts.append(text)
                else:
                    truncated_texts.append(text)
                    original_texts.append(None)
            
            # Generate embeddings if not provided
            if embeddings is None:
                logger.debug(f"Generating embeddings for {len(truncated_texts)} texts")
                embeddings = self.embeddings_facade.embed_texts(truncated_texts)
            
            if len(embeddings) != len(texts):
                raise ValueError(f"Expected {len(texts)} embeddings, got {len(embeddings)}")
            
            # Create memory records
            memories = []
            vector_items = []
            
            for i, (text, embedding, metadata, chunk_idx, mime, caption) in enumerate(
                zip(truncated_texts, embeddings, metadata_list, chunk_indices, mime_types, captions)
            ):
                memory_id = generate_memory_id()
                
                # Prepare metadata
                memory_metadata = {
                    **metadata,
                    "importance": importance,
                    "created_at": datetime.now().isoformat(),
                    "last_accessed_at": datetime.now().isoformat(),
                }
                
                # Store original text if truncated
                if original_texts[i]:
                    memory_metadata["original"] = original_texts[i]
                
                # Import ModalityType
                from engram.database.models import ModalityType
                
                # Create memory record
                memory = Memory(
                    id=memory_id,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    text=text,
                    memory_metadata=memory_metadata,
                    importance=importance,
                    modality=ModalityType(modality),
                    source_uri=source_uri,
                    chunk_idx=chunk_idx,
                    mime=mime,
                    caption_or_transcript=caption,
                )
                
                memories.append(memory)
                
                # Prepare vector item
                vector_items.append((memory_id, embedding, memory_metadata))
            
            # Save to database
            self.db.add_all(memories)
            self.db.commit()
            
            # Save to vector database
            namespace = f"{tenant_id}:{user_id}"
            self.vector_index.upsert(vector_items, namespace)
            
            # Update user stats
            self._update_user_stats(tenant_id, user_id)
            
            logger.info(f"Upserted {len(memories)} memories for tenant={tenant_id}, user={user_id}")
            return memories
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to upsert memories: {e}")
            raise ValueError(f"Memory upsert failed: {e}")

    def retrieve_memories(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for a query.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of memory dictionaries with scores
            
        Raises:
            ValueError: If retrieval fails
        """
        try:
            # Generate query embedding
            query_embeddings = self.embeddings_facade.embed_texts([query])
            if not query_embeddings:
                return []
            
            query_vector = query_embeddings[0]
            
            # Retrieve memories
            hits = self.retrieval_engine.retrieve_memories(
                query_vector=query_vector,
                tenant_id=tenant_id,
                user_id=user_id,
                top_k=top_k,
            )
            
            # Get full memory records from database
            if not hits:
                return []
            
            memory_ids = [hit.id for hit in hits]
            memories = self.db.query(Memory).filter(
                and_(
                    Memory.id.in_(memory_ids),
                    Memory.tenant_id == tenant_id,
                    Memory.user_id == user_id,
                    Memory.active == True,
                )
            ).all()
            
            # Create memory ID to record mapping
            memory_map = {memory.id: memory for memory in memories}
            
            # Combine hits with memory records
            results = []
            for hit in hits:
                if hit.id in memory_map:
                    memory = memory_map[hit.id]
                    
                    # Update last accessed time
                    memory.last_accessed_at = datetime.now()
                    
                    result = {
                        "memory_id": memory.id,
                        "text": memory.text,
                        "score": hit.score,
                        "metadata": memory.memory_metadata,
                        "importance": memory.importance,
                        "created_at": memory.created_at.isoformat(),
                        "last_accessed_at": memory.last_accessed_at.isoformat(),
                    }
                    results.append(result)
            
            # Commit last accessed time updates
            self.db.commit()
            
            logger.debug(f"Retrieved {len(results)} memories for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            raise ValueError(f"Memory retrieval failed: {e}")

    def delete_memory(self, memory_id: str, tenant_id: str, user_id: str) -> bool:
        """Delete a memory (soft delete).
        
        Args:
            memory_id: Memory identifier
            tenant_id: Tenant identifier
            user_id: User identifier
            
        Returns:
            True if memory was deleted, False if not found
        """
        try:
            # Find memory
            memory = self.db.query(Memory).filter(
                and_(
                    Memory.id == memory_id,
                    Memory.tenant_id == tenant_id,
                    Memory.user_id == user_id,
                    Memory.active == True,
                )
            ).first()
            
            if not memory:
                return False
            
            # Soft delete
            memory.active = False
            self.db.commit()
            
            # Remove from vector database
            namespace = f"{tenant_id}:{user_id}"
            self.vector_index.delete([memory_id], namespace)
            
            # Update user stats
            self._update_user_stats(tenant_id, user_id)
            
            logger.info(f"Deleted memory {memory_id} for tenant={tenant_id}, user={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete memory: {e}")
            raise ValueError(f"Memory deletion failed: {e}")

    def list_memories(
        self,
        tenant_id: str,
        user_id: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Memory]:
        """List memories with pagination.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier (optional, lists all users if None)
            active_only: Only return active memories
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of memory records
        """
        query = self.db.query(Memory).filter(Memory.tenant_id == tenant_id)
        
        if user_id:
            query = query.filter(Memory.user_id == user_id)
        
        if active_only:
            query = query.filter(Memory.active == True)
        
        return query.order_by(desc(Memory.created_at)).offset(offset).limit(limit).all()

    def _update_user_stats(self, tenant_id: str, user_id: str) -> None:
        """Update user memory statistics.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
        """
        try:
            # Get current stats
            stats = self.db.query(UserMemoryStats).filter(
                and_(
                    UserMemoryStats.tenant_id == tenant_id,
                    UserMemoryStats.user_id == user_id,
                )
            ).first()
            
            # Calculate new stats
            total_memories = self.db.query(func.count(Memory.id)).filter(
                and_(
                    Memory.tenant_id == tenant_id,
                    Memory.user_id == user_id,
                )
            ).scalar()
            
            active_memories = self.db.query(func.count(Memory.id)).filter(
                and_(
                    Memory.tenant_id == tenant_id,
                    Memory.user_id == user_id,
                    Memory.active == True,
                )
            ).scalar()
            
            avg_importance = self.db.query(func.avg(Memory.importance)).filter(
                and_(
                    Memory.tenant_id == tenant_id,
                    Memory.user_id == user_id,
                    Memory.active == True,
                )
            ).scalar() or 0.0
            
            if stats:
                # Update existing stats
                stats.total_memories = total_memories
                stats.active_memories = active_memories
                stats.avg_importance = float(avg_importance)
                stats.last_seen_at = datetime.now()
            else:
                # Create new stats
                stats = UserMemoryStats(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    total_memories=total_memories,
                    active_memories=active_memories,
                    avg_importance=float(avg_importance),
                    last_seen_at=datetime.now(),
                )
                self.db.add(stats)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")
            # Don't raise - this is not critical

    def get_user_stats(self, tenant_id: str, user_id: str) -> Optional[UserMemoryStats]:
        """Get user memory statistics.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            
        Returns:
            User memory stats if found, None otherwise
        """
        return self.db.query(UserMemoryStats).filter(
            and_(
                UserMemoryStats.tenant_id == tenant_id,
                UserMemoryStats.user_id == user_id,
            )
        ).first()

    def get_memories(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 100,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Memory]:
        """Get memories for a user with optional filtering.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            limit: Maximum number of memories to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of memories
        """
        try:
            from engram.database.postgres import get_db_session
            
            with get_db_session() as session:
                query = session.query(Memory).filter(
                    Memory.tenant_id == tenant_id,
                    Memory.user_id == user_id,
                    Memory.active == True
                )
                
                # Apply modality filter if provided
                if filter_dict and "modality" in filter_dict:
                    modalities = filter_dict["modality"]
                    if isinstance(modalities, dict) and "$in" in modalities:
                        modality_values = modalities["$in"]
                        query = query.filter(Memory.modality.in_(modality_values))
                
                memories = query.order_by(desc(Memory.created_at)).limit(limit).all()
                return memories
                
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return []

    def get_store_stats(self) -> Dict[str, Any]:
        """Get memory store statistics.
        
        Returns:
            Dictionary with store statistics
        """
        try:
            total_tenants = self.db.query(func.count(Tenant.id)).scalar()
            total_memories = self.db.query(func.count(Memory.id)).scalar()
            active_memories = self.db.query(func.count(Memory.id)).filter(
                Memory.active == True
            ).scalar()
            
            return {
                "total_tenants": total_tenants,
                "total_memories": total_memories,
                "active_memories": active_memories,
                "vector_provider": self.vector_index.provider_name,
                "embeddings_provider": self.embeddings_facade._provider_name,
            }
            
        except Exception as e:
            logger.error(f"Failed to get store stats: {e}")
            return {"error": str(e)}

