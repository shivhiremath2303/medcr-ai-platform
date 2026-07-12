"""Domain models package.

This package defines simple data-holding domain entities used across the
core application. The domain layer is intentionally dependency-free (no
Pydantic/FastAPI/LangChain imports) — simple dataclasses are used.
"""

from .chunk import Chunk
from .document import Document
from .evaluation import (
    EvaluationReport,
    GroundingMetrics,
    PerformanceMetrics,
    ReasoningMetrics,
    RetrievalMetrics,
)
from .evidence import Evidence
from .grounding import AnswerStatus, GroundingReport, SufficiencyLevel
from .metadata import Metadata
from .page import Page
from .reasoning import (
    ClauseComparison,
    LegalEntityRelationship,
    LegalIssue,
    ReasoningReport,
    TimelineEvent,
)
from .search_result import SearchResult
from .user import User, UserRole

__all__ = [
    "Document",
    "Page",
    "Chunk",
    "Metadata",
    "SearchResult",
    "User",
    "UserRole",
    "Evidence",
    "AnswerStatus",
    "SufficiencyLevel",
    "GroundingReport",
    "LegalIssue",
    "TimelineEvent",
    "LegalEntityRelationship",
    "ClauseComparison",
    "ReasoningReport",
    "RetrievalMetrics",
    "GroundingMetrics",
    "ReasoningMetrics",
    "PerformanceMetrics",
    "EvaluationReport",
]
