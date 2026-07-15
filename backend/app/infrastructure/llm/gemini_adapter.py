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

from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.resilience import CircuitBreaker
from app.core.observability.telemetry import get_tracer
from app.domain.repositories.llm_provider import LLMProvider

tracer = get_tracer(__name__)


class GeminiLLMAdapter(LLMProvider):
    """
    Adapter for Google Gemini AI with Resilience & Fault Tolerance.
    Implements Milestone 10.3.8 (Retries, Circuit Breaker, Fallbacks).
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
        self.model_name = model_name
        self.metrics = metrics
        self.limiter = limiter
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize Circuit Breaker for this provider
        self.circuit_breaker = CircuitBreaker(
            name=f"llm_gemini_{model_name}",
            failure_threshold=5,
            recovery_timeout=60,
            metrics=metrics,
        )

    # 1. Retry with Exponential Backoff (10.3.8)
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
    ) -> str:
        # 2. Circuit Breaker protection (10.3.8)
        return await self.circuit_breaker.call(
            self._generate_answer_internal, question, context
        )

    async def _generate_answer_internal(self, question: str, context: str) -> str:
        from app.prompts.legal_prompt import LEGAL_RAG_PROMPT

        prompt = LEGAL_RAG_PROMPT.format(
            context=context,
            question=question,
        )

        start_time = time.perf_counter()
        with tracer.start_as_current_span("gemini_generate_answer") as span:
            span.set_attribute("llm.model", self.model_name)

            try:
                # Use bulkhead limiter
                response = await self.limiter.run_in_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=prompt,
                    config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                    },
                )

                duration = time.perf_counter() - start_time
                self.metrics.track_llm_call("google", self.model_name, duration)

                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    usage = response.usage_metadata
                    self.metrics.track_tokens(
                        self.model_name,
                        usage.prompt_token_count or 0,
                        usage.candidates_token_count or 0,
                    )

                return response.text or ""

            except Exception as e:
                span.record_exception(e)
                # In production, we classify errors for the circuit breaker
                raise RuntimeError(f"LLM request failed: {e}") from e

    async def stream_answer(
        self,
        question: str,
        context: str,
    ) -> AsyncGenerator[str, None]:
        """
        Streamed RAG response with basic resilience.
        """
        from app.prompts.legal_prompt import LEGAL_RAG_PROMPT

        prompt = LEGAL_RAG_PROMPT.format(context=context, question=question)

        with tracer.start_as_current_span("gemini_stream_answer") as span:
            try:
                # Streaming is harder to retry mid-stream, so we wrap the connection setup
                response_stream = self.client.aio.models.generate_content_stream(
                    model=self.model_name,
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
                # Fail fast for streaming to maintain UX consistency
                raise

    async def rewrite_question(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        # Rewriting is less critical, so we just use the circuit breaker without aggressive retries
        return await self.circuit_breaker.call(
            self._rewrite_internal, question, conversation_context
        )

    async def _rewrite_internal(self, question: str, conversation_context: str) -> str:
        prompt = f"Rewrite this legal question to be standalone: {question}\nContext: {conversation_context}"
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
