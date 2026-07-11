from typing import Optional, Dict, Any
from app.domain.models.search_result import SearchResult


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
        self.params_received: list[Optional[Dict[str, Any]]] = []

    def retrieve(
        self,
        query: str,
        k: int,
        params: Optional[Dict[str, Any]] = None
    ) -> list[SearchResult]:
        self.queries.append(query)
        self.k_values.append(k)
        self.params_received.append(params)

        return self.results
