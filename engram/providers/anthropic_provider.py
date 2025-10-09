"""Anthropic provider for LLM completions."""

from typing import Any, Dict, Optional

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from engram.providers.base_provider import LLMProvider, LLMError
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AnthropicLLMProvider(LLMProvider):
    """Anthropic LLM provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "claude-3-sonnet-20240229",
        max_tokens: int = 2048,
    ):
        """Initialize Anthropic LLM provider.
        
        Args:
            api_key: Anthropic API key (uses env var if not provided)
            model_name: Anthropic model name
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.model_name = model_name
        self._max_tokens = max_tokens
        
        if not self.api_key:
            raise LLMError(
                "Anthropic API key not provided",
                provider_name=self.provider_name,
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def complete(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text completion using Anthropic.
        
        Args:
            prompt: Input prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional Anthropic parameters
            
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

            logger.debug(f"Generating Anthropic completion with model: {self.model_name}")
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=tokens_to_use,
                temperature=temp_to_use,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            completion = response.content[0].text if response.content else ""
            logger.debug(f"Generated completion with {len(completion)} characters")
            return completion

        except Exception as e:
            logger.error(f"Failed to generate Anthropic completion: {e}")
            raise LLMError(
                f"Failed to generate Anthropic completion: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

    @property
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "anthropic_llm"

    @property
    def max_tokens(self) -> int:
        """Get the maximum tokens supported by this provider.
        
        Returns:
            Maximum tokens as integer
        """
        return self._max_tokens

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Anthropic model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "supports_streaming": True,
        }

    def get_available_models(self) -> list[str]:
        """Get list of available Anthropic models.
        
        Returns:
            List of model names
        """
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]


# Convenience function to create Anthropic provider
def create_anthropic_provider(
    api_key: Optional[str] = None,
    model_name: str = "claude-3-sonnet-20240229",
    max_tokens: int = 2048,
) -> AnthropicLLMProvider:
    """Create Anthropic LLM provider.
    
    Args:
        api_key: Anthropic API key
        model_name: Model name
        max_tokens: Maximum tokens to generate
        
    Returns:
        AnthropicLLMProvider instance
    """
    return AnthropicLLMProvider(
        api_key=api_key,
        model_name=model_name,
        max_tokens=max_tokens,
    )
