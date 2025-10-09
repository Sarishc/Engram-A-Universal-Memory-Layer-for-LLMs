"""Multimodal embeddings registry for different content types."""

import os
import logging
from typing import List, Union, Optional, Dict, Any
from abc import ABC, abstractmethod
import numpy as np
from PIL import Image
import requests
from io import BytesIO

from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def embed_images(self, images: Union[List[str], List[np.ndarray]]) -> List[List[float]]:
        """Embed a list of images.
        
        Args:
            images: List of image paths or numpy arrays
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this provider."""
        pass


class SentenceTransformersProvider(EmbeddingProvider):
    """Sentence transformers provider for text embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the sentence transformers provider.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self._model_name = model_name
        except ImportError:
            logger.error("sentence-transformers not available. Install with: pip install sentence-transformers")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed text using sentence transformers."""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding texts with sentence transformers: {e}")
            raise
    
    def embed_images(self, images: Union[List[str], List[np.ndarray]]) -> List[List[float]]:
        """Sentence transformers doesn't support images directly."""
        raise NotImplementedError("Sentence transformers provider doesn't support image embeddings")
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return f"sentence-transformers-{self._model_name}"


class CLIPProvider(EmbeddingProvider):
    """CLIP provider for multimodal embeddings."""
    
    def __init__(self, model_name: str = "ViT-B-32", pretrained: str = "laion2b_s34b_b79k"):
        """Initialize the CLIP provider.
        
        Args:
            model_name: CLIP model name
            pretrained: Pretrained dataset name
        """
        try:
            import open_clip
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                model_name, pretrained=pretrained
            )
            self.tokenizer = open_clip.get_tokenizer(model_name)
            self._model_name = model_name
            self._pretrained = pretrained
        except ImportError:
            logger.error("open-clip-torch not available. Install with: pip install open-clip-torch")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed text using CLIP text encoder."""
        try:
            text_tokens = self.tokenizer(texts)
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            return text_features.cpu().numpy().tolist()
        except Exception as e:
            logger.error(f"Error embedding texts with CLIP: {e}")
            raise
    
    def embed_images(self, images: Union[List[str], List[np.ndarray]]) -> List[List[float]]:
        """Embed images using CLIP vision encoder."""
        try:
            import torch
            
            processed_images = []
            for img in images:
                if isinstance(img, str):
                    # Load image from path
                    image = Image.open(img).convert('RGB')
                elif isinstance(img, np.ndarray):
                    # Convert numpy array to PIL Image
                    if img.dtype != np.uint8:
                        img = (img * 255).astype(np.uint8)
                    image = Image.fromarray(img).convert('RGB')
                else:
                    raise ValueError(f"Unsupported image type: {type(img)}")
                
                processed_img = self.preprocess(image)
                processed_images.append(processed_img)
            
            # Stack images into batch
            image_tensor = torch.stack(processed_images)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().tolist()
            
        except Exception as e:
            logger.error(f"Error embedding images with CLIP: {e}")
            raise
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.visual.output_dim
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return f"clip-{self._model_name}-{self._pretrained}"


class OpenAIEmbeddingsProvider(EmbeddingProvider):
    """OpenAI embeddings provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-ada-002"):
        """Initialize OpenAI embeddings provider.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI embedding model name
        """
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or settings.openai_api_key)
            self._model = model
        except ImportError:
            logger.error("openai not available. Install with: pip install openai")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed text using OpenAI embeddings."""
        try:
            response = self.client.embeddings.create(
                model=self._model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error embedding texts with OpenAI: {e}")
            raise
    
    def embed_images(self, images: Union[List[str], List[np.ndarray]]) -> List[List[float]]:
        """OpenAI embeddings doesn't support images directly."""
        raise NotImplementedError("OpenAI embeddings provider doesn't support image embeddings")
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension based on model."""
        if "ada-002" in self._model:
            return 1536
        elif "3-small" in self._model:
            return 1536
        elif "3-large" in self._model:
            return 3072
        else:
            # Default to 1536 for unknown models
            return 1536
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return f"openai-{self._model}"


class MultimodalEmbeddingsRegistry:
    """Registry for multimodal embedding providers."""
    
    def __init__(self):
        """Initialize the registry with default providers."""
        self._providers: Dict[str, EmbeddingProvider] = {}
        self._default_providers: Dict[str, str] = {
            "text": "sentence_transformers",
            "image": "clip",
            "pdf": "sentence_transformers",
            "web": "sentence_transformers",
            "chat": "sentence_transformers",
            "video": "sentence_transformers",  # For transcripts
        }
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize default embedding providers."""
        try:
            # Initialize sentence transformers for text
            self._providers["sentence_transformers"] = SentenceTransformersProvider()
            logger.info("Initialized sentence transformers provider")
        except Exception as e:
            logger.warning(f"Failed to initialize sentence transformers: {e}")
        
        try:
            # Initialize CLIP for images
            self._providers["clip"] = CLIPProvider()
            logger.info("Initialized CLIP provider")
        except Exception as e:
            logger.warning(f"Failed to initialize CLIP: {e}")
        
        # Initialize OpenAI if API key is available
        if settings.openai_api_key:
            try:
                self._providers["openai"] = OpenAIEmbeddingsProvider()
                logger.info("Initialized OpenAI embeddings provider")
                # Override default for text if OpenAI is available
                self._default_providers["text"] = "openai"
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
    
    def get_provider(self, modality: str) -> EmbeddingProvider:
        """Get the appropriate embedding provider for a modality.
        
        Args:
            modality: Content modality (text, image, pdf, etc.)
            
        Returns:
            Embedding provider instance
            
        Raises:
            ValueError: If no provider is available for the modality
        """
        # Get the default provider for this modality
        provider_name = self._default_providers.get(modality)
        
        if not provider_name:
            raise ValueError(f"No default provider configured for modality: {modality}")
        
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not available for modality: {modality}")
        
        return provider
    
    def embed_texts(self, texts: List[str], modality: str = "text") -> List[List[float]]:
        """Embed texts using the appropriate provider.
        
        Args:
            texts: List of text strings
            modality: Content modality
            
        Returns:
            List of embedding vectors
        """
        provider = self.get_provider(modality)
        return provider.embed_texts(texts)
    
    def embed_images(self, images: Union[List[str], List[np.ndarray]]) -> List[List[float]]:
        """Embed images using the appropriate provider.
        
        Args:
            images: List of image paths or numpy arrays
            
        Returns:
            List of embedding vectors
        """
        provider = self.get_provider("image")
        return provider.embed_images(images)
    
    def get_dimension(self, modality: str) -> int:
        """Get the embedding dimension for a modality.
        
        Args:
            modality: Content modality
            
        Returns:
            Embedding dimension
        """
        provider = self.get_provider(modality)
        return provider.dimension
    
    def list_providers(self) -> Dict[str, str]:
        """List available providers.
        
        Returns:
            Dictionary mapping provider names to their types
        """
        return {
            name: provider.provider_name 
            for name, provider in self._providers.items()
        }


# Global registry instance
embeddings_registry = MultimodalEmbeddingsRegistry()
