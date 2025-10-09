"""Embeddings facade for provider-agnostic embedding generation."""

from typing import Dict, List, Optional

from engram.providers.base_provider import EmbeddingsProvider, ProviderFactory
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingsFacade:
    """Facade for embeddings providers with caching and provider management."""

    def __init__(self):
        """Initialize embeddings facade."""
        self._provider: Optional[EmbeddingsProvider] = None
        self._provider_name = settings.default_embeddings_provider
        
        # Register default providers
        self._register_providers()

    def _register_providers(self) -> None:
        """Register available embeddings providers."""
        try:
            from engram.providers.local_sentence_transformers import LocalSentenceTransformersProvider
            ProviderFactory.register_embeddings_provider("local", LocalSentenceTransformersProvider)
            
            from engram.providers.openai_provider import OpenAIEmbeddingsProvider
            ProviderFactory.register_embeddings_provider("openai", OpenAIEmbeddingsProvider)
            
            from engram.providers.google_provider import GoogleEmbeddingsProvider
            ProviderFactory.register_embeddings_provider("google", GoogleEmbeddingsProvider)
            
            logger.info(f"Registered embeddings providers: {ProviderFactory.list_embeddings_providers()}")
            
        except Exception as e:
            logger.error(f"Failed to register some embeddings providers: {e}")

    def _get_provider(self, provider_name: Optional[str] = None) -> EmbeddingsProvider:
        """Get embeddings provider instance.
        
        Args:
            provider_name: Name of provider to use (defaults to configured provider)
            
        Returns:
            EmbeddingsProvider instance
            
        Raises:
            ValueError: If provider is not available
        """
        provider_name = provider_name or self._provider_name
        
        # Return cached provider if same name
        if self._provider and self._provider.provider_name == provider_name:
            return self._provider
        
        try:
            # Create new provider instance
            if provider_name == "openai" and not settings.openai_api_key:
                logger.warning("OpenAI API key not configured, falling back to local provider")
                provider_name = "local"
            elif provider_name == "google" and not settings.google_application_credentials:
                logger.warning("Google credentials not configured, falling back to local provider")
                provider_name = "local"
            
            self._provider = ProviderFactory.create_embeddings_provider(provider_name)
            self._provider_name = provider_name
            
            logger.info(f"Initialized embeddings provider: {provider_name}")
            return self._provider
            
        except Exception as e:
            logger.error(f"Failed to create embeddings provider {provider_name}: {e}")
            
            # Fallback to local provider
            if provider_name != "local":
                logger.info("Falling back to local embeddings provider")
                try:
                    self._provider = ProviderFactory.create_embeddings_provider("local")
                    self._provider_name = "local"
                    return self._provider
                except Exception as fallback_error:
                    logger.error(f"Failed to create fallback local provider: {fallback_error}")
            
            raise ValueError(f"Could not initialize embeddings provider: {e}")

    def embed_texts(
        self,
        texts: List[str],
        provider_name: Optional[str] = None,
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            provider_name: Name of provider to use
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If embedding generation fails
        """
        if not texts:
            return []

        try:
            provider = self._get_provider(provider_name)
            
            logger.debug(f"Generating embeddings for {len(texts)} texts using {provider.provider_name}")
            
            # Generate embeddings
            embeddings = provider.embed_texts(texts)
            
            # Validate embeddings
            if len(embeddings) != len(texts):
                raise ValueError(f"Expected {len(texts)} embeddings, got {len(embeddings)}")
            
            # Validate embedding dimensions
            if embeddings:
                expected_dim = len(embeddings[0])
                for i, embedding in enumerate(embeddings):
                    if len(embedding) != expected_dim:
                        raise ValueError(f"Embedding {i} has dimension {len(embedding)}, expected {expected_dim}")
            
            logger.debug(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0]) if embeddings else 0}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise ValueError(f"Embedding generation failed: {e}")

    def get_embedding_dimension(self, provider_name: Optional[str] = None) -> int:
        """Get the dimension of embeddings produced by the provider.
        
        Args:
            provider_name: Name of provider to check
            
        Returns:
            Embedding dimension as integer
        """
        provider = self._get_provider(provider_name)
        return provider.get_embedding_dimension()

    def get_provider_info(self, provider_name: Optional[str] = None) -> Dict[str, any]:
        """Get information about the current or specified provider.
        
        Args:
            provider_name: Name of provider to get info for
            
        Returns:
            Dictionary with provider information
        """
        provider = self._get_provider(provider_name)
        
        return {
            "provider_name": provider.provider_name,
            "embedding_dimension": provider.get_embedding_dimension(),
            "available_providers": ProviderFactory.list_embeddings_providers(),
        }

    def list_available_providers(self) -> List[str]:
        """List available embeddings providers.
        
        Returns:
            List of provider names
        """
        return ProviderFactory.list_embeddings_providers()

    def validate_provider(self, provider_name: str) -> bool:
        """Validate if a provider is available and properly configured.
        
        Args:
            provider_name: Name of provider to validate
            
        Returns:
            True if provider is available and configured
        """
        try:
            if provider_name not in ProviderFactory.list_embeddings_providers():
                return False
            
            # Try to create provider instance
            provider = ProviderFactory.create_embeddings_provider(provider_name)
            
            # Test with dummy embedding
            dummy_embeddings = provider.embed_texts(["test"])
            return len(dummy_embeddings) == 1 and len(dummy_embeddings[0]) > 0
            
        except Exception as e:
            logger.debug(f"Provider {provider_name} validation failed: {e}")
            return False
