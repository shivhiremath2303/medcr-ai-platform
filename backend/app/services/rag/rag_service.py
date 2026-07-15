import asyncio
import hashlib
import json
import re
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import numpy as np

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
from app.domain.repositories.embedding_repository import EmbeddingRepository
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
    Optimized for Latency, Quality, and Dynamic Model Routing (10.5.4).
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
        embedding_provider: Optional[EmbeddingRepository] = None,
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
        self.embedding_provider = embedding_provider

        # Local semantic cache registry
        self.semantic_cache_entries: List[dict] = []

    @PerformanceProfiler.profile_function(
        name="rag_answer_question", slow_threshold_ms=8000
    )
    async def answer_question(
        self,
        question: str,
        k: int = 3,
        enable_evaluation: bool = True,
        tenant_id: Optional[str] = None
    ) -> dict:
        """
        Retrieve context, generate an answer, and perform scientific evaluation.
        Ensures tenant isolation and optimized for latency (10.5.2).
        """
        overall_start = time.perf_counter()
        with tracer.start_as_current_span("rag_workflow") as span:
            span.set_attribute("rag.question", question)
            if tenant_id:
                span.set_attribute("tenant.id", tenant_id)

            # 1. Distributed Caching Check (Namespace by tenant)
            memory_context = self.memory.get_context()
            context_hash = self._generate_cache_key(
                "answer", tenant_id or "global", question, memory_context, k
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

            # Check semantic cache for retrieval results (10.5.4)
            retrieval_cache_key = self._generate_cache_key(
                "retrieval", tenant_id or "global", understanding.original_query, k
            )

            results = await self._lookup_semantic_retrieval_cache(
                understanding.original_query, tenant_id or "global", k
            )

            retrieval_ms = 0.0
            if results:
                logger.info("Serving retrieval results from semantic cache.")
                span.set_attribute("retrieval.cache_hit", True)
            else:
                retrieval_start = time.perf_counter()
                with tracer.start_as_current_span("retrieval"):
                    results = await self.retrieval_service.retrieve(
                        query=understanding.original_query,
                        k=k,
                        params={"understanding": understanding},
                        tenant_id=tenant_id
                    )
                retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

                # Save to semantic and standard cache
                self.cache.set(retrieval_cache_key, results, ttl=CacheTTL.MEDIUM)
                await self._save_semantic_retrieval_cache(
                    understanding.original_query, tenant_id or "global", k, retrieval_cache_key
                )

            raw_confidence = sum(r.score for r in results[:1]) if results else 0.0
            sufficiency = self.grounding_engine.analyze_sufficiency(
                results, raw_confidence
            )

            if not results or sufficiency == "insufficient":
                return self._generate_insufficient_response()

            evidence_list = self.context_builder.results_to_evidence(results)
            context = self.context_builder.build(results, query=question)

            # 3. Parallel Stage: Retrieval Eval + LLM Generation (10.5.2)
            # We can start evaluating retrieval metrics while waiting for the LLM
            retrieval_eval_task = None
            if enable_evaluation:
                retrieval_eval_task = asyncio.create_task(
                    self.limiter.run_in_thread(
                        self.evaluation_engine.evaluate_retrieval, results, self._get_expected_ids(question)
                    )
                )

            llm_start = time.perf_counter()
            try:
                # LLM Generation with Dynamic Model Routing (10.5.4)
                answer = await self.llm_provider.generate_answer(
                    question=question,
                    context=context,
                    complexity_hint=understanding.intent.value,
                )
            except Exception as e:
                logger.error(f"AI Generation failed: {e}")
                span.set_status(tracer.Status(tracer.StatusCode.ERROR, str(e)))
                return self._generate_fallback_response(e)

            llm_ms = (time.perf_counter() - llm_start) * 1000
            self.metrics.track_pipeline_step("llm_generation", llm_ms / 1000)
            self.memory.add_assistant_message(answer)

            # 4. Parallel Analytics Phase (10.5.2)
            # Extract grounding, reasoning, and finish performance metrics concurrently
            with tracer.start_as_current_span("parallel_analytics"):
                grounding_task = self.limiter.run_async(
                    self._process_grounding, answer, evidence_list, sufficiency
                )
                reasoning_task = self.limiter.run_async(
                    self._process_reasoning, answer, evidence_list
                )

                # Wait for extraction results
                grounding_data, reasoning_metadata = await asyncio.gather(
                    grounding_task, reasoning_task
                )

            # 5. Build Scientific Evaluation Report
            eval_report = None
            if enable_evaluation and retrieval_eval_task:
                retrieval_metrics = await retrieval_eval_task

                # Remaining evaluations (IO or CPU bound)
                grounding_metrics = self.evaluation_engine.evaluate_grounding(
                    answer, evidence_list, grounding_data["score"]
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

                eval_report = self.evaluation_engine.generate_report(
                    query=question,
                    retrieval=retrieval_metrics,
                    grounding=grounding_metrics,
                    reasoning=reasoning_metrics,
                    performance=performance_metrics,
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

    async def _lookup_semantic_retrieval_cache(
        self, query: str, tenant_id: str, k: int
    ) -> Optional[List[Any]]:
        """
        Check if query matches a semantically similar cached query (10.5.4).
        Cosine similarity threshold is set to 0.95.
        """
        if not self.embedding_provider:
            return None

        try:
            query_emb = await self.embedding_provider.aembed_query(query)
            query_vector = np.array(query_emb)

            for entry in self.semantic_cache_entries:
                if entry["tenant_id"] == tenant_id and entry["k"] == k:
                    cached_vector = np.array(entry["embedding"])

                    similarity = np.dot(query_vector, cached_vector) / (
                        np.linalg.norm(query_vector) * np.linalg.norm(cached_vector)
                    )

                    if similarity >= 0.95:
                        logger.info(
                            "Semantic cache hit! Query '%s' matches '%s' with similarity %.4f",
                            query, entry["query"], similarity
                        )
                        return self.cache.get(entry["cache_key"])
        except Exception as e:
            logger.warning("Semantic cache lookup failed: %s", e)

        return None

    async def _save_semantic_retrieval_cache(
        self, query: str, tenant_id: str, k: int, cache_key: str
    ):
        """Save query embedding to local semantic cache registry (10.5.4)."""
        if not self.embedding_provider:
            return

        try:
            query_emb = await self.embedding_provider.aembed_query(query)
            self.semantic_cache_entries.append({
                "query": query,
                "tenant_id": tenant_id,
                "k": k,
                "embedding": query_emb,
                "cache_key": cache_key
            })
        except Exception as e:
            logger.warning("Failed to save semantic cache entry: %s", e)

    def _get_expected_ids(self, query: str) -> List[str]:
        """Helper to find expected IDs from benchmark repo."""
        for case in self.benchmark_repo.get_all_cases():
            if case.query.lower() in query.lower():
                return case.expected_evidence_ids
        return []

    async def stream_answer(
        self,
        question: str,
        k: int = 3,
        tenant_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streamed RAG response for API Scalability (10.3.7).
        Enhanced with tenant_id isolation (10.4.6).
        """
        memory_context = self.memory.get_context()

        understanding = await self.query_rewriter.understand_query(
            question=question,
            conversation_context=memory_context,
        )

        results = await self.retrieval_service.retrieve(
            query=understanding.original_query,
            k=k,
            params={"understanding": understanding},
            tenant_id=tenant_id
        )

        context = self.context_builder.build(results, query=question)

        # Stream from provider with Dynamic Model Routing (10.5.4)
        full_answer = ""
        async for chunk in self.llm_provider.stream_answer(
            question=question,
            context=context,
            complexity_hint=understanding.intent.value,
        ):
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
