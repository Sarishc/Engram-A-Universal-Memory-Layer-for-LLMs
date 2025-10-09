"""Local sentence transformers embeddings provider."""

from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from engram.providers.base_provider import EmbeddingsProvider, EmbeddingsError
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LocalSentenceTransformersProvider(EmbeddingsProvider):
    """Local embeddings provider using sentence-transformers."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the sentence transformers provider.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._embedding_dimension: Optional[int] = None

    @property
    def model(self) -> SentenceTransformer:
        """Get the sentence transformer model (lazy loading).
        
        Returns:
            Loaded SentenceTransformer model
        """
        if self._model is None:
            try:
                logger.info(f"Loading sentence-transformers model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Successfully loaded model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise EmbeddingsError(
                    f"Failed to load sentence-transformers model: {self.model_name}",
                    provider_name=self.provider_name,
                    original_error=e,
                )
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (list of floats)
            
        Raises:
            EmbeddingsError: If embedding generation fails
        """
        if not texts:
            return []

        try:
            # Clean and filter texts
            clean_texts = [text.strip() for text in texts if text.strip()]
            if not clean_texts:
                logger.warning("No valid texts provided for embedding")
                return []

            # Truncate texts if they exceed max length
            max_length = settings.max_text_length
            truncated_texts = []
            for text in clean_texts:
                if len(text) > max_length:
                    truncated_texts.append(text[:max_length])
                    logger.warning(f"Truncated text from {len(text)} to {max_length} characters")
                else:
                    truncated_texts.append(text)

            logger.debug(f"Generating embeddings for {len(truncated_texts)} texts")
            
            # Generate embeddings
            embeddings = self.model.encode(
                truncated_texts,
                convert_to_tensor=False,
                normalize_embeddings=True,  # Normalize for cosine similarity
                show_progress_bar=False,
            )

            # Convert to list of lists
            result = [embedding.tolist() for embedding in embeddings]
            
            logger.debug(f"Generated {len(result)} embeddings with dimension {len(result[0]) if result else 0}")
            return result

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise EmbeddingsError(
                f"Failed to generate embeddings: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider.
        
        Returns:
            Embedding dimension as integer
        """
        if self._embedding_dimension is None:
            try:
                # Generate a dummy embedding to get dimension
                dummy_embedding = self.embed_texts(["dummy"])
                self._embedding_dimension = len(dummy_embedding[0]) if dummy_embedding else 0
            except Exception as e:
                logger.error(f"Failed to determine embedding dimension: {e}")
                # Fallback to known dimension for all-MiniLM-L6-v2
                self._embedding_dimension = 384
                
        return self._embedding_dimension

    @property
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "local_sentence_transformers"

    def get_model_info(self) -> dict:
        """Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_text_length": settings.max_text_length,
        }
