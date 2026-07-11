from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheProvider(ABC):
    """
    Interface for general purpose caching.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in the cache with an optional TTL."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a value from the cache."""

    @abstractmethod
    def clear(self) -> None:
        """Clear the entire cache."""
