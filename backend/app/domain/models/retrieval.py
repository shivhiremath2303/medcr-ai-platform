from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class QueryIntent(str, Enum):
    CLAUSE_LOOKUP = "clause_lookup"
    DEFINITION = "definition"
    COMPARISON = "comparison"
    TIMELINE = "timeline"
    SUMMARY = "summary"
    GENERAL_LEGAL_QA = "general_legal_qa"


@dataclass
class QueryUnderstanding:
    """
    Structured understanding of a legal query.
    """

    original_query: str
    rewritten_query: str
    intent: QueryIntent
    entities: List[str] = field(default_factory=list)
    expanded_terms: List[str] = field(default_factory=list)
    is_multi_doc: bool = False


@dataclass
class RetrievalDiagnostics:
    """
    Diagnostics report for a retrieval operation.
    """

    query_type: str
    retrieval_strategy: str
    expanded_terms: List[str]
    dynamic_top_k: int
    documents_considered: int
    documents_selected: int
    duplicate_chunks_removed: int
    context_compression_ratio: float
    retrieval_latency_ms: float
    evidence_diversity_score: float
    hybrid_weights: Dict[str, float]
