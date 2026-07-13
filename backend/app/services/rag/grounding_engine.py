import re
from typing import Any, Dict, List

from app.core.observability.logger import get_logger
from app.core.observability.telemetry import traced
from app.domain.models import (
    AnswerStatus,
    Evidence,
    GroundingReport,
    SearchResult,
    SufficiencyLevel,
)

logger = get_logger(__name__)


class GroundingEngine:
    """
    Service responsible for hallucination detection, grounding validation,
    and evidence sufficiency analysis.
    Part of the AI Pipeline Tracing (Milestone 10.2.1).
    """

    @traced("grounding.analyze_sufficiency")
    def analyze_sufficiency(
        self, results: List[SearchResult], confidence: float
    ) -> SufficiencyLevel:
        """
        Evaluate if retrieved evidence is sufficient to answer a question.
        """
        if not results or confidence < 0.2:
            return SufficiencyLevel.INSUFFICIENT

        # Diversity check: how many unique documents?
        unique_docs = len({r.chunk.document_id for r in results})

        if len(results) >= 3 and unique_docs >= 1 and confidence > 0.6:
            return SufficiencyLevel.SUFFICIENT

        return SufficiencyLevel.PARTIAL

    @traced("grounding.calculate_score")
    def calculate_grounding_score(
        self,
        evidence_list: List[Evidence],
        citations: List[str],
        sufficiency: SufficiencyLevel,
        contradictions: List[str],
    ) -> float:
        """
        Computes a grounding score [0, 1] based on multiple factors.
        """
        if not evidence_list:
            return 0.0

        # 1. Base score from average confidence of cited evidence
        cited_indices = []
        for cit in citations:
            match = re.search(r"\d+", cit)
            if match:
                idx = int(match.group()) - 1
                if 0 <= idx < len(evidence_list):
                    cited_indices.append(idx)

        if not cited_indices:
            # Penalty for not using citations when evidence is available
            base_score = sum(e.confidence for e in evidence_list[:1]) * 0.5
        else:
            base_score = sum(evidence_list[i].confidence for i in cited_indices) / len(
                cited_indices
            )

        # 2. Sufficiency Multiplier
        sufficiency_map = {
            SufficiencyLevel.SUFFICIENT: 1.0,
            SufficiencyLevel.PARTIAL: 0.7,
            SufficiencyLevel.INSUFFICIENT: 0.3,
        }
        score = base_score * sufficiency_map.get(sufficiency, 1.0)

        # 3. Contradiction Penalty
        if contradictions:
            score *= 0.5

        # 4. Coverage Score (how many of the top 3 results were used)
        top_3_cited = [i for i in cited_indices if i < 3]
        coverage_bonus = len(top_3_cited) * 0.05  # max 0.15 bonus

        score = min(1.0, score + coverage_bonus)

        return round(score, 4)

    @traced("grounding.detect_contradictions")
    def detect_contradictions(self, answer: str) -> List[str]:
        """
        Extract contradiction notes from LLM output.
        LLM is prompted to mention conflicts explicitly.
        """
        # Simple regex to find "Conflict:" or "Contradiction:" lines
        conflicts = re.findall(
            r"(?:Conflict|Contradiction): (.*?)(?:\n|$)", answer, re.IGNORECASE
        )
        return [c.strip() for r in conflicts if (c := r.strip())]

    @traced("grounding.detect_missing")
    def detect_missing_evidence(self, answer: str) -> List[str]:
        """
        Extract missing document/clause notes from LLM output.
        """
        missing = re.findall(
            r"Missing (?:Evidence|Document|Clause): (.*?)(?:\n|$)",
            answer,
            re.IGNORECASE,
        )
        return [m.strip() for r in missing if (m := r.strip())]

    @traced("grounding.determine_status")
    def determine_status(
        self,
        answer: str,
        sufficiency: SufficiencyLevel,
        grounding_score: float,
        contradictions: List[str],
    ) -> AnswerStatus:
        """
        Categorizes the answer based on grounding analysis.
        """
        if (
            "The available documents do not contain sufficient evidence" in answer
            or sufficiency == SufficiencyLevel.INSUFFICIENT
        ):
            return AnswerStatus.INSUFFICIENT_EVIDENCE

        if "outside the scope" in answer.lower():
            return AnswerStatus.OUTSIDE_SCOPE

        if contradictions:
            return AnswerStatus.CONTRADICTORY_EVIDENCE

        if grounding_score > 0.7:
            return AnswerStatus.SUPPORTED

        return AnswerStatus.PARTIALLY_SUPPORTED

    @traced("grounding.validate_citations")
    def validate_answer(self, answer: str, evidence_list: List[Evidence]) -> List[str]:
        """
        Performs a final verification check on citations.
        Returns a list of validation errors (unsupported citations).
        """
        errors = []
        cited_numbers = re.findall(r"\[Evidence (\d+)\]", answer)

        for num in cited_numbers:
            idx = int(num) - 1
            if idx < 0 or idx >= len(evidence_list):
                errors.append(
                    f"Answer cited [Evidence {num}] which does not exist in retrieval results."
                )

        return errors
