from app.domain.models import SearchResult
from app.domain.repositories.vector_store_repository import VectorStoreRepository
from app.domain.repositories.keyword_retriever import KeywordRetriever
from app.domain.repositories.retriever import Retriever


class HybridRetriever(Retriever):
    """
    Combines vector search and BM25 keyword search.
    """

    def __init__(
        self,
        vector_store: VectorStoreRepository,
        keyword_retriever: KeywordRetriever,
    ):
        self.vector_store = vector_store
        self.keyword_retriever = keyword_retriever
        self._build_keyword_index()

    def _build_keyword_index(self) -> None:
        """
        Build the keyword index using all indexed chunks.
        """
        chunks = self.vector_store.get_all_chunks()
        self.keyword_retriever.index(chunks)

    def retrieve(
        self,
        query: str,
        k: int = 5,
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
                    chunk=chunk,
                    score=0.0,
                    rank=next_rank,
                )
            )

            existing_chunk_ids.add(chunk.chunk_id)
            next_rank += 1

        return merged_results[:k]
