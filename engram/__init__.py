"""Engram - Universal Memory Layer for Multi-Provider LLMs.

A provider-agnostic semantic memory service that stores, retrieves, and consolidates
memories for LLM applications with multi-tenant isolation and sub-100ms retrieval times.
"""

__version__ = "0.1.0"
__author__ = "Engram Team"
__email__ = "team@engram.ai"
__description__ = "Universal Memory Layer for Multi-Provider LLMs"

# Core imports for easy access
from engram.utils.config import Settings, get_settings
from engram.utils.logger import get_logger

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "Settings",
    "get_settings",
    "get_logger",
]
