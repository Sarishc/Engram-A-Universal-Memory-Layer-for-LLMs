"""Web content extraction and processing."""

import re
from typing import List, Dict, Any, Union
from urllib.parse import urlparse
import tempfile
import os

from engram.utils.logger import get_logger

logger = get_logger(__name__)


class WebExtractor:
    """Web content extractor with chunking support."""
    
    def __init__(self):
        """Initialize web extractor."""
        self.extractor = self._get_best_extractor()
    
    def _get_best_extractor(self):
        """Get the best available web content extractor."""
        # Try trafilatura first
        try:
            import trafilatura
            return "trafilatura"
        except ImportError:
            pass
        
        # Fallback to readability
        try:
            from readability import Document
            import requests
            from bs4 import BeautifulSoup
            return "readability"
        except ImportError:
            pass
        
        # Fallback to basic extraction
        try:
            import requests
            from bs4 import BeautifulSoup
            return "basic"
        except ImportError:
            pass
        
        raise ImportError("No web extraction library available. Install trafilatura or readability-lxml.")
    
    def extract(
        self,
        content: Union[str, bytes],
        chunk_size: int = 512,
        chunk_overlap: int = 76,
        source_uri: str = None,
    ) -> List[Dict[str, Any]]:
        """Extract and chunk web content.
        
        Args:
            content: Web content (URL or HTML)
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            source_uri: Source URI for the web content
            
        Returns:
            List of text chunks with metadata
        """
        try:
            # Handle different content types
            if isinstance(content, str):
                if content.startswith("http"):
                    # Download and extract from URL
                    text, metadata = self._extract_from_url(content)
                else:
                    # Treat as HTML content
                    text, metadata = self._extract_from_html(content)
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            if not text.strip():
                logger.warning("No text extracted from web content")
                return []
            
            # Clean and preprocess text
            text = self._clean_text(text)
            
            # Chunk the text
            chunks = self._chunk_text(text, chunk_size, chunk_overlap)
            
            # Add metadata
            chunked_content = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "chunk_index": i,
                    "source_type": "web",
                    "source_uri": source_uri,
                    "total_chunks": len(chunks),
                    **metadata,
                }
                
                chunked_content.append({
                    "text": chunk,
                    "metadata": chunk_metadata,
                })
            
            logger.info(f"Extracted {len(chunks)} chunks from web content")
            return chunked_content
            
        except Exception as e:
            logger.error(f"Error extracting web content: {e}")
            raise
    
    def _extract_from_url(self, url: str) -> tuple[str, Dict[str, Any]]:
        """Extract content from URL.
        
        Args:
            url: Web page URL
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        import requests
        
        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            html_content = response.text
            metadata = {
                "url": url,
                "title": self._extract_title_from_html(html_content),
                "domain": urlparse(url).netloc,
                "status_code": response.status_code,
            }
            
            return self._extract_from_html(html_content, metadata)
            
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            raise
    
    def _extract_from_html(self, html_content: str, metadata: Dict[str, Any] = None) -> tuple[str, Dict[str, Any]]:
        """Extract content from HTML.
        
        Args:
            html_content: HTML content
            metadata: Optional metadata
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        if metadata is None:
            metadata = {}
        
        if self.extractor == "trafilatura":
            return self._extract_with_trafilatura(html_content, metadata)
        elif self.extractor == "readability":
            return self._extract_with_readability(html_content, metadata)
        else:
            return self._extract_with_basic(html_content, metadata)
    
    def _extract_with_trafilatura(self, html_content: str, metadata: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Extract content using trafilatura."""
        import trafilatura
        
        # Extract main content
        text = trafilatura.extract(html_content, include_links=False, include_images=False)
        
        if text:
            # Extract metadata
            extracted_metadata = trafilatura.extract_metadata(html_content)
            if extracted_metadata:
                metadata.update({
                    "title": extracted_metadata.title,
                    "author": extracted_metadata.author,
                    "date": extracted_metadata.date,
                    "description": extracted_metadata.description,
                })
        
        return text or "", metadata
    
    def _extract_with_readability(self, html_content: str, metadata: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Extract content using readability."""
        from readability import Document
        from bs4 import BeautifulSoup
        
        doc = Document(html_content)
        clean_html = doc.summary()
        
        soup = BeautifulSoup(clean_html, 'html.parser')
        text = soup.get_text()
        
        # Extract title from original HTML
        if not metadata.get("title"):
            title_soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = title_soup.find('title')
            if title_tag:
                metadata["title"] = title_tag.get_text().strip()
        
        return text, metadata
    
    def _extract_with_basic(self, html_content: str, metadata: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Extract content using basic BeautifulSoup."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract title
        if not metadata.get("title"):
            title_tag = soup.find('title')
            if title_tag:
                metadata["title"] = title_tag.get_text().strip()
        
        # Get text
        text = soup.get_text()
        
        return text, metadata
    
    def _extract_title_from_html(self, html_content: str) -> str:
        """Extract title from HTML content."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('title')
        
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1 tag as fallback
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common web artifacts
        text = re.sub(r'Cookie Policy|Privacy Policy|Terms of Service|Subscribe|Newsletter', '', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Chunk text into overlapping segments.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            
        Returns:
            List of text chunks
        """
        # Split into paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return [text] if text.strip() else []
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size, finalize current chunk
            if current_chunk and len((current_chunk + " " + paragraph).split()) > chunk_size:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                words = current_chunk.split()
                if len(words) > chunk_overlap:
                    overlap_words = words[-chunk_overlap:]
                    current_chunk = " ".join(overlap_words) + " " + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += " " + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
