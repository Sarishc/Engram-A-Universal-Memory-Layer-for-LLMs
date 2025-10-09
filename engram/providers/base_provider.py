"""Base provider interfaces for embeddings and LLM services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from engram.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingsProvider(ABC):
    """Abstract base class for embeddings providers."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (list of floats)
            
        Raises:
            EmbeddingsError: If embedding generation fails
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider.
        
        Returns:
            Embedding dimension as integer
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        pass


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text completion using the LLM.
        
        Args:
            prompt: Input prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text completion
            
        Raises:
            LLMError: If completion generation fails
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        pass

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Get the maximum tokens supported by this provider.
        
        Returns:
            Maximum tokens as integer
        """
        pass


class ProviderError(Exception):
    """Base exception for provider-related errors."""

    def __init__(self, message: str, provider_name: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.provider_name = provider_name
        self.original_error = original_error


class EmbeddingsError(ProviderError):
    """Exception raised when embeddings generation fails."""

    pass


class LLMError(ProviderError):
    """Exception raised when LLM completion fails."""

    pass


class ProviderFactory:
    """Factory class for creating provider instances."""

    _embeddings_providers: Dict[str, type] = {}
    _llm_providers: Dict[str, type] = {}

    @classmethod
    def register_embeddings_provider(cls, name: str, provider_class: type) -> None:
        """Register an embeddings provider.
        
        Args:
            name: Provider name
            provider_class: Provider class implementing EmbeddingsProvider
        """
        cls._embeddings_providers[name] = provider_class
        logger.info(f"Registered embeddings provider: {name}")

    @classmethod
    def register_llm_provider(cls, name: str, provider_class: type) -> None:
        """Register an LLM provider.
        
        Args:
            name: Provider name
            provider_class: Provider class implementing LLMProvider
        """
        cls._llm_providers[name] = provider_class
        logger.info(f"Registered LLM provider: {name}")

    @classmethod
    def create_embeddings_provider(
        cls, name: str, **kwargs: Any
    ) -> EmbeddingsProvider:
        """Create an embeddings provider instance.
        
        Args:
            name: Provider name
            **kwargs: Provider-specific configuration
            
        Returns:
            EmbeddingsProvider instance
            
        Raises:
            ValueError: If provider is not registered
        """
        if name not in cls._embeddings_providers:
            raise ValueError(f"Unknown embeddings provider: {name}")
        
        provider_class = cls._embeddings_providers[name]
        return provider_class(**kwargs)

    @classmethod
    def create_llm_provider(cls, name: str, **kwargs: Any) -> LLMProvider:
        """Create an LLM provider instance.
        
        Args:
            name: Provider name
            **kwargs: Provider-specific configuration
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider is not registered
        """
        if name not in cls._llm_providers:
            raise ValueError(f"Unknown LLM provider: {name}")
        
        provider_class = cls._llm_providers[name]
        return provider_class(**kwargs)

    @classmethod
    def list_embeddings_providers(cls) -> List[str]:
        """List available embeddings providers.
        
        Returns:
            List of provider names
        """
        return list(cls._embeddings_providers.keys())

    @classmethod
    def list_llm_providers(cls) -> List[str]:
        """List available LLM providers.
        
        Returns:
            List of provider names
        """
        return list(cls._llm_providers.keys())
