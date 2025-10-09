"""ID generation utilities."""

import time
from typing import Optional

import ulid


def generate_ulid() -> str:
    """Generate a unique ULID.
    
    Returns:
        ULID string
    """
    return str(ulid.new())


def generate_memory_id() -> str:
    """Generate a unique memory ID using ULID.
    
    Returns:
        ULID string for memory identification
    """
    return str(ulid.new())


def generate_tenant_id() -> str:
    """Generate a unique tenant ID using ULID.
    
    Returns:
        ULID string for tenant identification
    """
    return str(ulid.new())


def generate_user_id() -> str:
    """Generate a unique user ID using ULID.
    
    Returns:
        ULID string for user identification
    """
    return str(ulid.new())


def generate_request_id() -> str:
    """Generate a unique request ID using ULID.
    
    Returns:
        ULID string for request tracing
    """
    return str(ulid.new())


def parse_ulid(ulid_str: str) -> Optional[dict]:
    """Parse ULID string to extract timestamp and other metadata.
    
    Args:
        ulid_str: ULID string to parse
        
    Returns:
        Dictionary with parsed ULID data or None if invalid
    """
    try:
        parsed = ulid.parse(ulid_str)
        return {
            "timestamp": parsed.timestamp,
            "datetime": parsed.datetime,
            "randomness": parsed.randomness,
            "bytes": parsed.bytes,
        }
    except ValueError:
        return None


def is_valid_ulid(ulid_str: str) -> bool:
    """Check if string is a valid ULID.
    
    Args:
        ulid_str: String to validate
        
    Returns:
        True if valid ULID, False otherwise
    """
    try:
        ulid.parse(ulid_str)
        return True
    except ValueError:
        return False


def ulid_to_timestamp(ulid_str: str) -> Optional[float]:
    """Extract timestamp from ULID.
    
    Args:
        ulid_str: ULID string
        
    Returns:
        Unix timestamp or None if invalid
    """
    parsed = parse_ulid(ulid_str)
    return parsed["timestamp"] if parsed else None


def timestamp_to_ulid(timestamp: Optional[float] = None) -> str:
    """Generate ULID from timestamp.
    
    Args:
        timestamp: Unix timestamp (defaults to current time)
        
    Returns:
        ULID string
    """
    if timestamp is None:
        timestamp = time.time()
    
    # Convert to milliseconds for ULID
    timestamp_ms = int(timestamp * 1000)
    return str(ulid.from_timestamp(timestamp_ms))
