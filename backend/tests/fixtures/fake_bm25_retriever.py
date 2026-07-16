from app.domain.models.chunk import Chunk
from app.domain.repositories.keyword_retriever import KeywordRetriever


class FakeBM25Retriever(KeywordRetriever):
    """
    Fake BM25 retriever for unit tests.
    """

    def __init__(
        self,
        search_results: list[Chunk] | None = None,
    ):
        self.chunks: list[Chunk] = []
        self.search_queries: list[str] = []
        self._search_results = search_results if search_results is not None else []

    async def index(
        self,
        chunks: list[Chunk],
    ) -> None:
        self.chunks = list(chunks)

    async def search(
        self,
        query: str,
        k: int = 5,
        tenant_id: str | None = None,
    ) -> list[Chunk]:
        self.search_queries.append(query)
        return self._search_results[:k]
