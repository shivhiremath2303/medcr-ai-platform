from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import List, Optional


class AnswerStatus(StrEnum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    OUTSIDE_SCOPE = "outside_scope"


class SufficiencyLevel(StrEnum):
    SUFFICIENT = "sufficient"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"


@dataclass
class GroundingReport:
    """
    Detailed report on the grounding and hallucination checks for a generated answer.
    """

    status: AnswerStatus
    grounding_score: float
    sufficiency_level: SufficiencyLevel
    missing_documents: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    unsupported_statements: List[str] = field(default_factory=list)
    reasoning_notes: str | None = None
