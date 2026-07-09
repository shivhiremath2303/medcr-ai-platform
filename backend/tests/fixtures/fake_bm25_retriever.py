from app.models.chunk import Chunk


class FakeBM25Retriever:
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

    def index(
        self,
        chunks: list[Chunk],
    ) -> None:
        self.chunks = list(chunks)

    def search(
        self,
        query: str,
        k: int,
    ) -> list[Chunk]:
        self.search_queries.append(query)

        return self._search_results[:k]
