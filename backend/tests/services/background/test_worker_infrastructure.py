import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, UTC

from app.services.background.worker_service import WorkerService
from app.infrastructure.background.redis_job_queue import RedisJobQueueProvider
from app.domain.models.background_task import BackgroundTask, TaskStatus, TaskPriority
from app.core.observability.metrics import MetricsRegistry, NoOpMetricsProvider
from app.core.observability.resource_guard import ResourceGuard

@pytest.fixture
def metrics():
    return MetricsRegistry(NoOpMetricsProvider())

@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    return provider

@pytest.fixture
def mock_guard():
    guard = MagicMock(spec=ResourceGuard)
    guard.is_under_pressure.return_value = False
    guard.should_reject_task.return_value = False
    return guard

class TestWorkerService:
    @pytest.mark.asyncio
    async def test_worker_loop_execution(self, mock_provider, metrics, mock_guard):
        worker = WorkerService(mock_provider, metrics, mock_guard)

        task = BackgroundTask(task_id="t1", name="test_job", payload={"x": 1})
        # Return task once, then empty to avoid infinite flooding
        mock_provider.get_pending_tasks.side_effect = [[task], []]

        handler = AsyncMock(return_value="done")
        worker.register_handler("test_job", handler)

        # Start worker and stop it after a short delay
        task_loop = asyncio.create_task(worker.start(polling_interval=0.01))
        await asyncio.sleep(0.1)
        await worker.stop()
        try:
            await asyncio.wait_for(task_loop, timeout=1.0)
        except asyncio.TimeoutError:
            pass

        handler.assert_called_with(x=1)
        mock_provider.update_task_status.assert_any_call("t1", TaskStatus.RUNNING)
        mock_provider.update_task_status.assert_any_call("t1", TaskStatus.COMPLETED, result="done")

    @pytest.mark.asyncio
    async def test_worker_resource_pressure_throttling(self, mock_provider, metrics, mock_guard):
        mock_guard.is_under_pressure.return_value = True
        worker = WorkerService(mock_provider, metrics, mock_guard)
        mock_provider.get_pending_tasks.return_value = []

        task_loop = asyncio.create_task(worker.start(polling_interval=0.01))
        await asyncio.sleep(0.1)
        await worker.stop()
        await task_loop

        # Throttled interval is polling_interval * 5 = 0.05.
        # In 0.1s, it should run roughly 2 times.
        assert mock_provider.get_pending_tasks.call_count <= 3

    @pytest.mark.asyncio
    async def test_worker_load_shedding(self, mock_provider, metrics, mock_guard):
        mock_guard.should_reject_task.return_value = True
        worker = WorkerService(mock_provider, metrics, mock_guard)

        task = BackgroundTask(task_id="shed_me", name="job", priority=TaskPriority.LOW)
        mock_provider.get_pending_tasks.side_effect = [[task], []]

        task_loop = asyncio.create_task(worker.start(polling_interval=0.01))
        await asyncio.sleep(0.1)
        await worker.stop()
        await task_loop

        mock_provider.update_task_status.assert_called_with(
            "shed_me", TaskStatus.FAILED, error="Dropped due to system resource pressure"
        )

    @pytest.mark.asyncio
    async def test_handler_not_found(self, mock_provider, metrics, mock_guard):
        worker = WorkerService(mock_provider, metrics, mock_guard)
        task = BackgroundTask(task_id="t1", name="unknown_job")
        mock_provider.get_pending_tasks.side_effect = [[task], []]

        task_loop = asyncio.create_task(worker.start(polling_interval=0.01))
        await asyncio.sleep(0.1)
        await worker.stop()
        await task_loop

        mock_provider.update_task_status.assert_called_with(
            "t1", TaskStatus.FAILED, error="No handler registered for task: unknown_job"
        )

    @pytest.mark.asyncio
    async def test_sync_handler_execution(self, mock_provider, metrics, mock_guard):
        worker = WorkerService(mock_provider, metrics, mock_guard)
        task = BackgroundTask(task_id="t2", name="sync_job", payload={"v": 10})
        mock_provider.get_pending_tasks.side_effect = [[task], []]

        def sync_handler(v):
            return v * 2

        worker.register_handler("sync_job", sync_handler)

        task_loop = asyncio.create_task(worker.start(polling_interval=0.01))
        await asyncio.sleep(0.1)
        await worker.stop()
        await task_loop

        mock_provider.update_task_status.assert_any_call("t2", TaskStatus.COMPLETED, result=20)

class TestRedisJobQueueProvider:
    @pytest.fixture
    def mock_redis_client(self):
        client = MagicMock()
        wrapper = MagicMock()
        wrapper.client = client
        return wrapper, client

    @pytest.mark.asyncio
    async def test_enqueue(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        queue = RedisJobQueueProvider(wrapper, metrics)

        task_id = await queue.enqueue("test_task", {"a": 1}, priority=TaskPriority.HIGH)

        assert task_id is not None
        # Verify stored in Redis
        client.set.assert_called()
        client.lpush.assert_called_with("queue:high", task_id)

    @pytest.mark.asyncio
    async def test_get_pending_tasks_priority_order(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        queue = RedisJobQueueProvider(wrapper, metrics)

        # Priority order: HIGH -> DEFAULT -> LOW
        # We want to test that it checks high first.
        client.rpop.side_effect = ["h1", "d1", "l1"]

        async def mock_get_task(tid):
            return BackgroundTask(task_id=tid, name=f"name_{tid}")

        with patch.object(queue, "get_task", side_effect=mock_get_task):
            tasks = await queue.get_pending_tasks(limit=2)

            assert len(tasks) == 2
            assert tasks[0].task_id == "h1"
            assert tasks[1].task_id == "d1"
            # Verify rpop called for high and default
            assert client.rpop.call_count == 2
            client.rpop.assert_any_call("queue:high")
            client.rpop.assert_any_call("queue:default")

    @pytest.mark.asyncio
    async def test_update_task_status(self, mock_redis_client, metrics):
        wrapper, client = mock_redis_client
        queue = RedisJobQueueProvider(wrapper, metrics)

        task = BackgroundTask(task_id="t1", name="task1")
        client.get.return_value = task.model_dump_json()

        await queue.update_task_status("t1", TaskStatus.COMPLETED, result="ok")

        # Verify Redis SET called with updated status
        args, _ = client.set.call_args
        updated_task = BackgroundTask.model_validate_json(args[1])
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.result == "ok"
        assert updated_task.completed_at is not None

class TestBackgroundTaskModel:
    def test_model_serialization(self):
        task = BackgroundTask(
            task_id="123",
            name="test",
            priority=TaskPriority.HIGH,
            payload={"key": "value"}
        )
        json_data = task.model_dump_json()
        restored = BackgroundTask.model_validate_json(json_data)

        assert restored.task_id == "123"
        assert restored.priority == TaskPriority.HIGH
        assert restored.payload == {"key": "value"}
        assert restored.status == TaskStatus.PENDING
