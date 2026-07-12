import re
import time
from typing import Optional, List, Dict, Any
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.query_rewriter import QueryRewriter
from app.domain.repositories.context_builder import ContextBuilder
from app.domain.repositories.benchmark_repository import BenchmarkRepository
from app.services.rag.grounding_engine import GroundingEngine
from app.services.rag.reasoning_engine import ReasoningEngine
from app.services.rag.evaluation_engine import EvaluationEngine
from app.core.observability.logger import get_logger
from app.core.observability.metrics import MetricsRegistry
from app.core.observability.telemetry import get_tracer

logger = get_logger(__name__)
tracer = get_tracer(__name__)


class RAGService:
    """
    Coordinates the advanced Retrieval-Augmented Generation workflow with scientific evaluation.
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

    def answer_question(
        self, question: str, k: int = 3, enable_evaluation: bool = True
    ) -> dict:
        """
        Retrieve context, generate an answer, and perform scientific evaluation.
        """
        overall_start = time.perf_counter()
        with tracer.start_as_current_span("rag_workflow") as span:
            span.set_attribute("rag.question", question)
            # Store the user's question
            self.memory.add_user_message(question)

            # Get conversation history
            memory_context = self.memory.get_context()

            # Phase 7.3.1: Legal Query Understanding
            with tracer.start_as_current_span("query_rewriting"):
                understanding = self.query_rewriter.understand_query(
                    question=question,
                    conversation_context=memory_context,
                )

            # Retrieve relevant chunks
            retrieval_start = time.perf_counter()
            with tracer.start_as_current_span("retrieval"):
                results = self.retrieval_service.retrieve(
                    query=understanding.original_query,
                    k=k,
                    params={"understanding": understanding},
                )
            retrieval_ms = (time.perf_counter() - retrieval_start) * 1000
            self.metrics.track_pipeline_step("retrieval", retrieval_ms / 1000)

            # Evidence Sufficiency Analysis
            raw_confidence = sum(r.score for r in results[:1]) if results else 0.0
            sufficiency = self.grounding_engine.analyze_sufficiency(
                results, raw_confidence
            )

            if not results or sufficiency == "insufficient":
                return self._generate_insufficient_response()

            # Convert results to structured Evidence objects
            evidence_list = self.context_builder.results_to_evidence(results)

            # Build LLM context
            context = self.context_builder.build(results)

            # 2. Grounded Answer Generation with Deep Reasoning
            llm_start = time.perf_counter()
            with tracer.start_as_current_span("llm_generation"):
                answer = self.llm_provider.generate_answer(
                    question=question,
                    context=context,
                )
            llm_ms = (time.perf_counter() - llm_start) * 1000
            self.metrics.track_pipeline_step("llm_generation", llm_ms / 1000)

            # Store assistant response
            self.memory.add_assistant_message(answer)

            # 3. Hallucination Detection & Verification
            with tracer.start_as_current_span("grounding_verification"):
                validation_errors = self.grounding_engine.validate_answer(
                    answer, evidence_list
                )

                summary = self._extract_summary(answer)
                citations = self._extract_citations(answer)
                contradictions = self.grounding_engine.detect_contradictions(answer)
                missing_docs = self.grounding_engine.detect_missing_evidence(answer)

            # 4. Structured Reasoning Extraction
            reasoning_metadata = self.reasoning_engine.extract_reasoning(
                answer, evidence_list
            )

            # 5. Grounding Score Calculation
            grounding_score = self.grounding_engine.calculate_grounding_score(
                evidence_list=evidence_list,
                citations=citations,
                sufficiency=sufficiency,
                contradictions=contradictions,
            )
            self.metrics.track_evaluation("grounding", grounding_score)

            # 6. Answer Status Categorization
            status = self.grounding_engine.determine_status(
                answer=answer,
                sufficiency=sufficiency,
                grounding_score=grounding_score,
                contradictions=contradictions,
            )

            # 7. Scientific Evaluation (Phase 7.5)
            eval_report = None
            if enable_evaluation:
                with tracer.start_as_current_span("scientific_evaluation"):
                    # Find benchmark case if any
                    expected_ids = []
                    for case in self.benchmark_repo.get_all_cases():
                        if case.query.lower() in question.lower():
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
                        tokens_in=len(context) // 4,  # estimation
                        tokens_out=len(answer) // 4,  # estimation
                    )

                    eval_report = self.evaluation_engine.generate_report(
                        query=question,
                        retrieval=retrieval_metrics,
                        grounding=grounding_metrics,
                        reasoning=reasoning_metrics,
                        performance=performance_metrics,
                    )

            # Get Retrieval Diagnostics
            diagnostics = None
            if hasattr(self.retrieval_service, "last_diagnostics"):
                diagnostics = self.retrieval_service.last_diagnostics

            # Build source list
            sources = [
                {
                    "filename": ev.document_name,
                    "page_number": ev.page_number,
                }
                for ev in evidence_list
            ]

            response_data = {
                "answer": answer,
                "summary": summary,
                "citations": citations,
                "evidence": evidence_list,
                "confidence": raw_confidence,
                "grounding_score": grounding_score,
                "answer_status": status.value,
                "missing_documents": missing_docs,
                "contradictions": contradictions,
                "reasoning_notes": (
                    f"Validation Errors: {', '.join(validation_errors)}"
                    if validation_errors
                    else None
                ),
                "reasoning_metadata": reasoning_metadata.__dict__,
                "sources": sources,
            }

            if eval_report:
                response_data["evaluation"] = {
                    "retrieval_ndcg": eval_report.retrieval.ndcg,
                    "grounding_score": eval_report.grounding.grounding_score,
                    "reasoning_consistency": eval_report.reasoning.logical_consistency_score,
                    "hallucination_rate": eval_report.hallucination_rate,
                    "overall_score": eval_report.overall_score,
                    "estimated_cost_usd": eval_report.performance.estimated_cost_usd,
                }

            if diagnostics:
                response_data["retrieval_diagnostics"] = diagnostics.__dict__

            total_ms = (time.perf_counter() - overall_start) * 1000
            span.set_attribute("rag.total_latency_ms", total_ms)
            self.metrics.track_pipeline_step("overall_rag", total_ms / 1000)

            return response_data

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
        if match:
            return match.group(1).strip()
        return ""

    def _extract_citations(self, answer: str) -> list[str]:
        return list(set(re.findall(r"\[Evidence \d+\]", answer)))
