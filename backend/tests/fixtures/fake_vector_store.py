from app.domain.models.chunk import Chunk
from app.domain.models.search_result import SearchResult
from app.domain.repositories.vector_store_repository import VectorStoreRepository


class FakeVectorStore(VectorStoreRepository):
    """
    Fake VectorStoreRepository for unit tests.
    """

    def __init__(
        self,
        chunks: list[Chunk] | None = None,
        search_results: list[SearchResult] | None = None,
    ):
        self._chunks = chunks if chunks is not None else []
        self._search_results = search_results if search_results is not None else []

    def create(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks

    def save(self) -> None:
        pass

    def load(self) -> bool:
        return True

    def get_all_chunks(self) -> list[Chunk]:
        return self._chunks

    def similarity_search(self, query: str, k: int = 3) -> list[SearchResult]:
        return self._search_results[:k]
