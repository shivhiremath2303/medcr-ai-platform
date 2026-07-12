from typing import List

from app.domain.repositories.benchmark_repository import (
    BenchmarkCase,
    BenchmarkRepository,
)


class MemoryBenchmarkRepository(BenchmarkRepository):
    """
    Phase 7.5.6: Benchmark Dataset
    In-memory storage for curated legal evaluation datasets.
    """

    def __init__(self):
        self._cases = [
            BenchmarkCase(
                id="case-001",
                query="What are the termination notice periods in the employment contract?",
                expected_answer="The notice period is 30 days.",
                expected_evidence_ids=["chunk-term-01"],
                category="clause_lookup",
                metadata={"complexity": "low"},
            ),
            BenchmarkCase(
                id="case-002",
                query="Compare the liability limits between the 2023 and 2024 agreements.",
                expected_answer="The limit increased from $1M to $2M.",
                expected_evidence_ids=["chunk-liab-23", "chunk-liab-24"],
                category="comparison",
                metadata={"complexity": "high"},
            ),
            BenchmarkCase(
                id="case-003",
                query="Is there a conflict between the confidentiality clause and the public disclosure requirement?",
                expected_answer="Yes, Clause 4 prohibits disclosure while Section 9 requires it for regulatory compliance.",
                expected_evidence_ids=["chunk-conf-01", "chunk-reg-01"],
                category="conflict_detection",
                metadata={"complexity": "medium"},
            ),
        ]

    def get_all_cases(self) -> List[BenchmarkCase]:
        return self._cases

    def get_cases_by_category(self, category: str) -> List[BenchmarkCase]:
        return [c for c in self._cases if c.category == category]
