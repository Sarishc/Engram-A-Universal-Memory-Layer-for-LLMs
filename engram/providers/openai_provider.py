"""OpenAI provider for embeddings and LLM completions."""

from typing import Any, Dict, List, Optional

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from engram.providers.base_provider import EmbeddingsProvider, LLMProvider, EmbeddingsError, LLMError
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OpenAIEmbeddingsProvider(EmbeddingsProvider):
    """OpenAI embeddings provider."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "text-embedding-3-small"):
        """Initialize OpenAI embeddings provider.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model_name: OpenAI embeddings model name
        """
        self.api_key = api_key or settings.openai_api_key
        self.model_name = model_name
        
        if not self.api_key:
            raise EmbeddingsError(
                "OpenAI API key not provided",
                provider_name=self.provider_name,
            )
        
        self.client = openai.OpenAI(api_key=self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
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

            logger.debug(f"Generating OpenAI embeddings for {len(truncated_texts)} texts")
            
            response = self.client.embeddings.create(
                model=self.model_name,
                input=truncated_texts,
            )

            embeddings = [data.embedding for data in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0]) if embeddings else 0}")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate OpenAI embeddings: {e}")
            raise EmbeddingsError(
                f"Failed to generate OpenAI embeddings: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider.
        
        Returns:
            Embedding dimension as integer
        """
        # OpenAI text-embedding-3-small has 1536 dimensions
        if self.model_name == "text-embedding-3-small":
            return 1536
        elif self.model_name == "text-embedding-ada-002":
            return 1536
        else:
            # For unknown models, try to get dimension from a dummy request
            try:
                dummy_embedding = self.embed_texts(["dummy"])
                return len(dummy_embedding[0]) if dummy_embedding else 1536
            except Exception:
                return 1536  # Fallback

    @property
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "openai_embeddings"


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        max_tokens: int = 2048,
    ):
        """Initialize OpenAI LLM provider.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model_name: OpenAI model name
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or settings.openai_api_key
        self.model_name = model_name
        self._max_tokens = max_tokens
        
        if not self.api_key:
            raise LLMError(
                "OpenAI API key not provided",
                provider_name=self.provider_name,
            )
        
        self.client = openai.OpenAI(api_key=self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def complete(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text completion using OpenAI.
        
        Args:
            prompt: Input prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional OpenAI parameters
            
        Returns:
            Generated text completion
            
        Raises:
            LLMError: If completion generation fails
        """
        try:
            # Use provided max_tokens or default
            tokens_to_use = max_tokens or self._max_tokens
            
            # Use provided temperature or default
            temp_to_use = temperature if temperature is not None else 0.7

            logger.debug(f"Generating OpenAI completion with model: {self.model_name}")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=tokens_to_use,
                temperature=temp_to_use,
                **kwargs,
            )

            completion = response.choices[0].message.content or ""
            logger.debug(f"Generated completion with {len(completion)} characters")
            return completion

        except Exception as e:
            logger.error(f"Failed to generate OpenAI completion: {e}")
            raise LLMError(
                f"Failed to generate OpenAI completion: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

    @property
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "openai_llm"

    @property
    def max_tokens(self) -> int:
        """Get the maximum tokens supported by this provider.
        
        Returns:
            Maximum tokens as integer
        """
        return self._max_tokens

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the OpenAI model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "supports_streaming": True,
        }


# Convenience function to create OpenAI providers
def create_openai_providers(
    api_key: Optional[str] = None,
    embeddings_model: str = "text-embedding-3-small",
    llm_model: str = "gpt-3.5-turbo",
    llm_max_tokens: int = 2048,
) -> tuple[OpenAIEmbeddingsProvider, OpenAILLMProvider]:
    """Create OpenAI embeddings and LLM providers.
    
    Args:
        api_key: OpenAI API key
        embeddings_model: Embeddings model name
        llm_model: LLM model name
        llm_max_tokens: Maximum tokens for LLM
        
    Returns:
        Tuple of (embeddings_provider, llm_provider)
    """
    embeddings_provider = OpenAIEmbeddingsProvider(
        api_key=api_key,
        model_name=embeddings_model,
    )
    
    llm_provider = OpenAILLMProvider(
        api_key=api_key,
        model_name=llm_model,
        max_tokens=llm_max_tokens,
    )
    
    return embeddings_provider, llm_provider
