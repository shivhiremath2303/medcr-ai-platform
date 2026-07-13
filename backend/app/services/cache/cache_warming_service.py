import logging
from typing import List, Callable, Any
from app.domain.repositories.cache_provider import CacheProvider

logger = logging.getLogger(__name__)

class CacheWarmingService:
    """
    Service for proactive cache population (Milestone 10.3.1).
    Used during startup or background tasks to warm up hot data paths.
    """

    def __init__(self, cache_provider: CacheProvider):
        self.cache = cache_provider

    async def warm_keys(self, keys_and_loaders: List[tuple[str, Callable[[], Any], int]]):
        """
        Warms a list of keys by running their loaders if they are missing.
        """
        for key, loader, ttl in keys_and_loaders:
            if self.cache.get(key) is None:
                try:
                    logger.info(f"Warming cache key: {key}")
                    value = await loader() if callable(loader) else loader
                    self.cache.set(key, value, ttl=ttl)
                except Exception as e:
                    logger.error(f"Failed to warm cache key {key}: {e}")

    def invalidate_pattern(self, pattern: str):
        """
        Invalidates keys matching a pattern.
        Note: Implementation depends on if the L2 provider supports globbing.
        """
        # For simplicity in 10.3.1, we assume explicit invalidation or TTL-based expiry.
        pass
