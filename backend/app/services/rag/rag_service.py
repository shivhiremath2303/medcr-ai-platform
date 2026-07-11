import re
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.query_rewriter import QueryRewriter
from app.domain.repositories.context_builder import ContextBuilder
from app.core.observability.logger import get_logger

logger = get_logger(__name__)

class RAGService:
    """
    Coordinates the Retrieval-Augmented Generation workflow with Evidence tracking.
    """

    def __init__(
        self,
        retrieval_service: Retriever,
        llm_provider: LLMProvider,
        query_rewriter: QueryRewriter,
        memory: ConversationRepository,
        context_builder: ContextBuilder,
    ):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.query_rewriter = query_rewriter
        self.memory = memory
        self.context_builder = context_builder

    def answer_question(
        self,
        question: str,
        k: int = 3,
    ) -> dict:
        """
        Retrieve context, generate an answer and return detailed evidence and citations.
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

        if not results:
            return {
                "answer": "No supporting evidence was found in the uploaded legal documents.",
                "summary": "No evidence found.",
                "citations": [],
                "evidence": [],
                "confidence": 0.0,
                "sources": [],
            }

        # Convert results to structured Evidence objects
        evidence_list = self.context_builder.results_to_evidence(results)

        # Build LLM context
        context = self.context_builder.build(results)

        # Generate answer
        answer = self.llm_provider.generate_answer(
            question=question,
            context=context,
        )

        # Store assistant response
        self.memory.add_assistant_message(answer)

        # Extract summary from LLM response if possible (heuristic based on prompt structure)
        summary = self._extract_summary(answer)

        # Extract citations used in the answer
        citations = self._extract_citations(answer)

        # Filter evidence to only those cited (optional, but requested by some users)
        # For now, we return all retrieved evidence as they are context.

        # Calculate overall confidence (average of cited evidence or top evidence)
        overall_confidence = self._calculate_overall_confidence(evidence_list, citations)

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
            "confidence": overall_confidence,
            "sources": sources,
        }

    def _extract_summary(self, answer: str) -> str:
        """Heuristic to extract summary from structured LLM response."""
        match = re.search(r"Summary:(.*?)(Analysis:|Conclusion:|$)", answer, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_citations(self, answer: str) -> list[str]:
        """Extract [Evidence X] style citations."""
        return list(set(re.findall(r"\[Evidence \d+\]", answer)))

    def _calculate_overall_confidence(self, evidence_list: list, citations: list[str]) -> float:
        """Calculate overall confidence score."""
        if not evidence_list:
            return 0.0

        if not citations:
            # If no citations but we have evidence, maybe LLM didn't cite but context was relevant
            return sum(e.confidence for e in evidence_list[:1]) / 1.0

        # Map citations like "[Evidence 1]" back to index
        cited_indices = []
        for cit in citations:
            match = re.search(r"\d+", cit)
            if match:
                idx = int(match.group()) - 1
                if 0 <= idx < len(evidence_list):
                    cited_indices.append(idx)

        if not cited_indices:
            return sum(e.confidence for e in evidence_list[:1]) / 1.0

        cited_evidence = [evidence_list[i] for i in cited_indices]
        return sum(e.confidence for e in cited_evidence) / len(cited_evidence)
