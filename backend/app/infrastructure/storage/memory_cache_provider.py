import time
from typing import Any, Optional, Dict
from app.domain.repositories.cache_provider import CacheProvider


class MemoryCacheProvider(CacheProvider):
    """
    In-memory implementation of CacheProvider.
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None

        item = self._cache[key]
        if item["expiry"] and time.time() > item["expiry"]:
            self.delete(key)
            return None

        return item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expiry = time.time() + ttl if ttl else None
        self._cache[key] = {
            "value": value,
            "expiry": expiry
        }

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()
