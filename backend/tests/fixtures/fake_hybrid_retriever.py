from typing import Any, Dict, Optional

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
        self.params_received: list[Dict[str, Any] | None] = []

    async def retrieve(
        self, query: str, k: int, params: Dict[str, Any] | None = None
    ) -> list[SearchResult]:
        self.queries.append(query)
        self.k_values.append(k)
        self.params_received.append(params)

        return self.results
