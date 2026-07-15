import asyncio
import time
from typing import AsyncGenerator, Optional

from google import genai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings
from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.resilience import CircuitBreaker
from app.core.observability.telemetry import get_tracer
from app.domain.repositories.llm_provider import LLMProvider

tracer = get_tracer(__name__)
settings = get_settings()


class GeminiLLMAdapter(LLMProvider):
    """
    Adapter for Google Gemini AI with Resilience, Fault Tolerance, and Model Routing.
    Implements Milestone 10.5.4 (Dynamic Model Routing).
    """

    def __init__(
        self,
        client: genai.Client,
        model_name: str,
        metrics: MetricsRegistry,
        limiter: ConcurrencyLimiter,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ):
        self.client = client
        self.model_name = model_name  # This is the flash/primary model
        self.metrics = metrics
        self.limiter = limiter
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Circuit Breakers for both model tiers
        self.circuit_breaker_flash = CircuitBreaker(
            name=f"llm_gemini_{model_name}",
            failure_threshold=5,
            recovery_timeout=60,
            metrics=metrics,
        )
        self.circuit_breaker_pro = CircuitBreaker(
            name=f"llm_gemini_{settings.gemini_pro_model}",
            failure_threshold=5,
            recovery_timeout=60,
            metrics=metrics,
        )

    def _select_model(self, complexity_hint: str | None = None) -> tuple[str, CircuitBreaker]:
        """
        Dynamically route queries based on their complexity (10.5.4).
        Heavy legal comparisons or multi-doc queries are routed to Pro,
        while general QA or lookups use the faster Flash model.
        """
        if complexity_hint in ["comparison", "summary", "timeline"]:
            return settings.gemini_pro_model, self.circuit_breaker_pro
        return self.model_name, self.circuit_breaker_flash

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, RuntimeError)),
        reraise=True,
    )
    async def generate_answer(
        self,
        question: str,
        context: str,
        complexity_hint: str | None = None,
    ) -> str:
        """Generate answer with dynamic model routing."""
        model, breaker = self._select_model(complexity_hint)
        return await breaker.call(
            self._generate_answer_internal, question, context, model
        )

    async def _generate_answer_internal(self, question: str, context: str, model: str) -> str:
        from app.prompts.legal_prompt import LEGAL_RAG_PROMPT

        prompt = LEGAL_RAG_PROMPT.format(
            context=context,
            question=question,
        )

        start_time = time.perf_counter()
        with tracer.start_as_current_span("gemini_generate_answer") as span:
            span.set_attribute("llm.model", model)

            try:
                # Use bulkhead limiter to protect downstream APIs
                response = await self.limiter.run_in_thread(
                    self.client.models.generate_content,
                    model=model,
                    contents=prompt,
                    config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                    },
                )

                duration = time.perf_counter() - start_time
                self.metrics.track_llm_call("google", model, duration)

                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    usage = response.usage_metadata
                    self.metrics.track_tokens(
                        model,
                        usage.prompt_token_count or 0,
                        usage.candidates_token_count or 0,
                    )

                return response.text or ""

            except Exception as e:
                span.record_exception(e)
                raise RuntimeError(f"LLM request failed for model {model}: {e}") from e

    async def stream_answer(
        self,
        question: str,
        context: str,
        complexity_hint: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Streamed RAG response with dynamic model routing.
        """
        from app.prompts.legal_prompt import LEGAL_RAG_PROMPT

        prompt = LEGAL_RAG_PROMPT.format(context=context, question=question)
        model, _ = self._select_model(complexity_hint)

        with tracer.start_as_current_span("gemini_stream_answer") as span:
            span.set_attribute("llm.model", model)
            try:
                response_stream = self.client.aio.models.generate_content_stream(
                    model=model,
                    contents=prompt,
                    config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                    },
                )
                async for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                span.record_exception(e)
                raise

    async def rewrite_question(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        # Rewriting uses the default primary model (Flash) for speed
        return await self.circuit_breaker_flash.call(
            self._rewrite_internal, question, conversation_context
        )

    async def _rewrite_internal(self, question: str, conversation_context: str) -> str:
        prompt = f"Rewrite this standalone legal question: {question}\nContext: {conversation_context}"
        try:
            response = await self.limiter.run_in_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config={"temperature": 0.0},
            )
            return response.text.strip() if response.text else question
        except Exception:
            return question
