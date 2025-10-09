"""Base connector class for external data sources."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from engram.utils.logger import get_logger

logger = get_logger(__name__)


class BaseConnector(ABC):
    """Base class for all data source connectors."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize connector with configuration.
        
        Args:
            config: Connector configuration
        """
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the data source.
        
        Returns:
            True if authentication successful
        """
        pass

    @abstractmethod
    async def list_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List available items from the data source.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of item metadata
        """
        pass

    @abstractmethod
    async def fetch_item(self, item_id: str) -> Dict[str, Any]:
        """Fetch a specific item from the data source.
        
        Args:
            item_id: Item identifier
            
        Returns:
            Item data
        """
        pass

    @abstractmethod
    async def get_last_sync_time(self) -> Optional[datetime]:
        """Get the last synchronization time.
        
        Returns:
            Last sync timestamp or None
        """
        pass

    @abstractmethod
    async def update_sync_time(self, timestamp: datetime) -> None:
        """Update the last synchronization time.
        
        Args:
            timestamp: Sync timestamp
        """
        pass

    def validate_config(self, required_fields: List[str]) -> bool:
        """Validate connector configuration.
        
        Args:
            required_fields: List of required configuration fields
            
        Returns:
            True if configuration is valid
        """
        for field in required_fields:
            if field not in self.config:
                logger.error(f"Missing required config field: {field}")
                return False
        return True
