import pickle
from typing import Any, Optional
from app.domain.repositories.cache_provider import CacheProvider
from app.infrastructure.storage.redis_client import RedisClient


class RedisCacheProvider(CacheProvider):
    """
    Redis implementation for general caching.
    Uses pickle for serialization of arbitrary Python objects.
    """

    def __init__(self, redis_client: RedisClient, default_ttl: int = 3600):
        self.redis_wrapper = redis_client
        self.default_ttl = default_ttl
        self.key_prefix = "cache:"

    def get(self, key: str) -> Optional[Any]:
        full_key = f"{self.key_prefix}{key}"
        data = self.redis_wrapper.client.get(full_key)
        if data:
            # Note: Using pickle for internal caching is generally acceptable
            # if the cache source is trusted.
            return pickle.loads(data.encode('latin1') if isinstance(data, str) else data)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        full_key = f"{self.key_prefix}{key}"
        ttl = ttl or self.default_ttl
        pickled_value = pickle.dumps(value)
        self.redis_wrapper.client.setex(full_key, ttl, pickled_value)

    def delete(self, key: str) -> None:
        full_key = f"{self.key_prefix}{key}"
        self.redis_wrapper.client.delete(full_key)

    def clear(self) -> None:
        client = self.redis_wrapper.client
        keys = client.keys(f"{self.key_prefix}*")
        if keys:
            client.delete(*keys)
