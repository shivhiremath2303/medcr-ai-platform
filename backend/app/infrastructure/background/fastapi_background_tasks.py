from typing import Any, Callable

from fastapi import BackgroundTasks as FastAPITasks

from app.domain.repositories.background_tasks import BackgroundTaskProvider


class FastAPIBackgroundTaskProvider(BackgroundTaskProvider):
    """
    Implementation of BackgroundTaskProvider using FastAPI's BackgroundTasks.
    Note: This is intended for use within request cycles.
    """

    def __init__(self, background_tasks: FastAPITasks):
        self.background_tasks = background_tasks

    def add_task(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.background_tasks.add_task(func, *args, **kwargs)
