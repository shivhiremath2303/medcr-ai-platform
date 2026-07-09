from app.models.search_result import SearchResult


class FakeHybridRetriever:
    """
    Fake HybridRetriever for unit tests.
    """

    def __init__(
        self,
        results: list[SearchResult],
    ):
        self.results = results

        self.queries: list[str] = []
        self.k_values: list[int] = []

    def retrieve(
        self,
        query: str,
        k: int,
    ) -> list[SearchResult]:
        self.queries.append(query)
        self.k_values.append(k)

        return self.results
