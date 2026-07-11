from app.domain.models import SearchResult, Evidence
from app.domain.repositories.context_builder import ContextBuilder as IContextBuilder

class ContextBuilder(IContextBuilder):
    """
    Builds LLM context from retrieval results.

    This service is responsible only for transforming
    retrieval results into prompt-ready context.
    """

    def build(
        self,
        results: list[SearchResult],
    ) -> str:
        """
        Convert retrieval results into a context string with explicit evidence IDs.
        """

        if not results:
            return ""

        context_parts: list[str] = []

        for i, result in enumerate(results, start=1):
            metadata = result.chunk.metadata

            # We use [Evidence X] as a marker for the LLM to use in citations
            context_parts.append(
                (
                    f"--- [Evidence {i}] ---\n"
                    f"Source Document: {metadata.filename}\n"
                    f"Page: {metadata.page_number}\n"
                    f"Excerpt:\n{result.chunk.text}\n"
                )
            )

        return "\n".join(context_parts)

    def results_to_evidence(self, results: list[SearchResult]) -> list[Evidence]:
        """
        Convert search results to domain Evidence objects and calculate confidence.
        """
        evidence_list = []

        for i, result in enumerate(results, start=1):
            # Simple confidence calculation based on available scores
            # If reranker_score is available (usually [0, 1] or similar), use it.
            # Otherwise use retrieval_score.

            score = result.reranker_score if result.reranker_score is not None else result.retrieval_score

            # Normalize confidence to [0, 1] if needed.
            # CrossEncoder scores are typically not [0, 1] but logits.
            # FAISS relevance scores are usually [0, 1].

            confidence = self._calculate_confidence(result)

            evidence_list.append(
                Evidence(
                    document_id=result.chunk.document_id,
                    document_name=result.chunk.metadata.filename,
                    page_number=result.chunk.metadata.page_number,
                    chunk_id=result.chunk.chunk_id,
                    chunk_text=result.chunk.text,
                    retrieval_score=result.retrieval_score or 0.0,
                    reranker_score=result.reranker_score,
                    confidence=confidence,
                    rank=i
                )
            )

        return evidence_list

    def _calculate_confidence(self, result: SearchResult) -> float:
        """
        Heuristic confidence calculation.
        """
        if result.reranker_score is not None:
            # CrossEncoder ms-marco-MiniLM-L-6-v2 typically outputs values
            # where > 0 is somewhat relevant, > 5 is very relevant.
            # We can use a sigmoid or simple scaling.
            import math
            # Simple sigmoid to map logit-like scores to [0, 1]
            return 1 / (1 + math.exp(-result.reranker_score))

        if result.retrieval_score is not None:
            # LangChain FAISS relevance scores are already [0, 1] (1 - distance/2 roughly)
            return max(0.0, min(1.0, result.retrieval_score))

        return 0.0
