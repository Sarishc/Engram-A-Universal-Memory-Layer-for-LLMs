"""PDF content extraction and processing."""

import os
import tempfile
from typing import List, Dict, Any, Union
from abc import ABC, abstractmethod

from engram.utils.logger import get_logger

logger = get_logger(__name__)


class PDFExtractorBase(ABC):
    """Base class for PDF extractors."""
    
    @abstractmethod
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        pass


class PyMuPDFExtractor(PDFExtractorBase):
    """PDF extractor using PyMuPDF (fitz)."""
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF."""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()
            
            doc.close()
            return text
            
        except ImportError:
            logger.error("PyMuPDF not available. Install with: pip install PyMuPDF")
            raise
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {e}")
            raise


class PDFPlumberExtractor(PDFExtractorBase):
    """PDF extractor using pdfplumber."""
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text using pdfplumber."""
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text
            
        except ImportError:
            logger.error("pdfplumber not available. Install with: pip install pdfplumber")
            raise
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            raise


class PDFExtractor:
    """PDF content extractor with chunking support."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 76):
        """Initialize PDF extractor.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.extractor = self._get_best_extractor()
    
    def _get_best_extractor(self) -> PDFExtractorBase:
        """Get the best available PDF extractor."""
        # Try PyMuPDF first (faster)
        try:
            import fitz
            return PyMuPDFExtractor()
        except ImportError:
            pass
        
        # Fallback to pdfplumber
        try:
            import pdfplumber
            return PDFPlumberExtractor()
        except ImportError:
            pass
        
        raise ImportError("No PDF extraction library available. Install PyMuPDF or pdfplumber.")
    
    def extract(
        self,
        content: Union[str, bytes],
        chunk_size: int = 512,
        chunk_overlap: int = 76,
        source_uri: str = None,
    ) -> List[Dict[str, Any]]:
        """Extract and chunk PDF content.
        
        Args:
            content: PDF content (file path, URL, or bytes)
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            source_uri: Source URI for the PDF
            
        Returns:
            List of text chunks with metadata
        """
        try:
            # Handle different content types
            if isinstance(content, bytes):
                # Save bytes to temporary file
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                    tmp_file.write(content)
                    pdf_path = tmp_file.name
                
                try:
                    text = self.extractor.extract_text(pdf_path)
                finally:
                    os.unlink(pdf_path)  # Clean up temp file
                    
            elif isinstance(content, str):
                if content.startswith("http"):
                    # Download PDF from URL
                    pdf_path = self._download_pdf(content)
                    try:
                        text = self.extractor.extract_text(pdf_path)
                    finally:
                        os.unlink(pdf_path)  # Clean up downloaded file
                else:
                    # Local file path
                    text = self.extractor.extract_text(content)
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            if not text.strip():
                logger.warning("No text extracted from PDF")
                return []
            
            # Chunk the text
            chunks = self._chunk_text(text, chunk_size, chunk_overlap)
            
            # Add metadata
            chunked_content = []
            for i, chunk in enumerate(chunks):
                chunked_content.append({
                    "text": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "source_type": "pdf",
                        "source_uri": source_uri,
                        "total_chunks": len(chunks),
                    }
                })
            
            logger.info(f"Extracted {len(chunks)} chunks from PDF")
            return chunked_content
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            raise
    
    def _download_pdf(self, url: str) -> str:
        """Download PDF from URL.
        
        Args:
            url: PDF URL
            
        Returns:
            Path to downloaded PDF file
        """
        import requests
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Chunk text into overlapping segments.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            
        Returns:
            List of text chunks
        """
        # Simple word-based chunking (can be improved with tokenization)
        words = text.split()
        
        if len(words) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            
            if end == len(words):
                break
                
            start = end - chunk_overlap
        
        return chunks
