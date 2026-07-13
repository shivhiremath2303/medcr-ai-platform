import asyncio
import hashlib
import json
import re
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.core.observability.cache_policy import CacheTTL
from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.logger import get_logger
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.profiler import PerformanceProfiler
from app.core.observability.telemetry import get_tracer
from app.domain.repositories.benchmark_repository import BenchmarkRepository
from app.domain.repositories.cache_provider import CacheProvider
from app.domain.repositories.context_builder import ContextBuilder
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.query_rewriter import QueryRewriter
from app.domain.repositories.retriever import Retriever
from app.services.rag.evaluation_engine import EvaluationEngine
from app.services.rag.grounding_engine import GroundingEngine
from app.services.rag.reasoning_engine import ReasoningEngine

logger = get_logger(__name__)
tracer = get_tracer(__name__)


class RAGService:
    """
    Coordinates the advanced Retrieval-Augmented Generation workflow with scientific evaluation.
    Integrated with Enterprise AI Observability, Distributed Caching, and API Scaling (Milestone 10.3.7).
    """

    def __init__(
        self,
        retrieval_service: Retriever,
        llm_provider: LLMProvider,
        query_rewriter: QueryRewriter,
        memory: ConversationRepository,
        context_builder: ContextBuilder,
        grounding_engine: GroundingEngine,
        reasoning_engine: ReasoningEngine,
        evaluation_engine: EvaluationEngine,
        benchmark_repo: BenchmarkRepository,
        metrics: MetricsRegistry,
        cache: CacheProvider,
        limiter: ConcurrencyLimiter,
    ):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.query_rewriter = query_rewriter
        self.memory = memory
        self.context_builder = context_builder
        self.grounding_engine = grounding_engine
        self.reasoning_engine = reasoning_engine
        self.evaluation_engine = evaluation_engine
        self.benchmark_repo = benchmark_repo
        self.metrics = metrics
        self.cache = cache
        self.limiter = limiter

    @PerformanceProfiler.profile_function(
        name="rag_answer_question", slow_threshold_ms=8000
    )
    async def answer_question(
        self, question: str, k: int = 3, enable_evaluation: bool = True
    ) -> dict:
        """
        Retrieve context, generate an answer, and perform scientific evaluation.
        """
        overall_start = time.perf_counter()
        with tracer.start_as_current_span("rag_workflow") as span:
            span.set_attribute("rag.question", question)

            # 1. Distributed Caching Check
            memory_context = self.memory.get_context()
            context_hash = self._generate_cache_key(
                "answer", question, memory_context, k
            )

            cached_answer = self.cache.get(context_hash)
            if cached_answer:
                logger.info("Serving RAG answer from distributed cache.")
                span.set_attribute("rag.cache_hit", True)
                return cached_answer

            # 2. Sequential Phase: Understanding -> Retrieval
            self.memory.add_user_message(question)

            with tracer.start_as_current_span("query_rewriting"):
                understanding = await self.query_rewriter.understand_query(
                    question=question,
                    conversation_context=memory_context,
                )

            retrieval_cache_key = self._generate_cache_key(
                "retrieval", understanding.original_query, k
            )
            results = self.cache.get(retrieval_cache_key)

            retrieval_ms = 0
            if results:
                logger.info("Serving retrieval results from cache.")
                span.set_attribute("retrieval.cache_hit", True)
            else:
                retrieval_start = time.perf_counter()
                with tracer.start_as_current_span("retrieval"):
                    results = await self.retrieval_service.retrieve(
                        query=understanding.original_query,
                        k=k,
                        params={"understanding": understanding},
                    )
                retrieval_ms = (time.perf_counter() - retrieval_start) * 1000
                self.cache.set(retrieval_cache_key, results, ttl=CacheTTL.MEDIUM)

            raw_confidence = sum(r.score for r in results[:1]) if results else 0.0
            sufficiency = self.grounding_engine.analyze_sufficiency(
                results, raw_confidence
            )

            if not results or sufficiency == "insufficient":
                return self._generate_insufficient_response()

            evidence_list = self.context_builder.results_to_evidence(results)
            context = self.context_builder.build(results)

            # 3. LLM Generation
            llm_start = time.perf_counter()
            try:
                answer = await self.llm_provider.generate_answer(
                    question=question,
                    context=context,
                )
            except Exception as e:
                # 10.3.8: Graceful Degradation / Fallback
                logger.error(
                    f"AI Generation failed. Serving fallback response. Error: {e}"
                )
                span.set_status(tracer.Status(tracer.StatusCode.ERROR, str(e)))
                return self._generate_fallback_response(e)

            llm_ms = (time.perf_counter() - llm_start) * 1000
            self.metrics.track_pipeline_step("llm_generation", llm_ms / 1000)
            self.memory.add_assistant_message(answer)

            # 4. Parallel Analytics Phase
            with tracer.start_as_current_span("parallel_analytics"):
                grounding_task = self.limiter.run_async(
                    self._process_grounding, answer, evidence_list, sufficiency
                )
                reasoning_task = self.limiter.run_async(
                    self._process_reasoning, answer, evidence_list
                )
                grounding_data, reasoning_metadata = await asyncio.gather(
                    grounding_task, reasoning_task
                )

            # 5. Scientific Evaluation
            eval_report = None
            if enable_evaluation:
                eval_report = await self._process_scientific_evaluation(
                    question,
                    results,
                    answer,
                    evidence_list,
                    grounding_data["score"],
                    reasoning_metadata,
                    retrieval_ms,
                    overall_start,
                    context,
                )

            # 6. Build Response
            response_data = self._build_response(
                answer,
                grounding_data,
                reasoning_metadata,
                evidence_list,
                raw_confidence,
                eval_report,
                getattr(self.retrieval_service, "last_diagnostics", None),
            )

            # Cache the result
            self.cache.set(context_hash, response_data, ttl=CacheTTL.SHORT)
            return response_data

    async def stream_answer(
        self, question: str, k: int = 3
    ) -> AsyncGenerator[str, None]:
        """
        Streamed RAG response for API Scalability (10.3.7).
        Yields partial text chunks.
        """
        memory_context = self.memory.get_context()

        # Note: Understanding and Retrieval are still sequential (they are the context needed for LLM)
        understanding = await self.query_rewriter.understand_query(
            question=question,
            conversation_context=memory_context,
        )

        results = await self.retrieval_service.retrieve(
            query=understanding.original_query,
            k=k,
            params={"understanding": understanding},
        )

        context = self.context_builder.build(results)

        # Stream from provider
        full_answer = ""
        async for chunk in self.llm_provider.stream_answer(question, context):
            full_answer += chunk
            yield chunk

        # Post-streaming: background tasks for memory and analytics
        self.memory.add_user_message(question)
        self.memory.add_assistant_message(full_answer)

    async def _process_grounding(
        self, answer: str, evidence_list: List, sufficiency: Any
    ) -> Dict:
        validation_errors = self.grounding_engine.validate_answer(answer, evidence_list)
        contradictions = self.grounding_engine.detect_contradictions(answer)
        missing_docs = self.grounding_engine.detect_missing_evidence(answer)

        self.metrics.track_hallucination(
            detected=bool(contradictions or validation_errors)
        )

        score = self.grounding_engine.calculate_grounding_score(
            evidence_list=evidence_list,
            citations=self._extract_citations(answer),
            sufficiency=sufficiency,
            contradictions=contradictions,
        )
        self.metrics.track_evaluation("grounding", score)

        status = self.grounding_engine.determine_status(
            answer=answer,
            sufficiency=sufficiency,
            grounding_score=score,
            contradictions=contradictions,
        )

        return {
            "score": score,
            "status": status,
            "errors": validation_errors,
            "contradictions": contradictions,
            "missing": missing_docs,
            "summary": self._extract_summary(answer),
        }

    async def _process_reasoning(self, answer: str, evidence_list: List) -> Any:
        return self.reasoning_engine.extract_reasoning(answer, evidence_list)

    async def _process_scientific_evaluation(
        self,
        query,
        results,
        answer,
        evidence_list,
        grounding_score,
        reasoning_metadata,
        retrieval_ms,
        overall_start,
        context,
    ) -> Any:
        expected_ids = []
        for case in self.benchmark_repo.get_all_cases():
            if case.query.lower() in query.lower():
                expected_ids = case.expected_evidence_ids
                break

        retrieval_metrics = self.evaluation_engine.evaluate_retrieval(
            results, expected_ids
        )
        grounding_metrics = self.evaluation_engine.evaluate_grounding(
            answer, evidence_list, grounding_score
        )
        reasoning_metrics = self.evaluation_engine.evaluate_reasoning(
            reasoning_metadata
        )

        performance_metrics = self.evaluation_engine.evaluate_performance(
            retrieval_ms=retrieval_ms,
            total_ms=(time.perf_counter() - overall_start) * 1000,
            tokens_in=len(context) // 4,
            tokens_out=len(answer) // 4,
        )

        return self.evaluation_engine.generate_report(
            query=query,
            retrieval=retrieval_metrics,
            grounding=grounding_metrics,
            reasoning=reasoning_metrics,
            performance=performance_metrics,
        )

    def _build_response(
        self,
        answer,
        grounding,
        reasoning,
        evidence_list,
        confidence,
        eval_report,
        diagnostics,
    ) -> Dict:
        sources = [
            {"filename": ev.document_name, "page_number": ev.page_number}
            for ev in evidence_list
        ]

        response = {
            "answer": answer,
            "summary": grounding["summary"],
            "citations": self._extract_citations(answer),
            "evidence": evidence_list,
            "confidence": confidence,
            "grounding_score": grounding["score"],
            "answer_status": grounding["status"].value,
            "missing_documents": grounding["missing"],
            "contradictions": grounding["contradictions"],
            "reasoning_notes": (
                f"Errors: {', '.join(grounding['errors'])}"
                if grounding["errors"]
                else None
            ),
            "reasoning_metadata": reasoning.__dict__,
            "sources": sources,
        }

        if eval_report:
            response["evaluation"] = {
                "retrieval_ndcg": eval_report.retrieval.ndcg,
                "grounding_score": eval_report.grounding.grounding_score,
                "reasoning_consistency": eval_report.reasoning.logical_consistency_score,
                "hallucination_rate": eval_report.hallucination_rate,
                "overall_score": eval_report.overall_score,
                "estimated_cost_usd": eval_report.performance.estimated_cost_usd,
            }

        if diagnostics:
            response["retrieval_diagnostics"] = diagnostics.__dict__

        return response

    def _generate_cache_key(self, prefix: str, *args) -> str:
        data = "".join(str(arg) for arg in args)
        return f"{prefix}:{hashlib.sha256(data.encode()).hexdigest()}"

    def _generate_fallback_response(self, error: Exception) -> dict:
        """Standard fallback when AI pipeline is unavailable (10.3.8)."""
        return {
            "answer": "The AI reasoning system is temporarily unavailable. Please try again in a few minutes.",
            "summary": "Service unavailable.",
            "citations": [],
            "evidence": [],
            "confidence": 0.0,
            "grounding_score": 0.0,
            "answer_status": "error",
            "missing_documents": [],
            "contradictions": [],
            "reasoning_notes": f"System Error: {str(error)}",
            "reasoning_metadata": None,
            "sources": [],
        }

    def _generate_insufficient_response(self) -> dict:
        return {
            "answer": "No supporting evidence was found in the uploaded legal documents.",
            "summary": "No evidence found.",
            "citations": [],
            "evidence": [],
            "confidence": 0.0,
            "grounding_score": 0.0,
            "answer_status": "insufficient_evidence",
            "missing_documents": [],
            "contradictions": [],
            "reasoning_notes": "Retrieval returned no results or confidence too low.",
            "reasoning_metadata": None,
            "sources": [],
        }

    def _extract_summary(self, answer: str) -> str:
        match = re.search(r"### Summary(.*?)(###|$)", answer, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_citations(self, answer: str) -> list[str]:
        return list(set(re.findall(r"\[Evidence \d+\]", answer)))
