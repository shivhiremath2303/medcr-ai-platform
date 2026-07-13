import json
import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.domain.models.background_task import BackgroundTask, TaskPriority, TaskStatus
from app.domain.repositories.background_tasks import BackgroundTaskProvider
from app.infrastructure.storage.redis_client import RedisClient
from app.core.observability.metrics import MetricsRegistry

class RedisJobQueueProvider(BackgroundTaskProvider):
    """
    Enterprise Redis-backed Job Queue.
    Supports priority, persistence, and distributed state tracking.
    Implements Milestone 10.3.2.
    """

    def __init__(self, redis_client: RedisClient, metrics: MetricsRegistry):
        self.redis = redis_client
        self.metrics = metrics
        self.key_prefix = "jobs:"
        self.queue_prefix = "queue:"

    def _job_key(self, task_id: str) -> str:
        return f"{self.key_prefix}{task_id}"

    def _queue_key(self, priority: TaskPriority) -> str:
        return f"{self.queue_prefix}{priority.value}"

    async def enqueue(
        self,
        name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.DEFAULT,
        max_retries: int = 3
    ) -> str:
        task_id = str(uuid.uuid4())
        task = BackgroundTask(
            task_id=task_id,
            name=name,
            payload=payload,
            priority=priority,
            max_retries=max_retries
        )

        client = self.redis.client
        # 1. Store task metadata
        client.set(self._job_key(task_id), task.model_dump_json())

        # 2. Push to priority queue (LPUSH for FIFO when using RPOP)
        client.lpush(self._queue_key(priority), task_id)

        self.metrics.increment_counter("jobs_enqueued_total", {"name": name, "priority": priority.value})
        return task_id

    async def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        data = self.redis.client.get(self._job_key(task_id))
        if data:
            return BackgroundTask.model_validate_json(data)
        return None

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ) -> None:
        client = self.redis.client
        data = client.get(self._job_key(task_id))
        if not data:
            return

        task = BackgroundTask.model_validate_json(data)
        task.status = status

        if status == TaskStatus.RUNNING:
            task.started_at = datetime.utcnow()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            task.completed_at = datetime.utcnow()
            task.result = result
            task.error = error

        client.set(self._job_key(task_id), task.model_dump_json())

        if status == TaskStatus.COMPLETED:
            self.metrics.increment_counter("jobs_completed_total", {"name": task.name})
        elif status == TaskStatus.FAILED:
            self.metrics.increment_counter("jobs_failed_total", {"name": task.name})

    async def get_pending_tasks(self, limit: int = 1) -> List[BackgroundTask]:
        """
        Polls queues in priority order.
        Note: In a high-scale production env, this would use BLPOP or a proper worker lib.
        """
        tasks = []
        client = self.redis.client

        # Priority order: HIGH -> DEFAULT -> LOW
        for priority in [TaskPriority.HIGH, TaskPriority.DEFAULT, TaskPriority.LOW]:
            # Atomic RPOP from queue
            task_id = client.rpop(self._queue_key(priority))
            if task_id:
                if isinstance(task_id, bytes):
                    task_id = task_id.decode()

                task = await self.get_task(task_id)
                if task:
                    tasks.append(task)

                if len(tasks) >= limit:
                    break

        return tasks
