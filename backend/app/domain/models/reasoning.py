from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class LegalIssue:
    title: str
    description: str
    severity: str  # low, medium, high, critical
    evidence_ids: List[str] = field(default_factory=list)


@dataclass
class TimelineEvent:
    date: str
    event: str
    description: str
    evidence_id: str


@dataclass
class LegalEntityRelationship:
    source: str
    target: str
    relationship_type: str
    description: str


@dataclass
class ClauseComparison:
    clause_type: str
    similarities: List[str] = field(default_factory=list)
    differences: List[str] = field(default_factory=list)
    conflict_detected: bool = False


@dataclass
class ReasoningReport:
    """
    Structured report containing the deep legal analysis.
    """

    facts: List[str] = field(default_factory=list)
    issues: List[LegalIssue] = field(default_factory=list)
    timeline: List[TimelineEvent] = field(default_factory=list)
    relationships: List[LegalEntityRelationship] = field(default_factory=list)
    comparisons: List[ClauseComparison] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
