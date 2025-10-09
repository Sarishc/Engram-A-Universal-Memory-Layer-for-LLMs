"""Google Vertex AI provider for embeddings and LLM completions."""

from typing import Any, Dict, List, Optional

from google.cloud import aiplatform
from google.oauth2 import service_account
from tenacity import retry, stop_after_attempt, wait_exponential

from engram.providers.base_provider import EmbeddingsProvider, LLMProvider, EmbeddingsError, LLMError
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class GoogleEmbeddingsProvider(EmbeddingsProvider):
    """Google Vertex AI embeddings provider."""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model_name: str = "textembedding-gecko",
    ):
        """Initialize Google embeddings provider.
        
        Args:
            credentials_path: Path to Google service account credentials
            project_id: Google Cloud project ID
            location: Google Cloud location
            model_name: Vertex AI embeddings model name
        """
        self.credentials_path = credentials_path or settings.google_application_credentials
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        if not self.credentials_path:
            raise EmbeddingsError(
                "Google credentials path not provided",
                provider_name=self.provider_name,
            )
        
        try:
            # Initialize credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials,
            )
            
            logger.info(f"Initialized Google Vertex AI with project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Vertex AI: {e}")
            raise EmbeddingsError(
                f"Failed to initialize Google Vertex AI: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

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

            logger.debug(f"Generating Google embeddings for {len(truncated_texts)} texts")
            
            # Create embeddings
            from vertexai.preview.language_models import TextEmbeddingModel
            
            model = TextEmbeddingModel.from_pretrained(self.model_name)
            embeddings = model.get_embeddings(truncated_texts)
            
            # Extract embedding values
            result = [embedding.values for embedding in embeddings]
            
            logger.debug(f"Generated {len(result)} embeddings with dimension {len(result[0]) if result else 0}")
            return result

        except Exception as e:
            logger.error(f"Failed to generate Google embeddings: {e}")
            raise EmbeddingsError(
                f"Failed to generate Google embeddings: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider.
        
        Returns:
            Embedding dimension as integer
        """
        # Google textembedding-gecko has 768 dimensions
        if self.model_name == "textembedding-gecko":
            return 768
        else:
            # For unknown models, try to get dimension from a dummy request
            try:
                dummy_embedding = self.embed_texts(["dummy"])
                return len(dummy_embedding[0]) if dummy_embedding else 768
            except Exception:
                return 768  # Fallback

    @property
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "google_embeddings"


class GoogleLLMProvider(LLMProvider):
    """Google Vertex AI LLM provider."""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model_name: str = "text-bison",
        max_tokens: int = 2048,
    ):
        """Initialize Google LLM provider.
        
        Args:
            credentials_path: Path to Google service account credentials
            project_id: Google Cloud project ID
            location: Google Cloud location
            model_name: Vertex AI model name
            max_tokens: Maximum tokens to generate
        """
        self.credentials_path = credentials_path or settings.google_application_credentials
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self._max_tokens = max_tokens
        
        if not self.credentials_path:
            raise LLMError(
                "Google credentials path not provided",
                provider_name=self.provider_name,
            )
        
        try:
            # Initialize credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials,
            )
            
            logger.info(f"Initialized Google Vertex AI LLM with project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Vertex AI LLM: {e}")
            raise LLMError(
                f"Failed to initialize Google Vertex AI LLM: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def complete(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text completion using Google Vertex AI.
        
        Args:
            prompt: Input prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional Google parameters
            
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

            logger.debug(f"Generating Google completion with model: {self.model_name}")
            
            from vertexai.preview.language_models import TextGenerationModel
            
            model = TextGenerationModel.from_pretrained(self.model_name)
            response = model.predict(
                prompt=prompt,
                max_output_tokens=tokens_to_use,
                temperature=temp_to_use,
                **kwargs,
            )

            completion = response.text or ""
            logger.debug(f"Generated completion with {len(completion)} characters")
            return completion

        except Exception as e:
            logger.error(f"Failed to generate Google completion: {e}")
            raise LLMError(
                f"Failed to generate Google completion: {e}",
                provider_name=self.provider_name,
                original_error=e,
            )

    @property
    def provider_name(self) -> str:
        """Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "google_llm"

    @property
    def max_tokens(self) -> int:
        """Get the maximum tokens supported by this provider.
        
        Returns:
            Maximum tokens as integer
        """
        return self._max_tokens

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Google model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "location": self.location,
            "project_id": self.project_id,
        }


# Convenience functions to create Google providers
def create_google_embeddings_provider(
    credentials_path: Optional[str] = None,
    project_id: Optional[str] = None,
    location: str = "us-central1",
    model_name: str = "textembedding-gecko",
) -> GoogleEmbeddingsProvider:
    """Create Google embeddings provider.
    
    Args:
        credentials_path: Path to Google service account credentials
        project_id: Google Cloud project ID
        location: Google Cloud location
        model_name: Embeddings model name
        
    Returns:
        GoogleEmbeddingsProvider instance
    """
    return GoogleEmbeddingsProvider(
        credentials_path=credentials_path,
        project_id=project_id,
        location=location,
        model_name=model_name,
    )


def create_google_llm_provider(
    credentials_path: Optional[str] = None,
    project_id: Optional[str] = None,
    location: str = "us-central1",
    model_name: str = "text-bison",
    max_tokens: int = 2048,
) -> GoogleLLMProvider:
    """Create Google LLM provider.
    
    Args:
        credentials_path: Path to Google service account credentials
        project_id: Google Cloud project ID
        location: Google Cloud location
        model_name: LLM model name
        max_tokens: Maximum tokens to generate
        
    Returns:
        GoogleLLMProvider instance
    """
    return GoogleLLMProvider(
        credentials_path=credentials_path,
        project_id=project_id,
        location=location,
        model_name=model_name,
        max_tokens=max_tokens,
    )
