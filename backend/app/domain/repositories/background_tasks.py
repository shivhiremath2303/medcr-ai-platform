from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from app.domain.models.background_task import BackgroundTask, TaskPriority, TaskStatus


class BackgroundTaskProvider(ABC):
    """
    Enterprise Interface for Distributed Background Processing (Milestone 10.3.2).
    """

    @abstractmethod
    async def enqueue(
        self,
        name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.DEFAULT,
        max_retries: int = 3,
    ) -> str:
        """Enqueue a task for distributed execution."""

    @abstractmethod
    async def get_task(self, task_id: str) -> BackgroundTask | None:
        """Retrieve task status and metadata."""

    @abstractmethod
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Any | None = None,
        error: str | None = None,
    ) -> None:
        """Update the state of a running task."""

    @abstractmethod
    async def get_pending_tasks(self, limit: int = 10) -> List[BackgroundTask]:
        """Fetch tasks waiting for execution (used by workers)."""
