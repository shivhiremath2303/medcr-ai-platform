from app.domain.models import SearchResult
from app.services.document.vector_store import VectorStoreService
from app.services.retrieval.bm25_retriever import BM25Retriever


class HybridRetriever:
    """
    Combines vector search and BM25 keyword search.
    """

    def __init__(
        self,
        vector_store: VectorStoreService | None = None,
        bm25: BM25Retriever | None = None,
    ):
        """
        Initialize the hybrid retriever.

        Args:
            vector_store:
                Optional VectorStoreService.
                Mainly used for testing.

            bm25:
                Optional BM25Retriever.
                Mainly used for testing.
        """

        if vector_store is None:
            from app.di import get_vector_store

            self.vector_store = get_vector_store()

            loaded = self.vector_store.load()

            if not loaded:
                raise RuntimeError(
                    "No FAISS index found. Please ingest documents first."
                )
        else:
            self.vector_store = vector_store

        if bm25 is None:
            from app.di import get_bm25_retriever

            self.bm25 = get_bm25_retriever()
        else:
            self.bm25 = bm25

        self._build_bm25_index()

    # ----------------------------------------------------------
    # Index building
    # ----------------------------------------------------------

    def _build_bm25_index(
        self,
    ) -> None:
        """
        Build the BM25 index using all indexed chunks.
        """

        chunks = self.vector_store.get_all_chunks()

        self.bm25.index(chunks)

    # ----------------------------------------------------------
    # Retrieval
    # ----------------------------------------------------------

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

        bm25_chunks = self.bm25.search(
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
