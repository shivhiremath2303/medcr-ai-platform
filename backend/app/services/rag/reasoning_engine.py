import re
from typing import List, Dict, Any, Optional
from app.domain.models import (
    LegalIssue, TimelineEvent, LegalEntityRelationship,
    ClauseComparison, ReasoningReport, Evidence
)
from app.core.observability.logger import get_logger

logger = get_logger(__name__)

class ReasoningEngine:
    """
    Service responsible for extracting structured legal reasoning from LLM output.
    """

    def extract_reasoning(self, answer: str, evidence_list: List[Evidence]) -> ReasoningReport:
        """
        Parses the structured LLM response into a domain ReasoningReport.
        """
        report = ReasoningReport()

        report.facts = self._extract_facts(answer)
        report.issues = self._extract_issues(answer)
        report.timeline = self._extract_timeline(answer)
        report.relationships = self._extract_relationships(answer)
        report.comparisons = self._extract_comparisons(answer)
        report.conflicts = self._extract_conflicts(answer)
        report.uncertainties = self._extract_uncertainties(answer)

        return report

    def _extract_facts(self, text: str) -> List[str]:
        match = re.search(r"### Facts(.*?)(###|$)", text, re.DOTALL | re.IGNORECASE)
        if not match: return []
        facts = re.findall(r"-\s*(.*?)(?:\n|$)", match.group(1))
        return [f.strip() for f in facts if f.strip()]

    def _extract_issues(self, text: str) -> List[LegalIssue]:
        match = re.search(r"### Issues & Risks(.*?)(###|$)", text, re.DOTALL | re.IGNORECASE)
        if not match: return []

        issues = []
        # Issue: [Title] | Severity: [Low/Medium/High] | Description: [details] [Evidence Z]
        lines = re.findall(r"-\s*Issue:(.*?)(?:\n|$)", match.group(1), re.IGNORECASE)
        for line in lines:
            try:
                parts = line.split("|")
                title = parts[0].strip()
                severity = "medium"
                description = line

                for p in parts:
                    if "severity:" in p.lower():
                        severity = p.lower().replace("severity:", "").strip()
                    if "description:" in p.lower():
                        description = p.replace("Description:", "").strip()

                evidence_ids = re.findall(r"\[Evidence (\d+)\]", line)

                issues.append(LegalIssue(
                    title=title,
                    description=description,
                    severity=severity,
                    evidence_ids=evidence_ids
                ))
            except Exception:
                continue
        return issues

    def _extract_timeline(self, text: str) -> List[TimelineEvent]:
        match = re.search(r"### Timeline(.*?)(###|$)", text, re.DOTALL | re.IGNORECASE)
        if not match: return []

        events = []
        # - [Date/Time]: [Event Description] [Evidence X]
        lines = re.findall(r"-\s*(.*?)(?:\n|$)", match.group(1))
        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)
                date = parts[0].strip()
                desc = parts[1].strip()
                evidence_id = ""
                ev_match = re.search(r"\[Evidence (\d+)\]", desc)
                if ev_match:
                    evidence_id = ev_match.group(1)

                events.append(TimelineEvent(
                    date=date,
                    event=desc, # In this case event and description are same for now
                    description=desc,
                    evidence_id=evidence_id
                ))
        return events

    def _extract_relationships(self, text: str) -> List[LegalEntityRelationship]:
        match = re.search(r"### Entity Relationships(.*?)(###|$)", text, re.DOTALL | re.IGNORECASE)
        if not match: return []

        rels = []
        # - [Entity A] -> [Relationship] -> [Entity B]: [Description]
        lines = re.findall(r"-\s*(.*?)(?:\n|$)", match.group(1))
        for line in lines:
            if "->" in line and ":" in line:
                try:
                    parts = line.split(":")
                    entities = parts[0].split("->")
                    if len(entities) >= 2:
                        rels.append(LegalEntityRelationship(
                            source=entities[0].strip(),
                            target=entities[-1].strip(),
                            relationship_type=entities[1].strip() if len(entities) > 2 else "related_to",
                            description=parts[1].strip()
                        ))
                except Exception:
                    continue
        return rels

    def _extract_comparisons(self, text: str) -> List[ClauseComparison]:
        # This is harder to extract from free-form analysis, but we can look for "Comparison:" blocks
        # or just rely on the Analysis section for human reading.
        # For structured extraction, we'll look for specific keywords.
        comparisons = []
        if "compare" in text.lower() or "difference" in text.lower():
            # Heuristic: extract a single "Legal Comparison" if multi-doc is mentioned
            comparisons.append(ClauseComparison(
                clause_type="General Comparison",
                similarities=["Extracted from Analysis section"],
                differences=[]
            ))
        return comparisons

    def _extract_conflicts(self, text: str) -> List[str]:
        conflicts = re.findall(r"Conflict:\s*(.*?)(?:\n|$)", text, re.IGNORECASE)
        return [c.strip() for c in conflicts if c.strip()]

    def _extract_uncertainties(self, text: str) -> List[str]:
        match = re.search(r"### Remaining Uncertainty(.*?)(###|$)", text, re.DOTALL | re.IGNORECASE)
        if not match: return []
        uncertainties = re.findall(r"-\s*(.*?)(?:\n|$)", match.group(1))
        return [u.strip() for u in uncertainties if u.strip()]
