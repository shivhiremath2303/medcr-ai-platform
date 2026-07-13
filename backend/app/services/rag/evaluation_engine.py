import math
import time
from typing import Any, Dict, List, Optional

from app.core.observability.logger import get_logger
from app.core.observability.telemetry import traced
from app.domain.models import (
    EvaluationReport,
    Evidence,
    GroundingMetrics,
    PerformanceMetrics,
    ReasoningMetrics,
    ReasoningReport,
    RetrievalMetrics,
    SearchResult,
)

logger = get_logger(__name__)


class EvaluationEngine:
    """
    Scientific measurement framework for AI quality, performance and cost.
    Part of the AI Pipeline Tracing (Milestone 10.2.1).
    """

    @traced("evaluation.retrieval")
    def evaluate_retrieval(
        self, results: List[SearchResult], expected_ids: List[str]
    ) -> RetrievalMetrics:
        """
        Phase 7.5.1: Retrieval Evaluation
        Calculates Precision, Recall, MRR, nDCG.
        """
        if not results:
            return RetrievalMetrics(0, 0, 0, 0, 0, 0)

        # Precision@K
        hits = [1 if r.chunk.chunk_id in expected_ids else 0 for r in results]
        precision = sum(hits) / len(results)

        # Recall@K
        recall = sum(hits) / len(expected_ids) if expected_ids else 1.0

        # MRR (Mean Reciprocal Rank)
        mrr = 0.0
        for i, hit in enumerate(hits):
            if hit:
                mrr = 1.0 / (i + 1)
                break

        # nDCG (simplified for binary relevance)
        dcg = sum([hit / math.log2(i + 2) for i, hit in enumerate(hits)])
        idcg = sum(
            [
                1.0 / math.log2(i + 2)
                for i in range(min(len(expected_ids), len(results)))
            ]
        )
        ndcg = dcg / idcg if idcg > 0 else 0.0

        # Diversity (ratio of unique documents)
        unique_docs = len({r.chunk.document_id for r in results})
        diversity = unique_docs / len(results)

        # Context utilization (simple heuristic)
        total_chars = sum(len(r.chunk.text) for r in results)
        utilization = min(1.0, total_chars / 10000)  # Assuming 10k is 'full'

        return RetrievalMetrics(
            precision_at_k=round(precision, 4),
            recall_at_k=round(recall, 4),
            mrr=round(mrr, 4),
            ndcg=round(ndcg, 4),
            evidence_diversity=round(diversity, 4),
            context_utilization=round(utilization, 4),
        )

    @traced("evaluation.grounding")
    def evaluate_grounding(
        self, answer: str, evidence_list: List[Evidence], grounding_score: float
    ) -> GroundingMetrics:
        """
        Phase 7.5.2: Grounding Evaluation
        """
        import re

        citations = re.findall(r"\[Evidence (\d+)\]", answer)
        valid_citations = [c for c in citations if 0 < int(c) <= len(evidence_list)]
        citation_accuracy = len(valid_citations) / len(citations) if citations else 1.0

        # Evidence coverage: what % of retrieved evidence was used?
        unique_cited = len(set(valid_citations))
        coverage = unique_cited / len(evidence_list) if evidence_list else 1.0

        return GroundingMetrics(
            grounding_score=grounding_score,
            citation_accuracy=round(citation_accuracy, 4),
            unsupported_claims_count=len(citations) - len(valid_citations),
            evidence_coverage=round(coverage, 4),
        )

    @traced("evaluation.reasoning")
    def evaluate_reasoning(self, report: ReasoningReport) -> ReasoningMetrics:
        """
        Phase 7.5.3: Reasoning Evaluation
        """
        # Logic consistency: based on conflicts detected
        consistency = 1.0 - (0.2 * len(report.conflicts))
        consistency = max(0.0, consistency)

        # Issue identification rate: ratio of identified issues vs facts
        issue_rate = len(report.issues) / len(report.facts) if report.facts else 0.0

        return ReasoningMetrics(
            logical_consistency_score=round(consistency, 4),
            conflict_handling_score=1.0 if report.conflicts else 0.0,
            issue_identification_rate=round(min(1.0, issue_rate), 4),
            timeline_accuracy=1.0 if report.timeline else 0.0,
            analysis_quality_score=0.8,  # Placeholder for heuristic
        )

    @traced("evaluation.performance")
    def evaluate_performance(
        self, retrieval_ms: float, total_ms: float, tokens_in: int, tokens_out: int
    ) -> PerformanceMetrics:
        """
        Phase 7.5.5: Performance Evaluation
        """
        # Cost calculation (Gemini 2.0 Flash approx rates)
        # $0.10 / 1M tokens in, $0.40 / 1M tokens out
        cost = (tokens_in * 0.10 / 1_000_000) + (tokens_out * 0.40 / 1_000_000)

        return PerformanceMetrics(
            retrieval_latency_ms=retrieval_ms,
            llm_latency_ms=total_ms - retrieval_ms,
            total_latency_ms=total_ms,
            token_usage_input=tokens_in,
            token_usage_output=tokens_out,
            estimated_cost_usd=round(cost, 6),
        )

    @traced("evaluation.report_generation")
    def generate_report(
        self,
        query: str,
        retrieval: RetrievalMetrics,
        grounding: GroundingMetrics,
        reasoning: ReasoningMetrics,
        performance: PerformanceMetrics,
    ) -> EvaluationReport:
        """
        Phase 7.5.7: Evaluation Reports
        """
        # Overall score: Weighted average
        overall = (
            retrieval.ndcg * 0.3
            + grounding.grounding_score * 0.4
            + reasoning.logical_consistency_score * 0.3
        )

        # Hallucination rate (proxy): unsupported claims / total claims
        hallucination_rate = 0.0
        if grounding.unsupported_claims_count > 0:
            hallucination_rate = grounding.unsupported_claims_count / 10  # heuristic

        return EvaluationReport(
            query=query,
            retrieval=retrieval,
            grounding=grounding,
            reasoning=reasoning,
            performance=performance,
            hallucination_rate=round(hallucination_rate, 4),
            overall_score=round(overall, 4),
        )
