from app.models.search_result import SearchResult


class FakeReranker:
    """
    Fake Reranker for unit tests.
    """

    def __init__(
        self,
        results: list[SearchResult] | None = None,
    ):
        self.results = results if results is not None else []

        self.queries: list[str] = []
        self.received_results: list[list[SearchResult]] = []
        self.k_values: list[int] = []

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        k: int,
    ) -> list[SearchResult]:
        self.queries.append(query)
        self.received_results.append(results)
        self.k_values.append(k)

        return self.results
