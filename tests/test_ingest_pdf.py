"""Tests for PDF ingestion."""

import pytest
from unittest.mock import Mock, patch
from engram.ingest.pdf import PDFExtractor


class TestPDFExtractor:
    """Test PDF extractor functionality."""
    
    def test_pdf_extractor_init(self):
        """Test PDF extractor initialization."""
        extractor = PDFExtractor()
        assert extractor.chunk_size == 512
        assert extractor.chunk_overlap == 76
        assert extractor.extractor is not None
    
    def test_chunk_text_simple(self):
        """Test text chunking functionality."""
        extractor = PDFExtractor()
        text = "This is a simple test text that should be chunked properly."
        
        chunks = extractor._chunk_text(text, chunk_size=10, chunk_overlap=2)
        
        assert len(chunks) > 0
        assert all(len(chunk.split()) <= 10 for chunk in chunks)
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        extractor = PDFExtractor()
        chunks = extractor._chunk_text("", chunk_size=10, chunk_overlap=2)
        assert chunks == [""]
    
    @patch('engram.ingest.pdf.tempfile.NamedTemporaryFile')
    def test_extract_from_bytes(self, mock_tempfile):
        """Test extracting from bytes."""
        extractor = PDFExtractor()
        
        # Mock the temporary file
        mock_file = Mock()
        mock_file.name = "/tmp/test.pdf"
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock the extractor
        extractor.extractor.extract_text = Mock(return_value="Sample PDF text")
        
        # Mock os.unlink
        with patch('engram.ingest.pdf.os.unlink'):
            result = extractor.extract(b"fake pdf bytes")
            
            assert len(result) > 0
            assert result[0]["text"] == "Sample PDF text"
            assert result[0]["metadata"]["source_type"] == "pdf"
    
    def test_extract_invalid_content(self):
        """Test extracting with invalid content type."""
        extractor = PDFExtractor()
        
        with pytest.raises(ValueError):
            extractor.extract(123)  # Invalid content type
