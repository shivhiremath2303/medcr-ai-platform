import json
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.query_rewriter import QueryRewriter as IQueryRewriter
from app.domain.models.retrieval import QueryUnderstanding, QueryIntent
from app.core.observability.logger import get_logger

logger = get_logger(__name__)


class QueryRewriter(IQueryRewriter):
    """
    Intelligently rewrites and expands legal queries.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def rewrite(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """Legacy support."""
        return question

    def understand_query(
        self,
        question: str,
        conversation_context: str,
    ) -> QueryUnderstanding:
        """
        Detects legal intent, entities, and expands terms.
        """

        # In a real production system, this would use a specific prompt
        # to the LLM to return a JSON with intent, entities, and expansions.
        # For this milestone, we'll implement a hybrid logic:
        # 1. Heuristic intent detection
        # 2. Basic expansion

        intent = self._detect_intent(question)
        expansions = self._expand_legal_terms(question)

        # Simple entity detection (dates, sections)
        entities = []
        if "section" in question.lower() or "clause" in question.lower():
            entities.append("legal_reference")

        return QueryUnderstanding(
            original_query=question,
            rewritten_query=question,  # In prod, this would be standalone
            intent=intent,
            entities=entities,
            expanded_terms=expansions,
            is_multi_doc="compare" in question.lower() or "between" in question.lower(),
        )

    def _detect_intent(self, query: str) -> QueryIntent:
        q = query.lower()
        if any(w in q for w in ["what is", "define", "definition"]):
            return QueryIntent.DEFINITION
        if any(w in q for w in ["clause", "section", "provision", "article"]):
            return QueryIntent.CLAUSE_LOOKUP
        if any(w in q for w in ["compare", "difference", "versus", "vs"]):
            return QueryIntent.COMPARISON
        if any(w in q for w in ["when", "date", "timeline", "after", "before"]):
            return QueryIntent.TIMELINE
        if any(w in q for w in ["summarize", "summary", "overview"]):
            return QueryIntent.SUMMARY
        return QueryIntent.GENERAL_LEGAL_QA

    def _expand_legal_terms(self, query: str) -> list[str]:
        # Basic legal synonym map for expansion
        expansions = []
        synonyms = {
            "termination": ["dismissal", "resignation", "breach", "cancellation"],
            "agreement": ["contract", "accord", "undertaking", "covenant"],
            "liability": ["responsibility", "obligation", "indemnity", "damages"],
            "employee": ["worker", "staff", "personnel", "consultant"],
        }

        q_words = query.lower().split()
        for word, syns in synonyms.items():
            if word in q_words:
                expansions.extend(syns)

        return list(set(expansions))
