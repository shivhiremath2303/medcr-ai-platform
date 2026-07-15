import json

from app.core.observability.logger import get_logger
from app.domain.models.retrieval import QueryIntent, QueryUnderstanding
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.query_rewriter import QueryRewriter as IQueryRewriter

logger = get_logger(__name__)


class QueryRewriter(IQueryRewriter):
    """
    Intelligently rewrites and expands legal queries with Scaling support.
    Implements Milestone 10.3.3.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def rewrite(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        if not conversation_context:
            return question
        return await self.llm_provider.rewrite_question(question, conversation_context)

    async def understand_query(
        self,
        question: str,
        conversation_context: str,
    ) -> QueryUnderstanding:
        """
        Detects legal intent, entities, and expands terms.
        """
        # If there's context, rewrite first (Async)
        rewritten = question
        if conversation_context:
            rewritten = await self.rewrite(question, conversation_context)

        intent = self._detect_intent(rewritten)
        expansions = self._expand_legal_terms(rewritten)

        entities = []
        if "section" in rewritten.lower() or "clause" in rewritten.lower():
            entities.append("legal_reference")

        return QueryUnderstanding(
            original_query=question,
            rewritten_query=rewritten,
            intent=intent,
            entities=entities,
            expanded_terms=expansions,
            is_multi_doc="compare" in rewritten.lower()
            or "between" in rewritten.lower(),
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
