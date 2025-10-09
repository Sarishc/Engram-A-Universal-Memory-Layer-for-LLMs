"""Chat content extraction and processing."""

import json
from typing import List, Dict, Any, Union
from datetime import datetime

from engram.utils.logger import get_logger

logger = get_logger(__name__)


class ChatExtractor:
    """Chat content extractor for various platforms."""
    
    def __init__(self):
        """Initialize chat extractor."""
        self.platform_extractors = {
            "slack": self._extract_slack,
            "discord": self._extract_discord,
            "json": self._extract_json,
            "generic": self._extract_generic,
        }
    
    def extract(
        self,
        content: Union[str, bytes, List[Dict[str, Any]]],
        chunk_size: int = 512,
        chunk_overlap: int = 76,
        source_uri: str = None,
        platform: str = "generic",
    ) -> List[Dict[str, Any]]:
        """Extract and process chat content.
        
        Args:
            content: Chat content (JSON string, bytes, or list of messages)
            chunk_size: Target chunk size for messages
            chunk_overlap: Overlap between chunks
            source_uri: Source URI for the chat data
            platform: Chat platform (slack, discord, json, generic)
            
        Returns:
            List of chat chunks with metadata
        """
        try:
            # Parse content based on type
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            if isinstance(content, str):
                try:
                    messages = json.loads(content)
                except json.JSONDecodeError:
                    # Treat as raw text
                    messages = [{"text": content, "author": "unknown", "timestamp": datetime.now().isoformat()}]
            elif isinstance(content, list):
                messages = content
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
            
            # Extract using platform-specific extractor
            extractor = self.platform_extractors.get(platform, self._extract_generic)
            normalized_messages = extractor(messages)
            
            if not normalized_messages:
                logger.warning("No messages extracted from chat content")
                return []
            
            # Group messages into chunks
            chunks = self._chunk_messages(normalized_messages, chunk_size, chunk_overlap)
            
            # Create chat chunks
            chat_chunks = []
            for i, chunk in enumerate(chunks):
                chat_chunks.append({
                    "text": chunk["text"],
                    "metadata": {
                        "chunk_index": i,
                        "source_type": "chat",
                        "source_uri": source_uri,
                        "platform": platform,
                        "total_chunks": len(chunks),
                        "message_count": chunk["message_count"],
                        "time_range": chunk["time_range"],
                        "authors": chunk["authors"],
                    },
                    "messages": chunk["messages"],
                })
            
            logger.info(f"Extracted {len(chat_chunks)} chunks from {platform} chat with {len(normalized_messages)} messages")
            return chat_chunks
            
        except Exception as e:
            logger.error(f"Error extracting chat content: {e}")
            raise
    
    def _extract_slack(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract messages from Slack export format.
        
        Args:
            messages: List of Slack messages
            
        Returns:
            List of normalized messages
        """
        normalized = []
        
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            
            # Extract text content
            text = msg.get("text", "")
            if not text:
                continue
            
            # Extract user info
            user = msg.get("user", "unknown")
            if isinstance(user, dict):
                user = user.get("name", "unknown")
            
            # Extract timestamp
            timestamp = msg.get("ts", "")
            if timestamp:
                try:
                    # Slack timestamps are Unix timestamps
                    timestamp = datetime.fromtimestamp(float(timestamp)).isoformat()
                except (ValueError, TypeError):
                    timestamp = datetime.now().isoformat()
            
            normalized.append({
                "text": text,
                "author": user,
                "timestamp": timestamp,
                "channel": msg.get("channel", ""),
                "thread_ts": msg.get("thread_ts", ""),
                "type": msg.get("type", "message"),
            })
        
        return normalized
    
    def _extract_discord(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract messages from Discord export format.
        
        Args:
            messages: List of Discord messages
            
        Returns:
            List of normalized messages
        """
        normalized = []
        
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            
            # Extract text content
            content = msg.get("content", "")
            if not content:
                continue
            
            # Extract author
            author = msg.get("author", {})
            if isinstance(author, dict):
                author_name = author.get("username", "unknown")
            else:
                author_name = str(author)
            
            # Extract timestamp
            timestamp = msg.get("timestamp", "")
            if timestamp:
                try:
                    # Discord timestamps are ISO format
                    if timestamp.endswith('Z'):
                        timestamp = timestamp[:-1]
                    timestamp = datetime.fromisoformat(timestamp).isoformat()
                except (ValueError, TypeError):
                    timestamp = datetime.now().isoformat()
            
            normalized.append({
                "text": content,
                "author": author_name,
                "timestamp": timestamp,
                "channel": msg.get("channel", ""),
                "guild": msg.get("guild", ""),
                "type": msg.get("type", "message"),
            })
        
        return normalized
    
    def _extract_json(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract messages from generic JSON format.
        
        Args:
            messages: List of message objects
            
        Returns:
            List of normalized messages
        """
        normalized = []
        
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            
            # Try to extract common fields
            text = msg.get("text") or msg.get("content") or msg.get("message", "")
            if not text:
                continue
            
            author = msg.get("author") or msg.get("user") or msg.get("username", "unknown")
            timestamp = msg.get("timestamp") or msg.get("date") or msg.get("time", "")
            
            # Parse timestamp if it's a string
            if isinstance(timestamp, str) and timestamp:
                try:
                    # Try common timestamp formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            timestamp = datetime.strptime(timestamp, fmt).isoformat()
                            break
                        except ValueError:
                            continue
                    else:
                        # If no format matches, use current time
                        timestamp = datetime.now().isoformat()
                except (ValueError, TypeError):
                    timestamp = datetime.now().isoformat()
            elif not timestamp:
                timestamp = datetime.now().isoformat()
            
            normalized.append({
                "text": text,
                "author": author,
                "timestamp": timestamp,
                "metadata": {k: v for k, v in msg.items() if k not in ["text", "content", "message", "author", "user", "username", "timestamp", "date", "time"]},
            })
        
        return normalized
    
    def _extract_generic(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract messages from generic format.
        
        Args:
            messages: List of message objects
            
        Returns:
            List of normalized messages
        """
        normalized = []
        
        for msg in messages:
            if isinstance(msg, str):
                # Simple string message
                normalized.append({
                    "text": msg,
                    "author": "unknown",
                    "timestamp": datetime.now().isoformat(),
                })
            elif isinstance(msg, dict):
                # Try to extract text and author
                text = msg.get("text") or msg.get("content") or msg.get("message", "")
                if text:
                    normalized.append({
                        "text": text,
                        "author": msg.get("author", "unknown"),
                        "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                        "metadata": {k: v for k, v in msg.items() if k not in ["text", "content", "message", "author", "timestamp"]},
                    })
        
        return normalized
    
    def _chunk_messages(self, messages: List[Dict[str, Any]], chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
        """Group messages into chunks.
        
        Args:
            messages: List of normalized messages
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of message chunks
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_authors = set()
        chunk_timestamps = []
        
        for msg in messages:
            msg_tokens = len(msg["text"].split())
            
            # If adding this message would exceed chunk size, finalize current chunk
            if current_chunk and current_tokens + msg_tokens > chunk_size:
                chunks.append(self._create_chunk(current_chunk, chunk_authors, chunk_timestamps))
                
                # Start new chunk with overlap
                if current_chunk and len(current_chunk) > 1:
                    # Keep last few messages for overlap
                    overlap_messages = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                    current_chunk = overlap_messages
                    current_tokens = sum(len(m["text"].split()) for m in overlap_messages)
                    chunk_authors = {m["author"] for m in overlap_messages}
                    chunk_timestamps = [m["timestamp"] for m in overlap_messages]
                else:
                    current_chunk = []
                    current_tokens = 0
                    chunk_authors = set()
                    chunk_timestamps = []
            
            current_chunk.append(msg)
            current_tokens += msg_tokens
            chunk_authors.add(msg["author"])
            chunk_timestamps.append(msg["timestamp"])
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, chunk_authors, chunk_timestamps))
        
        return chunks
    
    def _create_chunk(self, messages: List[Dict[str, Any]], authors: set, timestamps: List[str]) -> Dict[str, Any]:
        """Create a chunk from messages.
        
        Args:
            messages: List of messages in chunk
            authors: Set of authors in chunk
            timestamps: List of timestamps in chunk
            
        Returns:
            Chunk dictionary
        """
        # Combine messages into text
        text_parts = []
        for msg in messages:
            author = msg["author"]
            text = msg["text"]
            timestamp = msg["timestamp"]
            
            # Format: [timestamp] author: message
            formatted_msg = f"[{timestamp}] {author}: {text}"
            text_parts.append(formatted_msg)
        
        text = "\n".join(text_parts)
        
        # Determine time range
        if timestamps:
            time_range = f"{min(timestamps)} to {max(timestamps)}"
        else:
            time_range = "unknown"
        
        return {
            "text": text,
            "messages": messages,
            "message_count": len(messages),
            "authors": list(authors),
            "time_range": time_range,
        }
