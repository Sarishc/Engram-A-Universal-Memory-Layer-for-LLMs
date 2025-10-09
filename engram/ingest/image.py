"""Image content extraction and processing."""

import os
import tempfile
import hashlib
from typing import List, Dict, Any, Union
from PIL import Image
import numpy as np

from engram.utils.logger import get_logger
from engram.utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class ImageExtractor:
    """Image content extractor with caption generation support."""
    
    def __init__(self):
        """Initialize image extractor."""
        self.blob_dir = settings.blob_store_dir
    
    def extract(
        self,
        content: Union[str, bytes],
        chunk_size: int = 512,
        chunk_overlap: int = 76,
        source_uri: str = None,
    ) -> List[Dict[str, Any]]:
        """Extract and process image content.
        
        Args:
            content: Image content (file path, URL, or bytes)
            chunk_size: Not used for images (kept for interface consistency)
            chunk_overlap: Not used for images (kept for interface consistency)
            source_uri: Source URI for the image
            
        Returns:
            List containing single image chunk with metadata
        """
        try:
            # Handle different content types
            if isinstance(content, bytes):
                # Save bytes to blob storage
                image_path = self._save_image_bytes(content, source_uri)
                image_data = self._load_image(image_path)
            elif isinstance(content, str):
                if content.startswith("http"):
                    # Download image from URL
                    image_path = self._download_image(content)
                    image_data = self._load_image(image_path)
                else:
                    # Local file path
                    image_path = content
                    image_data = self._load_image(image_path)
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            # Generate caption (optional)
            caption = self._generate_caption(image_path)
            
            # Extract metadata
            metadata = self._extract_image_metadata(image_data, source_uri)
            
            # Create chunk
            chunk = {
                "text": caption or f"Image: {metadata.get('filename', 'unknown')}",
                "metadata": {
                    "source_type": "image",
                    "source_uri": source_uri,
                    "image_path": image_path,
                    "caption": caption,
                    **metadata,
                },
                "image_path": image_path,  # For embedding generation
            }
            
            logger.info(f"Extracted image content: {metadata.get('filename', 'unknown')}")
            return [chunk]
            
        except Exception as e:
            logger.error(f"Error extracting image content: {e}")
            raise
    
    def _save_image_bytes(self, image_bytes: bytes, source_uri: str = None) -> str:
        """Save image bytes to blob storage.
        
        Args:
            image_bytes: Image bytes
            source_uri: Source URI for filename generation
            
        Returns:
            Path to saved image file
        """
        # Generate filename
        if source_uri:
            # Try to get filename from URL
            filename = os.path.basename(source_uri.split('?')[0])
            if not filename or '.' not in filename:
                filename = f"image_{hashlib.md5(image_bytes).hexdigest()[:8]}.jpg"
        else:
            filename = f"image_{hashlib.md5(image_bytes).hexdigest()[:8]}.jpg"
        
        # Ensure filename has extension
        if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            filename += '.jpg'
        
        # Save to blob directory
        os.makedirs(self.blob_dir, exist_ok=True)
        image_path = os.path.join(self.blob_dir, filename)
        
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        return image_path
    
    def _download_image(self, url: str) -> str:
        """Download image from URL.
        
        Args:
            url: Image URL
            
        Returns:
            Path to downloaded image file
        """
        import requests
        
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        return self._save_image_bytes(response.content, url)
    
    def _load_image(self, image_path: str) -> Image.Image:
        """Load and validate image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image object
        """
        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            raise
    
    def _generate_caption(self, image_path: str) -> str:
        """Generate caption for image (optional).
        
        Args:
            image_path: Path to image file
            
        Returns:
            Generated caption or empty string
        """
        try:
            # This is a placeholder for caption generation
            # In a real implementation, you might use:
            # - BLIP model for image captioning
            # - CLIP with text prompts
            # - Commercial APIs like OpenAI Vision
            
            # For now, return a simple descriptive caption
            filename = os.path.basename(image_path)
            return f"Image file: {filename}"
            
        except Exception as e:
            logger.warning(f"Error generating caption: {e}")
            return ""
    
    def _extract_image_metadata(self, image: Image.Image, source_uri: str = None) -> Dict[str, Any]:
        """Extract metadata from image.
        
        Args:
            image: PIL Image object
            source_uri: Source URI
            
        Returns:
            Image metadata dictionary
        """
        metadata = {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
            "size_bytes": 0,  # Would need file size
        }
        
        # Add filename if available
        if source_uri:
            metadata["filename"] = os.path.basename(source_uri.split('?')[0])
            metadata["domain"] = self._extract_domain(source_uri)
        
        # Extract EXIF data if available
        try:
            exif_data = image._getexif()
            if exif_data:
                metadata["exif"] = {
                    "camera": exif_data.get(271, ""),  # Make
                    "model": exif_data.get(272, ""),   # Model
                    "datetime": exif_data.get(306, ""), # DateTime
                }
        except Exception:
            pass  # EXIF data not available
        
        return metadata
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain name
        """
        from urllib.parse import urlparse
        return urlparse(url).netloc
