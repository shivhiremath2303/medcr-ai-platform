from abc import ABC, abstractmethod
from typing import Any, Callable


class BackgroundTaskProvider(ABC):
    """
    Interface for scheduling background tasks.
    """

    @abstractmethod
    def add_task(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """Schedule a task to run in the background."""
