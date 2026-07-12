from typing import Any, Dict, Optional

from app.domain.models import SearchResult
from app.domain.repositories.keyword_retriever import KeywordRetriever
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.vector_store_repository import VectorStoreRepository


class HybridRetrieverAdapter(Retriever):
    """
    Adapter that combines vector search and BM25 keyword search.
    Supports dynamic weights via params.
    """

    def __init__(
        self,
        vector_store: VectorStoreRepository,
        keyword_retriever: KeywordRetriever,
        vector_weight: float = 0.7,
        similarity_threshold: float = 0.0,
    ):
        self.vector_store = vector_store
        self.keyword_retriever = keyword_retriever
        self.vector_weight = vector_weight
        self.similarity_threshold = similarity_threshold
        self._build_keyword_index()

    def _build_keyword_index(self) -> None:
        """
        Build the keyword index using all indexed chunks.
        """
        chunks = self.vector_store.get_all_chunks()
        if chunks:
            self.keyword_retriever.index(chunks)

    def retrieve(
        self, query: str, k: int = 5, params: Optional[Dict[str, Any]] = None
    ) -> list[SearchResult]:
        """
        Retrieve using both vector search and BM25.
        """

        vector_results = self.vector_store.similarity_search(
            query=query,
            k=k,
        )

        bm25_chunks = self.keyword_retriever.search(
            query=query,
            k=k,
        )

        merged_results = list(vector_results)
        existing_chunk_ids = {result.chunk.chunk_id for result in merged_results}

        next_rank = len(merged_results) + 1

        for chunk in bm25_chunks:
            if chunk.chunk_id in existing_chunk_ids:
                continue

            merged_results.append(
                SearchResult(
                    chunk=chunk, score=0.0, rank=next_rank, retrieval_score=0.0
                )
            )

            existing_chunk_ids.add(chunk.chunk_id)
            next_rank += 1

        # Filter by threshold
        if self.similarity_threshold > 0:
            merged_results = [
                r for r in merged_results if r.score >= self.similarity_threshold
            ]

        return merged_results[:k]
