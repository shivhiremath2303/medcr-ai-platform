import time
from unittest.mock import MagicMock, patch

import pytest

from app.core.observability.metrics import MetricsRegistry, NoOpMetricsProvider
from app.infrastructure.storage.memory_cache_provider import MemoryCacheProvider
from app.infrastructure.storage.multi_level_cache_provider import (
    MemoryL1Cache,
    MultiLevelCacheProvider,
)
from app.infrastructure.storage.redis_cache_provider import RedisCacheProvider


@pytest.fixture
def metrics():
    return MetricsRegistry(NoOpMetricsProvider())


class TestMemoryCacheProvider:
    def test_set_get(self):
        provider = MemoryCacheProvider()
        provider.set("test_key", "test_value")
        assert provider.get("test_key") == "test_value"

    def test_get_nonexistent(self):
        provider = MemoryCacheProvider()
        assert provider.get("nonexistent") is None

    def test_ttl_expiration(self):
        provider = MemoryCacheProvider()
        # Set with very short TTL
        provider.set("expiring_key", "value", ttl=0.1)
        assert provider.get("expiring_key") == "value"

        # Wait for expiration
        time.sleep(0.2)
        assert provider.get("expiring_key") is None

    def test_delete(self):
        provider = MemoryCacheProvider()
        provider.set("key", "value")
        provider.delete("key")
        assert provider.get("key") is None

    def test_clear(self):
        provider = MemoryCacheProvider()
        provider.set("k1", "v1")
        provider.set("k2", "v2")
        provider.clear()
        assert provider.get("k1") is None
        assert provider.get("k2") is None


class TestRedisCacheProvider:
    @pytest.fixture
    def mock_redis_client(self):
        client = MagicMock()
        wrapper = MagicMock()
        wrapper.client = client
        wrapper.is_available.return_value = True
        return wrapper, client

    def test_set_get_success(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)

        # Mock GET to return pickled value
        import pickle

        test_val = {"data": 123}
        client.get.return_value = pickle.dumps(test_val).decode("latin1")

        val = provider.get("key")
        assert val == test_val
        client.get.assert_called_with("cache:key")

    def test_get_miss(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)
        client.get.return_value = None

        assert provider.get("key") is None

    def test_set_success(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)

        provider.set("key", "value", ttl=100)

        # Verify setex was called with pickled value
        args, _ = client.setex.call_args
        assert args[0] == "cache:key"
        assert args[1] == 100
        import pickle

        assert pickle.loads(args[2]) == "value"  # noqa: S301

    def test_delete_success(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)
        provider.delete("key")
        client.delete.assert_called_with("cache:key")

    def test_delete_unavailable(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        wrapper.is_available.return_value = False
        provider = RedisCacheProvider(wrapper, metrics)
        provider.delete("key")
        client.delete.assert_not_called()

    def test_delete_exception(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)
        client.delete.side_effect = Exception("error")
        provider.delete("key")  # should not raise

    def test_clear_success(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)
        client.keys.return_value = ["cache:k1", "cache:k2"]

        provider.clear()
        client.delete.assert_called_with("cache:k1", "cache:k2")

    def test_clear_empty(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)
        client.keys.return_value = []
        provider.clear()
        client.delete.assert_not_called()

    def test_clear_unavailable(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        wrapper.is_available.return_value = False
        provider = RedisCacheProvider(wrapper, metrics)
        provider.clear()
        client.keys.assert_not_called()

    def test_clear_exception(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)
        client.keys.side_effect = Exception("error")
        provider.clear()  # should not raise

    def test_graceful_degradation_unavailable(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        wrapper.is_available.return_value = False
        provider = RedisCacheProvider(wrapper, metrics)

        # Should return None and not call client.get
        assert provider.get("key") is None
        client.get.assert_not_called()

        # Should return without calling client.setex
        provider.set("key", "value")
        client.setex.assert_not_called()

    def test_graceful_degradation_exception(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        provider = RedisCacheProvider(wrapper, metrics)
        client.get.side_effect = Exception("Redis error")

        # Should handle exception and return None
        assert provider.get("key") is None

        client.setex.side_effect = Exception("Redis error")
        # Should not raise
        provider.set("key", "value")

    def test_metrics_integration(self, mock_redis_client):
        wrapper, client = mock_redis_client
        metrics_mock = MagicMock()
        provider = RedisCacheProvider(wrapper, metrics_mock)

        client.get.return_value = None
        provider.get("key")

        metrics_mock.track_redis_op.assert_called_with("get")
        metrics_mock.track_cache_hit.assert_called_with(False)


class TestMultiLevelCacheProvider:
    @pytest.fixture
    def mock_l2(self):
        return MagicMock()

    def test_l1_hit(self, mock_l2, metrics):
        provider = MultiLevelCacheProvider(mock_l2, metrics)
        provider.l1.set("key", "value")

        val = provider.get("key")
        assert val == "value"
        mock_l2.get.assert_not_called()

    def test_l2_hit_and_backfill(self, mock_l2, metrics):
        provider = MultiLevelCacheProvider(mock_l2, metrics)
        mock_l2.get.return_value = "l2_value"

        # L1 is empty initially
        val = provider.get("key")
        assert val == "l2_value"
        mock_l2.get.assert_called_with("key")

        # Check backfill to L1
        assert provider.l1.get("key") == "l2_value"

    def test_miss_both(self, mock_l2, metrics):
        provider = MultiLevelCacheProvider(mock_l2, metrics)
        mock_l2.get.return_value = None

        assert provider.get("key") is None
        mock_l2.get.assert_called_with("key")

    def test_set_write_through(self, mock_l2, metrics):
        provider = MultiLevelCacheProvider(mock_l2, metrics)
        provider.set("key", "value", ttl=100)

        assert provider.l1.get("key") == "value"
        mock_l2.set.assert_called_with("key", "value", ttl=100)

    def test_delete_both(self, mock_l2, metrics):
        provider = MultiLevelCacheProvider(mock_l2, metrics)
        provider.l1.set("key", "value")
        provider.delete("key")

        assert provider.l1.get("key") is None
        mock_l2.delete.assert_called_with("key")

    def test_delete_nonexistent_l1(self, mock_l2, metrics):
        provider = MultiLevelCacheProvider(mock_l2, metrics)
        provider.delete("key")
        mock_l2.delete.assert_called_with("key")

    def test_set_existing_l1(self, mock_l2, metrics):
        l1 = MemoryL1Cache(max_size=10)
        l1.set("key", "v1")
        l1.set("key", "v2")  # Should trigger move_to_end
        assert l1.get("key") == "v2"

    def test_clear_both(self, mock_l2, metrics):
        provider = MultiLevelCacheProvider(mock_l2, metrics)
        provider.clear()

        mock_l2.clear.assert_called()

    def test_l1_eviction(self, mock_l2, metrics):
        # Test MemoryL1Cache eviction
        l1 = MemoryL1Cache(max_size=2)
        l1.set("k1", "v1")
        l1.set("k2", "v2")
        l1.set("k3", "v3")  # Should evict k1

        assert l1.get("k1") is None
        assert l1.get("k2") == "v2"
        assert l1.get("k3") == "v3"

    def test_l1_ttl(self, mock_l2, metrics):
        l1 = MemoryL1Cache(max_size=10)
        l1.set("k1", "v1", ttl=0.1)
        assert l1.get("k1") == "v1"
        time.sleep(0.2)
        assert l1.get("k1") is None
