import re
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.query_rewriter import QueryRewriter
from app.domain.repositories.context_builder import ContextBuilder
from app.services.rag.grounding_engine import GroundingEngine
from app.services.rag.reasoning_engine import ReasoningEngine
from app.core.observability.logger import get_logger

logger = get_logger(__name__)

class RAGService:
    """
    Coordinates the advanced Retrieval-Augmented Generation workflow with deep legal reasoning.
    """

    def __init__(
        self,
        retrieval_service: Retriever,
        llm_provider: LLMProvider,
        query_rewriter: QueryRewriter,
        memory: ConversationRepository,
        context_builder: ContextBuilder,
        grounding_engine: GroundingEngine,
        reasoning_engine: ReasoningEngine,
    ):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.query_rewriter = query_rewriter
        self.memory = memory
        self.context_builder = context_builder
        self.grounding_engine = grounding_engine
        self.reasoning_engine = reasoning_engine

    def answer_question(
        self,
        question: str,
        k: int = 3,
    ) -> dict:
        """
        Retrieve context using intelligent retrieval, generate an answer with deep reasoning, and return detailed diagnostics.
        """

        # Store the user's question
        self.memory.add_user_message(question)

        # Get conversation history
        memory_context = self.memory.get_context()

        # Phase 7.3.1: Legal Query Understanding
        understanding = self.query_rewriter.understand_query(
            question=question,
            conversation_context=memory_context,
        )

        # Retrieve relevant chunks using intelligent retrieval
        results = self.retrieval_service.retrieve(
            query=understanding.original_query,
            k=k,
            params={"understanding": understanding}
        )

        # 1. Evidence Sufficiency Analysis
        raw_confidence = sum(r.score for r in results[:1]) if results else 0.0
        sufficiency = self.grounding_engine.analyze_sufficiency(results, raw_confidence)

        if not results or sufficiency == "insufficient":
             return self._generate_insufficient_response()

        # Convert results to structured Evidence objects
        evidence_list = self.context_builder.results_to_evidence(results)

        # Build LLM context
        context = self.context_builder.build(results)

        # 2. Grounded Answer Generation with Deep Reasoning
        answer = self.llm_provider.generate_answer(
            question=question,
            context=context,
        )

        # Store assistant response
        self.memory.add_assistant_message(answer)

        # 3. Hallucination Detection & Verification
        validation_errors = self.grounding_engine.validate_answer(answer, evidence_list)

        summary = self._extract_summary(answer)
        citations = self._extract_citations(answer)
        contradictions = self.grounding_engine.detect_contradictions(answer)
        missing_docs = self.grounding_engine.detect_missing_evidence(answer)

        # 4. Structured Reasoning Extraction (Phase 7.4.8)
        reasoning_metadata = self.reasoning_engine.extract_reasoning(answer, evidence_list)

        # 5. Grounding Score Calculation
        grounding_score = self.grounding_engine.calculate_grounding_score(
            evidence_list=evidence_list,
            citations=citations,
            sufficiency=sufficiency,
            contradictions=contradictions
        )

        # 6. Answer Status Categorization
        status = self.grounding_engine.determine_status(
            answer=answer,
            sufficiency=sufficiency,
            grounding_score=grounding_score,
            contradictions=contradictions
        )

        # 7. Get Retrieval Diagnostics
        diagnostics = None
        if hasattr(self.retrieval_service, "last_diagnostics"):
            diagnostics = self.retrieval_service.last_diagnostics

        # Build source list (for backward compatibility)
        sources = [
            {
                "filename": ev.document_name,
                "page_number": ev.page_number,
            }
            for ev in evidence_list
        ]

        response_data = {
            "answer": answer,
            "summary": summary,
            "citations": citations,
            "evidence": evidence_list,
            "confidence": raw_confidence,
            "grounding_score": grounding_score,
            "answer_status": status.value,
            "missing_documents": missing_docs,
            "contradictions": contradictions,
            "reasoning_notes": f"Validation Errors: {', '.join(validation_errors)}" if validation_errors else None,
            "reasoning_metadata": reasoning_metadata.__dict__,
            "sources": sources,
        }

        if diagnostics:
            response_data["retrieval_diagnostics"] = diagnostics.__dict__

        return response_data

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
            "reasoning_metadata": None,
            "sources": [],
        }

    def _extract_summary(self, answer: str) -> str:
        match = re.search(r"### Summary(.*?)(###|$)", answer, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_citations(self, answer: str) -> list[str]:
        return list(set(re.findall(r"\[Evidence \d+\]", answer)))
