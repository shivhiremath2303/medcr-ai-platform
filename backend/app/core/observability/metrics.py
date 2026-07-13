import time
from typing import Dict, Optional

from app.domain.repositories.metrics_provider import MetricsProvider


class NoOpMetricsProvider(MetricsProvider):
    """
    Default implementation that does nothing.
    """

    def increment_counter(
        self, name: str, labels: Optional[Dict[str, str]] = None, amount: float = 1.0
    ) -> None:
        pass

    def observe_histogram(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        pass

    def set_gauge(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        pass


class MetricsRegistry:
    """
    Enterprise Metric Registry.
    Standardizes metric names and labels across the platform.
    Implements Milestone 10.2.2.
    """

    def __init__(self, provider: MetricsProvider):
        self.provider = provider

    # --- HTTP & API Metrics ---

    def track_http_request(
        self, method: str, path: str, status_code: int, duration: float
    ):
        self.provider.increment_counter(
            "api_requests_total",
            {"method": method, "path": path, "status": str(status_code)},
        )
        self.provider.observe_histogram(
            "api_request_duration_seconds", duration, {"method": method, "path": path}
        )

    # --- AI & RAG Metrics (10.2.2 & 10.2.7) ---

    def track_llm_call(self, provider: str, model: str, duration: float):
        self.provider.increment_counter(
            "ai_llm_calls_total", {"provider": provider, "model": model}
        )
        self.provider.observe_histogram(
            "ai_llm_latency_seconds",
            duration,
            {"provider": provider, "model": model},
        )

    def track_tokens(self, model: str, input_tokens: int, output_tokens: int):
        self.provider.increment_counter(
            "ai_tokens_consumed_total", {"model": model, "type": "input"}, amount=float(input_tokens)
        )
        self.provider.increment_counter(
            "ai_tokens_consumed_total", {"model": model, "type": "output"}, amount=float(output_tokens)
        )

    def track_ai_cost(self, model: str, cost_usd: float):
        self.provider.increment_counter(
            "ai_cost_usd_total", {"model": model}, amount=cost_usd
        )

    def track_retrieval(self, strategy: str, duration: float, results_count: int = 0):
        self.provider.increment_counter("ai_retrieval_total", {"strategy": strategy})
        self.provider.observe_histogram(
            "ai_retrieval_latency_seconds", duration, {"strategy": strategy}
        )
        self.provider.observe_histogram(
            "ai_retrieval_results_count", float(results_count), {"strategy": strategy}
        )

    def track_reranker(self, model: str, duration: float):
        self.provider.observe_histogram(
            "ai_reranker_latency_seconds", duration, {"model": model}
        )

    def track_evaluation(self, metric: str, score: float):
        """Track scientific AI evaluation scores (grounding, reasoning, etc.)"""
        self.provider.observe_histogram(
            "ai_evaluation_score", score, {"metric": metric}
        )

    def track_hallucination(self, detected: bool):
        status = "detected" if detected else "clean"
        self.provider.increment_counter("ai_hallucinations_total", {"status": status})

    # --- Infrastructure & Persistence ---

    def track_redis_op(self, operation: str, status: str = "success"):
        self.provider.increment_counter(
            "infra_redis_operations_total", {"operation": operation, "status": status}
        )

    def track_cache_hit(self, hit: bool):
        status = "hit" if hit else "miss"
        self.provider.increment_counter("infra_cache_requests_total", {"status": status})

    def track_vector_store_size(self, index_name: str, count: int):
        self.provider.set_gauge(
            "infra_vector_store_documents_total", count, {"index": index_name}
        )

    # --- Business & Operational Metrics (10.2.9) ---

    def track_user_activity(self, action: str, role: str):
        self.provider.increment_counter(
            "business_user_actions_total", {"action": action, "role": role}
        )

    def track_document_processed(self, extension: str, pages: int = 1):
        self.provider.increment_counter(
            "business_documents_processed_total", {"extension": extension}
        )
        self.provider.increment_counter(
            "business_pages_processed_total", {"extension": extension}, amount=float(pages)
        )

    def track_conversation_turn(self, model: str, message_len: int):
        self.provider.increment_counter("business_conversation_turns_total", {"model": model})
        self.provider.observe_histogram("business_message_length_chars", float(message_len), {"model": model})

    def track_pipeline_step(self, step: str, duration: float, status: str = "success"):
        self.provider.increment_counter(
            "infra_pipeline_steps_total", {"step": step, "status": status}
        )
        self.provider.observe_histogram(
            "infra_pipeline_step_duration_seconds", duration, {"step": step}
        )
