import time
from typing import Dict, Optional

from app.core.observability.context import get_tenant_id
from app.domain.repositories.metrics_provider import MetricsProvider


class NoOpMetricsProvider(MetricsProvider):
    """
    Default implementation that does nothing.
    """

    def increment_counter(
        self, name: str, labels: Dict[str, str] | None = None, amount: float = 1.0
    ) -> None:
        pass

    def observe_histogram(
        self, name: str, value: float, labels: Dict[str, str] | None = None
    ) -> None:
        pass

    def set_gauge(
        self, name: str, value: float, labels: Dict[str, str] | None = None
    ) -> None:
        pass


class MetricsRegistry:
    """
    Enterprise Metric Registry.
    Standardizes metric names and labels across the platform.
    Automatically injects tenant_id for multi-tenant observability (10.4.8).
    """

    def __init__(self, provider: MetricsProvider):
        self.provider = provider

    def _inject_tenant(self, labels: Dict[str, str] | None) -> Dict[str, str]:
        labels = labels or {}
        tenant_id = get_tenant_id()
        if tenant_id:
            labels["tenant_id"] = tenant_id
        return labels

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] | None = None):
        """Passthrough to the underlying provider with tenant awareness."""
        self.provider.set_gauge(name, value, self._inject_tenant(labels))

    def increment_counter(
        self, name: str, labels: Dict[str, str] | None = None, amount: float = 1.0
    ):
        """Passthrough to the underlying provider with tenant awareness."""
        self.provider.increment_counter(name, self._inject_tenant(labels), amount)

    def observe_histogram(
        self, name: str, value: float, labels: Dict[str, str] | None = None
    ):
        """Passthrough to the underlying provider with tenant awareness."""
        self.provider.observe_histogram(name, value, self._inject_tenant(labels))

    # --- HTTP & API Metrics ---

    def track_http_request(
        self, method: str, path: str, status_code: int, duration: float
    ):
        labels = {"method": method, "path": path, "status": str(status_code)}
        self.increment_counter("api_requests_total", labels)
        self.observe_histogram("api_request_duration_seconds", duration, labels)

    # --- AI & RAG Metrics (10.2.2 & 10.2.7) ---

    def track_llm_call(self, provider: str, model: str, duration: float):
        labels = {"provider": provider, "model": model}
        self.increment_counter("ai_llm_calls_total", labels)
        self.observe_histogram("ai_llm_latency_seconds", duration, labels)

    def track_tokens(self, model: str, input_tokens: int, output_tokens: int):
        self.increment_counter(
            "ai_tokens_consumed_total",
            {"model": model, "type": "input"},
            amount=float(input_tokens),
        )
        self.increment_counter(
            "ai_tokens_consumed_total",
            {"model": model, "type": "output"},
            amount=float(output_tokens),
        )

    def track_ai_cost(self, model: str, cost_usd: float):
        self.increment_counter("ai_cost_usd_total", {"model": model}, amount=cost_usd)

    def track_retrieval(self, strategy: str, duration: float, results_count: int = 0):
        labels = {"strategy": strategy}
        self.increment_counter("ai_retrieval_total", labels)
        self.observe_histogram("ai_retrieval_latency_seconds", duration, labels)
        self.observe_histogram(
            "ai_retrieval_results_count", float(results_count), labels
        )

    def track_reranker(self, model: str, duration: float):
        self.observe_histogram(
            "ai_reranker_latency_seconds", duration, {"model": model}
        )

    def track_evaluation(self, metric: str, score: float):
        """Track scientific AI evaluation scores (grounding, reasoning, etc.)"""
        self.observe_histogram("ai_evaluation_score", score, {"metric": metric})

    def track_hallucination(self, detected: bool):
        status = "detected" if detected else "clean"
        self.increment_counter("ai_hallucinations_total", {"status": status})

    # --- Infrastructure & Persistence ---

    def track_redis_op(self, operation: str, status: str = "success"):
        self.increment_counter(
            "infra_redis_operations_total", {"operation": operation, "status": status}
        )

    def track_cache_hit(self, hit: bool):
        status = "hit" if hit else "miss"
        self.increment_counter("infra_cache_requests_total", {"status": status})

    def track_vector_store_size(self, index_name: str, count: int):
        self.set_gauge(
            "infra_vector_store_documents_total", count, {"index": index_name}
        )

    # --- Business & Operational Metrics (10.2.9) ---

    def track_user_activity(self, action: str, role: str):
        self.increment_counter(
            "business_user_actions_total", {"action": action, "role": role}
        )

    def track_document_processed(self, extension: str, pages: int = 1):
        labels = {"extension": extension}
        self.increment_counter("business_documents_processed_total", labels)
        self.increment_counter(
            "business_pages_processed_total",
            labels,
            amount=float(pages),
        )

    def track_conversation_turn(self, model: str, message_len: int):
        labels = {"model": model}
        self.increment_counter("business_conversation_turns_total", labels)
        self.observe_histogram(
            "business_message_length_chars", float(message_len), labels
        )

    def track_pipeline_step(self, step: str, duration: float, status: str = "success"):
        labels = {"step": step, "status": status}
        self.increment_counter("infra_pipeline_steps_total", labels)
        self.observe_histogram("infra_pipeline_step_duration_seconds", duration, labels)
