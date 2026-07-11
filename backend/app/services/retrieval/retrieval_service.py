import time
from typing import List, Dict, Any, Tuple, Optional
from app.domain.models import SearchResult, Chunk
from app.domain.models.retrieval import QueryUnderstanding, QueryIntent, RetrievalDiagnostics
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.reranker import Reranker
from app.core.observability.metrics import MetricsRegistry


class RetrievalService(Retriever):
    """
    Advanced Retrieval Service with dynamic strategies and diagnostics.
    """

    def __init__(
        self,
        retriever: Retriever,
        reranker: Reranker,
        metrics: MetricsRegistry,
        candidate_multiplier: int = 4,
        min_candidates: int = 20,
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.metrics = metrics
        self.candidate_multiplier = candidate_multiplier
        self.min_candidates = min_candidates
        self.last_diagnostics: Optional[RetrievalDiagnostics] = None

    def retrieve(
        self,
        query: str,
        k: int = 5,
        params: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Implementation for general Retriever interface.
        If params contains QueryUnderstanding, it uses intelligent retrieval.
        """
        if params and "understanding" in params:
            return self.retrieve_intelligent(params["understanding"], k)

        # Fallback to standard retrieval
        return self._retrieve_standard(query, k)

    def retrieve_intelligent(
        self,
        understanding: QueryUnderstanding,
        k: int = 5
    ) -> List[SearchResult]:
        """
        Perform retrieval based on query understanding.
        """
        start_time = time.perf_counter()

        # 1. Calculate Dynamic Top-K (Phase 7.3.4)
        dynamic_k = self._calculate_dynamic_top_k(understanding, k)

        # 2. Determine Dynamic Strategy & Weights (Phase 7.3.3)
        strategy, weights = self._determine_strategy(understanding)

        # 3. Expanded Query
        expanded_query = understanding.original_query
        if understanding.expanded_terms:
            expanded_query += " " + " ".join(understanding.expanded_terms)

        # 4. Initial Retrieval
        candidate_count = max(
            dynamic_k * self.candidate_multiplier,
            self.min_candidates,
        )

        candidates = self.retriever.retrieve(
            query=expanded_query,
            k=candidate_count,
            params={"vector_weight": weights.get("vector", 0.7)}
        )

        # 5. Reranking
        reranked_results = self.reranker.rerank(
            query=understanding.original_query,
            results=candidates,
            k=dynamic_k,
        )

        # 6. Duplicate Evidence Removal (Phase 7.3.5)
        filtered_results = self._remove_duplicates(reranked_results)

        # 7. Ensure Diversity (Phase 7.3.6)
        final_results = filtered_results[:k]

        latency = (time.perf_counter() - start_time) * 1000

        # 8. Record Diagnostics (Phase 7.3.10)
        self.last_diagnostics = RetrievalDiagnostics(
            query_type=understanding.intent.value,
            retrieval_strategy=strategy,
            expanded_terms=understanding.expanded_terms,
            dynamic_top_k=dynamic_k,
            documents_considered=len(candidates),
            documents_selected=len(final_results),
            duplicate_chunks_removed=len(reranked_results) - len(filtered_results),
            context_compression_ratio=0.0, # To be filled by context builder if needed
            retrieval_latency_ms=latency,
            evidence_diversity_score=self._calculate_diversity(final_results),
            hybrid_weights=weights
        )

        self.metrics.track_retrieval(strategy, latency / 1000)

        return final_results

    def _retrieve_standard(self, query: str, k: int) -> List[SearchResult]:
        candidates = self.retriever.retrieve(query=query, k=k*self.candidate_multiplier)
        return self.reranker.rerank(query=query, results=candidates, k=k)

    def _calculate_dynamic_top_k(self, understanding: QueryUnderstanding, k: int) -> int:
        dynamic_k = k
        if understanding.is_multi_doc or understanding.intent == QueryIntent.COMPARISON:
            dynamic_k = int(k * 1.5)
        if understanding.intent == QueryIntent.SUMMARY:
            dynamic_k = k * 2
        return min(dynamic_k, 15) # Cap it

    def _determine_strategy(self, understanding: QueryUnderstanding) -> Tuple[str, Dict[str, float]]:
        weights = {"vector": 0.7, "bm25": 0.3}
        strategy = "hybrid_standard"

        if understanding.intent == QueryIntent.DEFINITION:
            weights = {"vector": 0.9, "bm25": 0.1}
            strategy = "semantic_heavy"
        elif understanding.intent == QueryIntent.CLAUSE_LOOKUP:
            weights = {"vector": 0.4, "bm25": 0.6}
            strategy = "keyword_heavy"

        return strategy, weights

    def _remove_duplicates(self, results: List[SearchResult]) -> List[SearchResult]:
        seen_texts = set()
        unique_results = []
        for res in results:
            # Simple exact match or high overlap check
            text_norm = res.chunk.text.strip().lower()[:200]
            if text_norm not in seen_texts:
                seen_texts.add(text_norm)
                unique_results.append(res)
        return unique_results

    def _calculate_diversity(self, results: List[SearchResult]) -> float:
        if not results: return 0.0
        doc_ids = {r.chunk.document_id for r in results}
        return len(doc_ids) / len(results)
