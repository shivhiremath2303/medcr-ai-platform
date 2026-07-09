from app.models.chunk import Chunk
from app.models.search_result import SearchResult


class FakeVectorStore:
    """
    Fake VectorStoreService for unit tests.
    """

    def __init__(
        self,
        chunks: list[Chunk],
        search_results: list[SearchResult],
    ):
        self._chunks = chunks
        self._search_results = search_results

    def get_all_chunks(
        self,
    ) -> list[Chunk]:
        return self._chunks

    def similarity_search(
        self,
        query: str,
        k: int,
    ) -> list[SearchResult]:
        return self._search_results[:k]
