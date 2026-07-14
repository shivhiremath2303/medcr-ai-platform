import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.health import HealthCheck, HealthService
from app.core.observability.metrics import MetricsRegistry, NoOpMetricsProvider
from app.core.observability.resilience import CircuitBreaker, CircuitState
from app.core.observability.resource_guard import ResourceGuard
from app.domain.models.audit import AuditEventType
from app.domain.models.background_task import BackgroundTask, TaskPriority, TaskStatus
from app.infrastructure.background.redis_job_queue import RedisJobQueueProvider
from app.infrastructure.storage.multi_level_cache_provider import (
    MultiLevelCacheProvider,
)
from app.services.audit.audit_service import AuditService
from app.services.background.worker_service import WorkerService


@pytest.fixture
def metrics():
    return MetricsRegistry(NoOpMetricsProvider())


def test_resource_guard_monitors_memory(metrics):
    guard = ResourceGuard(metrics, memory_limit_mb=100.0, pressure_threshold=0.5)
    usage = guard.get_current_usage_mb()
    assert usage >= 0
    is_pressed = guard.is_under_pressure()
    assert isinstance(is_pressed, bool)


@pytest.mark.asyncio
async def test_concurrency_limiter_executes_tasks(metrics):
    guard = ResourceGuard(metrics)
    limiter = ConcurrencyLimiter(guard, max_concurrent_tasks=2, max_workers=2)

    async def sample_task(x):
        await asyncio.sleep(0.01)
        return x * 2

    result = await limiter.run_async(sample_task, 5)
    assert result == 10

    def sync_task(x):
        return x + 1

    result_sync = await limiter.run_in_thread(sync_task, 10)
    assert result_sync == 11


@pytest.mark.asyncio
async def test_circuit_breaker_trips_on_failure(metrics):
    breaker = CircuitBreaker(
        "test", failure_threshold=2, recovery_timeout=1, metrics=metrics
    )

    async def failing_func():
        raise ValueError("Fail")

    with pytest.raises(ValueError):
        await breaker.call(failing_func)
    assert breaker.state == CircuitState.CLOSED

    with pytest.raises(ValueError):
        await breaker.call(failing_func)
    assert breaker.state == CircuitState.OPEN

    with pytest.raises(RuntimeError, match="OPEN"):
        await breaker.call(failing_func)


@pytest.mark.asyncio
async def test_multi_level_cache_logic(metrics):
    l2 = MagicMock()
    l2.get.return_value = None

    provider = MultiLevelCacheProvider(l2, metrics)
    provider.set("key", "value", ttl=60)
    assert provider.get("key") == "value"
    l2.get.assert_not_called()

    provider.clear()
    assert provider.get("key") is None


@pytest.mark.asyncio
async def test_redis_job_queue_enqueue(metrics):
    redis_mock = MagicMock()
    # Mock redis client methods
    redis_mock.client.set = MagicMock()
    redis_mock.client.lpush = MagicMock()

    queue = RedisJobQueueProvider(redis_mock, metrics)
    task_id = await queue.enqueue("test_job", {"data": 1}, priority=TaskPriority.HIGH)

    assert task_id is not None
    assert redis_mock.client.set.called
    assert redis_mock.client.lpush.called


@pytest.mark.asyncio
async def test_worker_service_execution(metrics):
    task_provider = AsyncMock()
    guard = ResourceGuard(metrics)
    worker = WorkerService(task_provider, metrics, guard)

    task = BackgroundTask(task_id="t1", name="job1", payload={"x": 1})
    task_provider.get_pending_tasks.return_value = [task]

    handler = AsyncMock(return_value="done")
    worker.register_handler("job1", handler)

    # Run one iteration manually
    await worker._execute_task(task)

    handler.assert_called_once_with(x=1)
    task_provider.update_task_status.assert_any_call("t1", TaskStatus.RUNNING)
    task_provider.update_task_status.assert_any_call(
        "t1", TaskStatus.COMPLETED, result="done"
    )


def test_audit_service_logs_events():
    with patch("app.services.audit.audit_service.logger") as mock_logger:
        service = AuditService()
        service.log(AuditEventType.AI_QUERY, "test_action", details={"meta": 1})

        assert mock_logger.log.called
        args, kwargs = mock_logger.log.call_args
        assert "Audit Event" in kwargs["msg"]
        assert kwargs["extra"]["extra_data"]["is_audit_event"] is True


@pytest.mark.asyncio
async def test_health_service_aggregates_checks():
    service = HealthService("1.0", "test")

    class MockCheck(HealthCheck):
        @property
        def name(self):
            return "mock"

        async def check(self):
            return {"status": "up"}

    service.add_readiness_check(MockCheck())
    report = await service.get_readiness()

    assert report["status"] == "up"
    assert "mock" in report["checks"]
