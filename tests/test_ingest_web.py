"""Tests for web ingestion."""

import pytest
from unittest.mock import Mock, patch
from engram.ingest.web import WebExtractor


class TestWebExtractor:
    """Test web extractor functionality."""
    
    def test_web_extractor_init(self):
        """Test web extractor initialization."""
        extractor = WebExtractor()
        assert extractor.extractor is not None
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        extractor = WebExtractor()
        
        dirty_text = "This   has    lots    of   spaces.  \n\n\nAnd newlines."
        clean_text = extractor._clean_text(dirty_text)
        
        assert "   " not in clean_text
        assert "\n\n\n" not in clean_text
        assert len(clean_text) < len(dirty_text)
    
    def test_chunk_text_paragraphs(self):
        """Test chunking text with paragraphs."""
        extractor = WebExtractor()
        
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = extractor._chunk_text(text, chunk_size=10, chunk_overlap=2)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        extractor = WebExtractor()
        chunks = extractor._chunk_text("", chunk_size=10, chunk_overlap=2)
        assert chunks == []
    
    @patch('engram.ingest.web.requests.get')
    def test_extract_from_url(self, mock_get):
        """Test extracting from URL."""
        extractor = WebExtractor()
        
        # Mock response
        mock_response = Mock()
        mock_response.text = "<html><body><h1>Test Page</h1><p>Test content</p></body></html>"
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock HTML extraction
        with patch.object(extractor, '_extract_from_html', return_value=("Test content", {})):
            text, metadata = extractor._extract_from_url("http://example.com")
            
            assert text == "Test content"
            assert "url" in metadata
            assert metadata["url"] == "http://example.com"
    
    def test_extract_invalid_content(self):
        """Test extracting with invalid content type."""
        extractor = WebExtractor()
        
        with pytest.raises(ValueError):
            extractor.extract(123)  # Invalid content type
