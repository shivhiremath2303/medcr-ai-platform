import uuid
from typing import Any, Callable, Dict, List, Optional

from fastapi import BackgroundTasks as FastAPITasks

from app.domain.models.background_task import BackgroundTask, TaskPriority, TaskStatus
from app.domain.repositories.background_tasks import BackgroundTaskProvider


class FastAPIBackgroundTaskProvider(BackgroundTaskProvider):
    """
    Implementation of BackgroundTaskProvider using FastAPI's BackgroundTasks.
    Note: This is intended for use within request cycles as a non-distributed fallback.
    """

    def __init__(self, background_tasks: FastAPITasks):
        self.background_tasks = background_tasks
        self._tasks: Dict[str, BackgroundTask] = {}

    async def enqueue(
        self,
        name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.DEFAULT,
        max_retries: int = 3,
    ) -> str:
        task_id = str(uuid.uuid4())
        task = BackgroundTask(
            task_id=task_id,
            name=name,
            payload=payload,
            priority=priority,
            max_retries=max_retries,
        )
        self._tasks[task_id] = task
        # In this fallback, we don't actually have a worker to poll it,
        # so this is mostly for interface compatibility.
        return task_id

    async def get_task(self, task_id: str) -> BackgroundTask | None:
        return self._tasks.get(task_id)

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Any | None = None,
        error: str | None = None,
    ) -> None:
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = status
            task.result = result
            task.error = error

    async def get_pending_tasks(self, limit: int = 10) -> List[BackgroundTask]:
        return [t for t in self._tasks.values() if t.status == TaskStatus.PENDING][
            :limit
        ]

    def add_task(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.background_tasks.add_task(func, *args, **kwargs)
