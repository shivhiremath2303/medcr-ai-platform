"""Domain models package.

This package defines simple data-holding domain entities used across the
core application. The domain layer is intentionally dependency-free (no
Pydantic/FastAPI/LangChain imports) — simple dataclasses are used.
"""
from .document import Document
from .page import Page
from .chunk import Chunk
from .metadata import Metadata
from .search_result import SearchResult
from .user import User, UserRole
from .evidence import Evidence
from .grounding import AnswerStatus, SufficiencyLevel, GroundingReport
from .reasoning import LegalIssue, TimelineEvent, LegalEntityRelationship, ClauseComparison, ReasoningReport
from .evaluation import RetrievalMetrics, GroundingMetrics, ReasoningMetrics, PerformanceMetrics, EvaluationReport

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
