"""Main ingestion pipeline orchestrator."""

import os
import hashlib
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from engram.utils.logger import get_logger
from engram.utils.config import get_settings
from engram.utils.ids import generate_ulid
from engram.database.models import ModalityType
from engram.providers.multimodal_registry import embeddings_registry
from engram.core.memory_store import MemoryStore
from engram.ingest.pdf import PDFExtractor
from engram.ingest.web import WebExtractor
from engram.ingest.image import ImageExtractor
from engram.ingest.video import VideoExtractor
from engram.ingest.chat import ChatExtractor

logger = get_logger(__name__)
settings = get_settings()


class IngestionStatus(Enum):
    """Status of ingestion operation."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class IngestionResult:
    """Result of an ingestion operation."""
    status: IngestionStatus
    memory_ids: List[str]
    chunks_created: int
    errors: List[str]
    metadata: Dict[str, Any]


class IngestionPipeline:
    """Main ingestion pipeline for multimodal content."""
    
    def __init__(self, memory_store: Optional[MemoryStore] = None):
        """Initialize the ingestion pipeline.
        
        Args:
            memory_store: Optional memory store instance
        """
        self.memory_store = memory_store or MemoryStore()
        self.extractors = {
            ModalityType.PDF: PDFExtractor(),
            ModalityType.WEB: WebExtractor(),
            ModalityType.IMAGE: ImageExtractor(),
            ModalityType.VIDEO: VideoExtractor(),
            ModalityType.CHAT: ChatExtractor(),
        }
        
        # Create blob storage directory
        os.makedirs(settings.blob_store_dir, exist_ok=True)
    
    def ingest_item(
        self,
        tenant_id: str,
        user_id: str,
        content: Union[str, bytes],
        modality: ModalityType,
        source_uri: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 76,
    ) -> IngestionResult:
        """Ingest a single item of content.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            content: Content to ingest (URL, file path, or bytes)
            modality: Content modality type
            source_uri: Optional source URI
            metadata: Optional metadata
            chunk_size: Text chunk size in tokens
            chunk_overlap: Text chunk overlap in tokens
            
        Returns:
            IngestionResult with status and details
        """
        memory_ids = []
        errors = []
        
        try:
            logger.info(f"Starting ingestion for {modality.value} content")
            
            # Extract content using appropriate extractor
            if modality in self.extractors:
                extractor = self.extractors[modality]
                chunks = extractor.extract(
                    content=content,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    source_uri=source_uri
                )
            else:
                # For text modality, treat content as raw text
                chunks = [{"text": str(content), "metadata": {}}]
            
            if not chunks:
                errors.append("No content extracted")
                return IngestionResult(
                    status=IngestionStatus.FAILED,
                    memory_ids=[],
                    chunks_created=0,
                    errors=errors,
                    metadata={}
                )
            
            # Generate embeddings and upsert memories
            texts = [chunk["text"] for chunk in chunks]
            
            # Get embeddings based on modality
            if modality in [ModalityType.IMAGE]:
                # For images, we need to handle differently
                embeddings = self._get_image_embeddings(chunks, source_uri)
            else:
                # For text-based content
                embeddings = embeddings_registry.embed_texts(texts, modality.value)
            
            # Prepare memory items
            memory_items = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_metadata = chunk.get("metadata", {})
                if metadata:
                    chunk_metadata.update(metadata)
                
                # Add chunk-specific metadata
                chunk_metadata.update({
                    "chunk_idx": i,
                    "chunk_size": len(chunk["text"]),
                    "embedding_dim": len(embedding),
                    "embedding_provider": embeddings_registry.get_provider(modality.value).provider_name,
                })
                
                # Generate memory ID
                memory_id = generate_ulid()
                
                memory_items.append((
                    memory_id,
                    embedding,
                    {
                        **chunk_metadata,
                        "modality": modality.value,
                        "source_uri": source_uri,
                        "chunk_idx": i,
                        "mime": self._get_mime_type(modality, source_uri),
                        "caption_or_transcript": chunk.get("caption") or chunk.get("transcript"),
                    }
                ))
                
                memory_ids.append(memory_id)
            
            # Upsert to memory store
            self.memory_store.upsert_memories(
                tenant_id=tenant_id,
                user_id=user_id,
                texts=[chunk["text"] for chunk in chunks],
                embeddings=embeddings,
                metadata_list=[item[2] for item in memory_items],
                importance=0.5,  # Default importance
            )
            
            logger.info(f"Successfully ingested {len(chunks)} chunks for {modality.value}")
            
            return IngestionResult(
                status=IngestionStatus.SUCCESS,
                memory_ids=memory_ids,
                chunks_created=len(chunks),
                errors=[],
                metadata={
                    "modality": modality.value,
                    "source_uri": source_uri,
                    "chunk_size": chunk_size,
                    "embedding_dim": len(embeddings[0]) if embeddings else 0,
                }
            )
            
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")
            errors.append(str(e))
            
            return IngestionResult(
                status=IngestionStatus.FAILED,
                memory_ids=memory_ids,
                chunks_created=len(memory_ids),
                errors=errors,
                metadata={"modality": modality.value, "source_uri": source_uri}
            )
    
    def _get_image_embeddings(self, chunks: List[Dict[str, Any]], source_uri: Optional[str]) -> List[List[float]]:
        """Get embeddings for image chunks.
        
        Args:
            chunks: List of image chunks
            source_uri: Source URI for images
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for chunk in chunks:
            try:
                # If chunk has image_path, use it
                if "image_path" in chunk:
                    image_embeddings = embeddings_registry.embed_images([chunk["image_path"]])
                    embeddings.extend(image_embeddings)
                else:
                    # Fallback to text embedding if no image available
                    text_embeddings = embeddings_registry.embed_texts([chunk["text"]], "image")
                    embeddings.extend(text_embeddings)
            except Exception as e:
                logger.warning(f"Error getting image embedding: {e}")
                # Fallback to text embedding
                text_embeddings = embeddings_registry.embed_texts([chunk["text"]], "image")
                embeddings.extend(text_embeddings)
        
        return embeddings
    
    def _get_mime_type(self, modality: ModalityType, source_uri: Optional[str]) -> Optional[str]:
        """Get MIME type for the content.
        
        Args:
            modality: Content modality
            source_uri: Source URI
            
        Returns:
            MIME type string
        """
        if not source_uri:
            return None
        
        # Map modality to MIME type
        mime_map = {
            ModalityType.PDF: "application/pdf",
            ModalityType.IMAGE: "image/jpeg",  # Default for images
            ModalityType.VIDEO: "video/mp4",  # Default for videos
            ModalityType.WEB: "text/html",
            ModalityType.CHAT: "application/json",
        }
        
        # Try to get MIME type from file extension
        if source_uri.startswith("http"):
            # For URLs, try to infer from path
            if ".pdf" in source_uri.lower():
                return "application/pdf"
            elif any(ext in source_uri.lower() for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                return "image/jpeg"
            elif any(ext in source_uri.lower() for ext in [".mp4", ".avi", ".mov"]):
                return "video/mp4"
        
        return mime_map.get(modality)


# Global pipeline instance
_pipeline_instance: Optional[IngestionPipeline] = None


def ingest_item(
    tenant_id: str,
    user_id: str,
    content: Union[str, bytes],
    modality: ModalityType,
    source_uri: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 512,
    chunk_overlap: int = 76,
) -> IngestionResult:
    """Convenience function to ingest an item.
    
    Args:
        tenant_id: Tenant identifier
        user_id: User identifier
        content: Content to ingest
        modality: Content modality type
        source_uri: Optional source URI
        metadata: Optional metadata
        chunk_size: Text chunk size in tokens
        chunk_overlap: Text chunk overlap in tokens
        
    Returns:
        IngestionResult with status and details
    """
    global _pipeline_instance
    
    if _pipeline_instance is None:
        _pipeline_instance = IngestionPipeline()
    
    return _pipeline_instance.ingest_item(
        tenant_id=tenant_id,
        user_id=user_id,
        content=content,
        modality=modality,
        source_uri=source_uri,
        metadata=metadata,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
