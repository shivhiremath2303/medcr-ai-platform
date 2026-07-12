import pickle
from typing import Any, Optional
from app.domain.repositories.cache_provider import CacheProvider
from app.infrastructure.storage.redis_client import RedisClient
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.telemetry import get_tracer

tracer = get_tracer(__name__)

class RedisCacheProvider(CacheProvider):
    """
    Redis implementation for general caching.
    Uses pickle for serialization of arbitrary Python objects.
    """

    def __init__(self, redis_client: RedisClient, metrics: MetricsRegistry, default_ttl: int = 3600):
        self.redis_wrapper = redis_client
        self.metrics = metrics
        self.default_ttl = default_ttl
        self.key_prefix = "cache:"

    def get(self, key: str) -> Optional[Any]:
        full_key = f"{self.key_prefix}{key}"
        with tracer.start_as_current_span("redis_cache_get") as span:
            span.set_attribute("cache.key", full_key)
            try:
                data = self.redis_wrapper.client.get(full_key)
                self.metrics.track_redis_op("get")
                self.metrics.track_cache_hit(data is not None)

                if data:
                    return pickle.loads(data.encode('latin1') if isinstance(data, str) else data)
                return None
            except Exception as e:
                span.record_exception(e)
                self.metrics.track_redis_op("get", status="error")
                return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        full_key = f"{self.key_prefix}{key}"
        ttl = ttl or self.default_ttl
        pickled_value = pickle.dumps(value)
        with tracer.start_as_current_span("redis_cache_set") as span:
            span.set_attribute("cache.key", full_key)
            try:
                self.redis_wrapper.client.setex(full_key, ttl, pickled_value)
                self.metrics.track_redis_op("set")
            except Exception as e:
                span.record_exception(e)
                self.metrics.track_redis_op("set", status="error")

    def delete(self, key: str) -> None:
        full_key = f"{self.key_prefix}{key}"
        with tracer.start_as_current_span("redis_cache_delete") as span:
            span.set_attribute("cache.key", full_key)
            try:
                self.redis_wrapper.client.delete(full_key)
                self.metrics.track_redis_op("delete")
            except Exception as e:
                span.record_exception(e)
                self.metrics.track_redis_op("delete", status="error")

    def clear(self) -> None:
        client = self.redis_wrapper.client
        keys = client.keys(f"{self.key_prefix}*")
        if keys:
            client.delete(*keys)
