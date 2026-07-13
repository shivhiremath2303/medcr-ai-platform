from abc import ABC, abstractmethod
from typing import Dict, Optional


class MetricsProvider(ABC):
    """
    Enterprise Interface for tracking application metrics.
    Supports Counters, Histograms, and Gauges.
    """

    @abstractmethod
    def increment_counter(
        self, name: str, labels: Optional[Dict[str, str]] = None, amount: float = 1.0
    ) -> None:
        """Increment a counter metric."""

    @abstractmethod
    def observe_histogram(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Observe a value in a histogram metric."""

    @abstractmethod
    def set_gauge(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Set a gauge metric to a specific value."""
