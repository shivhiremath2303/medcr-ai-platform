from typing import Any, Dict, Optional

from prometheus_client import REGISTRY, CollectorRegistry, Counter, Gauge, Histogram

from app.domain.repositories.metrics_provider import MetricsProvider


class PrometheusMetricsProvider(MetricsProvider):
    """
    Enterprise Prometheus implementation of the MetricsProvider.
    Implements Milestone 10.2.2.
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        # Use the global registry by default if none provided
        self.registry = registry if registry is not None else REGISTRY
        self.metrics: Dict[str, Any] = {}

    def _get_or_create_metric(
        self, metric_type: type, name: str, labels: Optional[Dict[str, str]] = None
    ) -> Any:
        if name not in self.metrics:
            label_names = list(labels.keys()) if labels else []
            description = f"Prometheus {metric_type.__name__} for {name}"

            # Create metric with proper registry
            self.metrics[name] = metric_type(
                name,
                description,
                labelnames=label_names,
                registry=self.registry,
            )
        return self.metrics[name]

    def increment_counter(
        self, name: str, labels: Optional[Dict[str, str]] = None, amount: float = 1.0
    ) -> None:
        counter = self._get_or_create_metric(Counter, name, labels)
        if labels:
            counter.labels(**labels).inc(amount)
        else:
            counter.inc(amount)

    def observe_histogram(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        histogram = self._get_or_create_metric(Histogram, name, labels)
        if labels:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)

    def set_gauge(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        gauge = self._get_or_create_metric(Gauge, name, labels)
        if labels:
            gauge.labels(**labels).set(value)
        else:
            gauge.set(value)
