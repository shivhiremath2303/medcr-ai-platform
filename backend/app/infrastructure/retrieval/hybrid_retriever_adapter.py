import asyncio
from typing import Any, Dict, List, Optional

from app.domain.models import SearchResult
from app.domain.repositories.keyword_retriever import KeywordRetriever
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.vector_store_repository import VectorStoreRepository


class HybridRetrieverAdapter(Retriever):
    """
    Adapter that combines vector search and BM25 keyword search.
    Updated to support async horizontal scaling (10.3.3).
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
        # Note: Indexing happens in background via Worker in Phase 10.3.2
        # but we need initial sync for simple deployments.

    async def retrieve(
        self, query: str, k: int = 5, params: Dict[str, Any] | None = None
    ) -> List[SearchResult]:
        """
        Retrieve using both vector search and BM25 in parallel (10.3.3).
        """
        # Execute vector and keyword search concurrently
        vector_task = self.vector_store.similarity_search(query=query, k=k)

        # Keyword retriever might be sync, so wrap in task if needed or await
        # Assuming BM25 is fast and CPU-bound, but for consistency we'll await
        bm25_task = self.keyword_retriever.search(query=query, k=k)

        # In a real async implementation, keyword_retriever would also be async
        if asyncio.iscoroutine(bm25_task):
            vector_results, bm25_chunks = await asyncio.gather(vector_task, bm25_task)
        else:
            vector_results = await vector_task
            bm25_chunks = bm25_task

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

        if self.similarity_threshold > 0:
            merged_results = [
                r for r in merged_results if r.score >= self.similarity_threshold
            ]

        return merged_results[:k]
