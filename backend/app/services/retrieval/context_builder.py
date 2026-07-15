import math
import re
from typing import List, Set

from app.domain.models import Evidence, SearchResult
from app.domain.repositories.context_builder import ContextBuilder as IContextBuilder


class ContextBuilder(IContextBuilder):
    """
    Builds LLM context with diversity optimization, Dynamic Pruning, and compression.
    Optimized for Token Efficiency and Relevance (10.5.3).
    """

    def __init__(self, max_tokens_per_chunk: int = 500):
        self.max_tokens_per_chunk = max_tokens_per_chunk

    def build(
        self,
        results: list[SearchResult],
        query: str | None = None
    ) -> str:
        """
        Convert retrieval results into a compressed context string.
        Optionally uses the query to prune less relevant sentences (10.5.3).
        """

        if not results:
            return ""

        # 1. Evidence Diversity (7.3.6)
        # Re-sort results to ensure document diversity if they have similar scores
        results = self._ensure_diversity(results)

        context_parts: list[str] = []

        # Extract query keywords for dynamic pruning
        keywords = self._extract_keywords(query) if query else set()

        for i, result in enumerate(results, start=1):
            metadata = result.chunk.metadata

            # 2. Dynamic Pruning (10.5.3)
            # Focus on sentences most relevant to the query keywords
            pruned_text = self._dynamic_prune(result.chunk.text, keywords)

            # 3. Context Compression (7.3.8)
            compressed_text = self._compress_text(pruned_text)

            context_parts.append(
                f"--- [Evidence {i}] ---\n"
                f"Source: {metadata.filename} (Page {metadata.page_number})\n"
                f"Excerpt: {compressed_text}\n"
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
                    rank=i,
                )
            )
        return evidence_list

    def _ensure_diversity(self, results: list[SearchResult]) -> list[SearchResult]:
        """Ensures that many results from the same document don't crowd out others."""
        if len(results) <= 3:
            return results

        diversified = []
        doc_groups = {}
        for r in results:
            doc_id = r.chunk.document_id
            if doc_id not in doc_groups:
                doc_groups[doc_id] = []
            doc_groups[doc_id].append(r)

        # Round-robin selection
        max_depth = max(len(g) for g in doc_groups.values())
        for d in range(max_depth):
            for doc_id in list(doc_groups.keys()):
                if d < len(doc_groups[doc_id]):
                    diversified.append(doc_groups[doc_id][d])
            if len(diversified) >= len(results):
                break

        return diversified

    def _dynamic_prune(self, text: str, keywords: Set[str]) -> str:
        """
        Keeps sentences that have keyword matches or are adjacent to them.
        Reduces context window "noise" while preserving coherence (10.5.3).
        """
        if not keywords:
            return text

        sentences = re.split(r'(?<=[.!?])\s+', text)
        relevant_indices = set()

        for i, s in enumerate(sentences):
            s_lower = s.lower()
            if any(k in s_lower for k in keywords):
                relevant_indices.add(i)
                # Keep surrounding context for coherence
                if i > 0: relevant_indices.add(i-1)
                if i < len(sentences) - 1: relevant_indices.add(i+1)

        if not relevant_indices:
            return text # Fallback to original if no match found

        pruned_sentences = []
        sorted_indices = sorted(list(relevant_indices))

        last_idx = -1
        for idx in sorted_indices:
            if last_idx != -1 and idx > last_idx + 1:
                pruned_sentences.append("[...]")
            pruned_sentences.append(sentences[idx])
            last_idx = idx

        return " ".join(pruned_sentences)

    def _compress_text(self, text: str) -> str:
        """
        Removes boilerplate, redundant whitespace, and duplicate sentences.
        """
        # Remove repetitive boilerplate
        text = re.sub(r"(CONFIDENTIAL\s*)+", "CONFIDENTIAL ", text)
        text = re.sub(r"(DRAFT\s*)+", "DRAFT ", text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Simple sentence deduplication (already handled by pruning logic mostly)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        unique_sentences = []
        seen = set()
        for s in sentences:
            s_clean = s.strip().lower()
            if s_clean not in seen and len(s_clean) > 5:
                seen.add(s_clean)
                unique_sentences.append(s)

        return " ".join(unique_sentences)

    def _extract_keywords(self, query: str) -> Set[str]:
        """Simple keyword extractor for pruning."""
        # Stopwords (minimal set for legal context)
        stop_words = {"the", "a", "an", "and", "or", "but", "if", "then", "at", "by", "from", "for", "to", "in", "of", "is", "was", "be"}
        words = re.findall(r"\w+", query.lower())
        return {w for w in words if w not in stop_words and len(w) > 2}

    def _calculate_confidence(self, result: SearchResult) -> float:
        if result.reranker_score is not None:
            # Simple sigmoid for CrossEncoder score normalization
            return 1 / (1 + math.exp(-result.reranker_score))
        if result.retrieval_score is not None:
            return max(0.0, min(1.0, result.retrieval_score))
        return 0.0
