"""Video content extraction and processing."""

import os
import tempfile
import hashlib
from typing import List, Dict, Any, Union, Tuple
import numpy as np

from engram.utils.logger import get_logger
from engram.utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class VideoExtractor:
    """Video content extractor with transcript and keyframe extraction."""
    
    def __init__(self):
        """Initialize video extractor."""
        self.blob_dir = settings.blob_store_dir
        self.keyframe_interval = getattr(settings, 'keyframe_sec', 8)
        self.whisper_model = getattr(settings, 'whisper_model', 'small')
    
    def extract(
        self,
        content: Union[str, bytes],
        chunk_size: int = 512,
        chunk_overlap: int = 76,
        source_uri: str = None,
    ) -> List[Dict[str, Any]]:
        """Extract and process video content.
        
        Args:
            content: Video content (file path, URL, or bytes)
            chunk_size: Target chunk size for transcripts
            chunk_overlap: Overlap between transcript chunks
            source_uri: Source URI for the video
            
        Returns:
            List of video chunks (transcript + keyframes)
        """
        try:
            # Handle different content types
            if isinstance(content, bytes):
                # Save bytes to blob storage
                video_path = self._save_video_bytes(content, source_uri)
            elif isinstance(content, str):
                if content.startswith("http"):
                    # Download video from URL
                    video_path = self._download_video(content)
                else:
                    # Local file path
                    video_path = content
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            chunks = []
            
            # Extract transcript
            transcript_chunks = self._extract_transcript(video_path, chunk_size, chunk_overlap, source_uri)
            chunks.extend(transcript_chunks)
            
            # Extract keyframes
            keyframe_chunks = self._extract_keyframes(video_path, source_uri)
            chunks.extend(keyframe_chunks)
            
            logger.info(f"Extracted {len(chunks)} chunks from video: {len(transcript_chunks)} transcript, {len(keyframe_chunks)} keyframes")
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting video content: {e}")
            raise
    
    def _save_video_bytes(self, video_bytes: bytes, source_uri: str = None) -> str:
        """Save video bytes to blob storage.
        
        Args:
            video_bytes: Video bytes
            source_uri: Source URI for filename generation
            
        Returns:
            Path to saved video file
        """
        # Generate filename
        if source_uri:
            filename = os.path.basename(source_uri.split('?')[0])
            if not filename or '.' not in filename:
                filename = f"video_{hashlib.md5(video_bytes).hexdigest()[:8]}.mp4"
        else:
            filename = f"video_{hashlib.md5(video_bytes).hexdigest()[:8]}.mp4"
        
        # Ensure filename has extension
        if not any(filename.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
            filename += '.mp4'
        
        # Save to blob directory
        os.makedirs(self.blob_dir, exist_ok=True)
        video_path = os.path.join(self.blob_dir, filename)
        
        with open(video_path, 'wb') as f:
            f.write(video_bytes)
        
        return video_path
    
    def _download_video(self, url: str) -> str:
        """Download video from URL.
        
        Args:
            url: Video URL
            
        Returns:
            Path to downloaded video file
        """
        import requests
        
        response = requests.get(url, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        return self._save_video_bytes(response.content, url)
    
    def _extract_transcript(self, video_path: str, chunk_size: int, chunk_overlap: int, source_uri: str) -> List[Dict[str, Any]]:
        """Extract transcript from video using Whisper.
        
        Args:
            video_path: Path to video file
            chunk_size: Target chunk size for transcripts
            chunk_overlap: Overlap between chunks
            source_uri: Source URI
            
        Returns:
            List of transcript chunks
        """
        try:
            transcript = self._transcribe_video(video_path)
            
            if not transcript.strip():
                logger.warning("No transcript extracted from video")
                return []
            
            # Chunk the transcript
            chunks = self._chunk_text(transcript, chunk_size, chunk_overlap)
            
            # Create transcript chunks
            transcript_chunks = []
            for i, chunk in enumerate(chunks):
                transcript_chunks.append({
                    "text": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "source_type": "video_transcript",
                        "source_uri": source_uri,
                        "total_chunks": len(chunks),
                        "content_type": "transcript",
                    },
                    "transcript": chunk,
                })
            
            return transcript_chunks
            
        except Exception as e:
            logger.error(f"Error extracting transcript: {e}")
            return []
    
    def _transcribe_video(self, video_path: str) -> str:
        """Transcribe video using Whisper.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Transcribed text
        """
        try:
            # Try faster-whisper first
            try:
                from faster_whisper import WhisperModel
                model = WhisperModel(self.whisper_model, device="cpu", compute_type="int8")
                segments, info = model.transcribe(video_path)
                
                transcript_parts = []
                for segment in segments:
                    transcript_parts.append(segment.text.strip())
                
                return " ".join(transcript_parts)
                
            except ImportError:
                # Fallback to openai-whisper
                import whisper
                model = whisper.load_model(self.whisper_model)
                result = model.transcribe(video_path)
                return result["text"]
                
        except ImportError:
            logger.error("Whisper not available. Install with: pip install faster-whisper or pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"Error transcribing video: {e}")
            raise
    
    def _extract_keyframes(self, video_path: str, source_uri: str) -> List[Dict[str, Any]]:
        """Extract keyframes from video.
        
        Args:
            video_path: Path to video file
            source_uri: Source URI
            
        Returns:
            List of keyframe chunks
        """
        try:
            keyframes = self._extract_video_keyframes(video_path)
            
            keyframe_chunks = []
            for i, (timestamp, image_path) in enumerate(keyframes):
                keyframe_chunks.append({
                    "text": f"Video keyframe at {timestamp}s",
                    "metadata": {
                        "chunk_index": i,
                        "source_type": "video_keyframe",
                        "source_uri": source_uri,
                        "timestamp": timestamp,
                        "content_type": "keyframe",
                    },
                    "image_path": image_path,
                    "timestamp": timestamp,
                })
            
            return keyframe_chunks
            
        except Exception as e:
            logger.error(f"Error extracting keyframes: {e}")
            return []
    
    def _extract_video_keyframes(self, video_path: str) -> List[Tuple[float, str]]:
        """Extract keyframes from video using ffmpeg.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of (timestamp, image_path) tuples
        """
        try:
            import ffmpeg
            
            # Get video duration
            probe = ffmpeg.probe(video_path)
            duration = float(probe['streams'][0]['duration'])
            
            # Calculate keyframe timestamps
            timestamps = []
            current_time = 0
            while current_time < duration:
                timestamps.append(current_time)
                current_time += self.keyframe_interval
            
            # Extract keyframes
            keyframes = []
            for i, timestamp in enumerate(timestamps):
                # Generate keyframe filename
                keyframe_filename = f"keyframe_{os.path.basename(video_path)}_{i:03d}.jpg"
                keyframe_path = os.path.join(self.blob_dir, keyframe_filename)
                
                try:
                    # Extract frame at timestamp
                    (
                        ffmpeg
                        .input(video_path, ss=timestamp)
                        .output(keyframe_path, vframes=1, format='image2')
                        .overwrite_output()
                        .run(quiet=True)
                    )
                    
                    keyframes.append((timestamp, keyframe_path))
                    
                except ffmpeg.Error as e:
                    logger.warning(f"Error extracting keyframe at {timestamp}s: {e}")
                    continue
            
            return keyframes
            
        except ImportError:
            logger.error("ffmpeg-python not available. Install with: pip install ffmpeg-python")
            raise
        except Exception as e:
            logger.error(f"Error extracting video keyframes: {e}")
            raise
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Chunk text into overlapping segments.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            
        Returns:
            List of text chunks
        """
        # Simple word-based chunking
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
