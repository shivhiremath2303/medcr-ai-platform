import logging
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

from app.core.observability.metrics import MetricsRegistry
from app.core.observability.telemetry import get_tracer
from app.domain.repositories.cache_provider import CacheProvider

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class MemoryL1Cache:
    """Simple LRU Memory Cache for L1 layer."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, tuple[Any, float]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        value, expiry = self.cache[key]
        if expiry > 0 and time.time() > expiry:
            del self.cache[key]
            return None
        # Move to end (MRU)
        self.cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expiry = (time.time() + ttl) if ttl else 0
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, expiry)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        self.cache.clear()


class MultiLevelCacheProvider(CacheProvider):
    """
    Enterprise Multi-Level Cache Provider.
    L1: Local In-Memory (OrderedDict LRU)
    L2: Distributed Redis
    Implements Milestone 10.3.1.
    """

    def __init__(
        self,
        l2_provider: CacheProvider,
        metrics: MetricsRegistry,
        l1_max_size: int = 1000,
    ):
        self.l2 = l2_provider
        self.l1 = MemoryL1Cache(max_size=l1_max_size)
        self.metrics = metrics

    def get(self, key: str) -> Optional[Any]:
        with tracer.start_as_current_span("cache_get_multi_level") as span:
            span.set_attribute("cache.key", key)

            # 1. Try L1 (Memory)
            val = self.l1.get(key)
            if val is not None:
                self.metrics.track_cache_hit(True)
                span.set_attribute("cache.layer", "L1")
                return val

            # 2. Try L2 (Redis)
            val = self.l2.get(key)
            if val is not None:
                # Populate back to L1 for faster subsequent access
                self.l1.set(key, val, ttl=300)  # Short default for L1 backfill
                self.metrics.track_cache_hit(True)
                span.set_attribute("cache.layer", "L2")
                return val

            self.metrics.track_cache_hit(False)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with tracer.start_as_current_span("cache_set_multi_level") as span:
            span.set_attribute("cache.key", key)
            # Write-through to both layers
            self.l1.set(key, value, ttl=ttl)
            self.l2.set(key, value, ttl=ttl)

    def delete(self, key: str) -> None:
        self.l1.delete(key)
        self.l2.delete(key)

    def clear(self) -> None:
        self.l1.clear()
        self.l2.clear()
