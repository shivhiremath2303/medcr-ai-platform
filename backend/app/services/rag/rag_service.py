import re
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.query_rewriter import QueryRewriter
from app.domain.repositories.context_builder import ContextBuilder
from app.services.rag.grounding_engine import GroundingEngine
from app.core.observability.logger import get_logger

logger = get_logger(__name__)

class RAGService:
    """
    Coordinates the Retrieval-Augmented Generation workflow with Evidence tracking and Grounding validation.
    """

    def __init__(
        self,
        retrieval_service: Retriever,
        llm_provider: LLMProvider,
        query_rewriter: QueryRewriter,
        memory: ConversationRepository,
        context_builder: ContextBuilder,
        grounding_engine: GroundingEngine,
    ):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.query_rewriter = query_rewriter
        self.memory = memory
        self.context_builder = context_builder
        self.grounding_engine = grounding_engine

    def answer_question(
        self,
        question: str,
        k: int = 3,
    ) -> dict:
        """
        Retrieve context, generate an answer and return detailed evidence, citations and grounding analysis.
        """

        # Store the user's question
        self.memory.add_user_message(question)

        # Get conversation history
        memory_context = self.memory.get_context()

        # Rewrite the question
        retrieval_query = self.query_rewriter.rewrite(
            question=question,
            conversation_context=memory_context,
        )

        # Retrieve relevant chunks
        results = self.retrieval_service.retrieve(
            query=retrieval_query,
            k=k,
        )

        # 1. Evidence Sufficiency Analysis
        # Calculate raw confidence from top results
        raw_confidence = sum(r.score for r in results[:1]) if results else 0.0
        sufficiency = self.grounding_engine.analyze_sufficiency(results, raw_confidence)

        if not results or sufficiency == "insufficient":
             return self._generate_insufficient_response()

        # Convert results to structured Evidence objects
        evidence_list = self.context_builder.results_to_evidence(results)

        # Build LLM context
        context = self.context_builder.build(results)

        # 2. Grounded Answer Generation
        answer = self.llm_provider.generate_answer(
            question=question,
            context=context,
        )

        # Store assistant response
        self.memory.add_assistant_message(answer)

        # 3. Hallucination Detection & Verification

        # Verify citations (Phase 7.2.8)
        validation_errors = self.grounding_engine.validate_answer(answer, evidence_list)
        if validation_errors:
            logger.warning(f"Answer verification failed: {validation_errors}")
            # In production, we might want to regenerate or redact,
            # for now we'll append a note or just flag it.

        # Extract components for API
        summary = self._extract_summary(answer)
        citations = self._extract_citations(answer)
        contradictions = self.grounding_engine.detect_contradictions(answer)
        missing_docs = self.grounding_engine.detect_missing_evidence(answer)

        # 4. Grounding Score Calculation (Phase 7.2.7)
        grounding_score = self.grounding_engine.calculate_grounding_score(
            evidence_list=evidence_list,
            citations=citations,
            sufficiency=sufficiency,
            contradictions=contradictions
        )

        # 5. Answer Status Categorization (Phase 7.2.6)
        status = self.grounding_engine.determine_status(
            answer=answer,
            sufficiency=sufficiency,
            grounding_score=grounding_score,
            contradictions=contradictions
        )

        # Build source list (for backward compatibility)
        sources = [
            {
                "filename": ev.document_name,
                "page_number": ev.page_number,
            }
            for ev in evidence_list
        ]

        return {
            "answer": answer,
            "summary": summary,
            "citations": citations,
            "evidence": evidence_list,
            "confidence": raw_confidence, # backward compatibility
            "grounding_score": grounding_score,
            "answer_status": status.value,
            "missing_documents": missing_docs,
            "contradictions": contradictions,
            "reasoning_notes": f"Validation Errors: {', '.join(validation_errors)}" if validation_errors else None,
            "sources": sources,
        }

    def _generate_insufficient_response(self) -> dict:
        return {
            "answer": "No supporting evidence was found in the uploaded legal documents.",
            "summary": "No evidence found.",
            "citations": [],
            "evidence": [],
            "confidence": 0.0,
            "grounding_score": 0.0,
            "answer_status": "insufficient_evidence",
            "missing_documents": [],
            "contradictions": [],
            "reasoning_notes": "Retrieval returned no results or confidence too low.",
            "sources": [],
        }

    def _extract_summary(self, answer: str) -> str:
        """Heuristic to extract summary from structured LLM response."""
        match = re.search(r"Summary:(.*?)(Analysis:|Conclusion:|Final Legal Answer:|$)", answer, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_citations(self, answer: str) -> list[str]:
        """Extract [Evidence X] style citations."""
        return list(set(re.findall(r"\[Evidence \d+\]", answer)))
