import re
import math
from app.domain.models import SearchResult, Evidence
from app.domain.repositories.context_builder import ContextBuilder as IContextBuilder

class ContextBuilder(IContextBuilder):
    """
    Builds LLM context with diversity optimization and compression.
    """

    def build(
        self,
        results: list[SearchResult],
    ) -> str:
        """
        Convert retrieval results into a compressed context string.
        """

        if not results:
            return ""

        # Phase 7.3.6: Evidence Diversity
        # Re-sort results to ensure document diversity if they have similar scores
        results = self._ensure_diversity(results)

        context_parts: list[str] = []

        for i, result in enumerate(results, start=1):
            metadata = result.chunk.metadata

            # Phase 7.3.8: Context Compression
            compressed_text = self._compress_text(result.chunk.text)

            context_parts.append(
                f"--- [Evidence {i}] ---\n"
                f"Source Document: {metadata.filename}\n"
                f"Page: {metadata.page_number}\n"
                f"Excerpt:\n{compressed_text}\n"
            )

        return "\n".join(context_parts)

    def results_to_evidence(self, results: list[SearchResult]) -> list[Evidence]:
        evidence_list = []
        for i, result in enumerate(results, start=1):
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

    def _ensure_diversity(self, results: list[SearchResult]) -> list[SearchResult]:
        """Ensures that many results from the same document don't crowd out others."""
        if len(results) <= 3: return results

        diversified = []

        # Round-robin like selection from doc groups
        doc_groups = {}
        for r in results:
            doc_id = r.chunk.document_id
            if doc_id not in doc_groups: doc_groups[doc_id] = []
            doc_groups[doc_id].append(r)

        # Limit to max 2 chunks per doc initially
        for _ in range(max(len(g) for g in doc_groups.values())):
            for doc_id in list(doc_groups.keys()):
                if doc_groups[doc_id]:
                    diversified.append(doc_groups[doc_id].pop(0))

        return diversified

    def _compress_text(self, text: str) -> str:
        """
        Removes boilerplate and redundant sentences.
        """
        # Remove repetitive boilerplate (e.g. multiple "CONFIDENTIAL")
        text = re.sub(r"(CONFIDENTIAL\s*)+", "CONFIDENTIAL ", text)

        # Remove multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Simple sentence deduplication
        sentences = text.split(". ")
        unique_sentences = []
        seen = set()
        for s in sentences:
            s_clean = s.strip().lower()
            if s_clean not in seen and len(s_clean) > 5:
                seen.add(s_clean)
                unique_sentences.append(s)

        return ". ".join(unique_sentences)

    def _calculate_confidence(self, result: SearchResult) -> float:
        if result.reranker_score is not None:
            return 1 / (1 + math.exp(-result.reranker_score))
        if result.retrieval_score is not None:
            return max(0.0, min(1.0, result.retrieval_score))
        return 0.0
