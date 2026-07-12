from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg: float
    evidence_diversity: float
    context_utilization: float


@dataclass
class GroundingMetrics:
    grounding_score: float
    citation_accuracy: float
    unsupported_claims_count: int
    evidence_coverage: float


@dataclass
class ReasoningMetrics:
    logical_consistency_score: float
    conflict_handling_score: float
    issue_identification_rate: float
    timeline_accuracy: float
    analysis_quality_score: float


@dataclass
class PerformanceMetrics:
    retrieval_latency_ms: float
    llm_latency_ms: float
    total_latency_ms: float
    token_usage_input: int
    token_usage_output: int
    estimated_cost_usd: float


@dataclass
class EvaluationReport:
    """
    Comprehensive evaluation report for a single query or a benchmark run.
    """

    timestamp: datetime = field(default_factory=datetime.utcnow)
    query: str = ""
    retrieval: Optional[RetrievalMetrics] = None
    grounding: Optional[GroundingMetrics] = None
    reasoning: Optional[ReasoningMetrics] = None
    performance: Optional[PerformanceMetrics] = None
    hallucination_rate: float = 0.0
    overall_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
