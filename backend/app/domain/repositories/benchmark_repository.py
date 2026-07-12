from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class BenchmarkCase:
    id: str
    query: str
    expected_answer: str
    expected_evidence_ids: List[str]
    category: str  # e.g., "clause_lookup", "comparison", "timeline"
    metadata: Dict[str, Any]


class BenchmarkRepository(ABC):
    @abstractmethod
    def get_all_cases(self) -> List[BenchmarkCase]:
        """Retrieve all benchmark cases."""

    @abstractmethod
    def get_cases_by_category(self, category: str) -> List[BenchmarkCase]:
        """Retrieve cases by category."""
