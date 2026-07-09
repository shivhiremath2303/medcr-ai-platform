from sentence_transformers import CrossEncoder

from app.models.search_result import SearchResult


class Reranker:
    """
    Reranks retrieval results using a CrossEncoder model.
    """

    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self):
        self.model = CrossEncoder(
            self.MODEL_NAME,
        )

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        k: int,
    ) -> list[SearchResult]:
        """
        Rerank retrieval results.
        """

        if not results:
            return []

        pairs = [
            (
                query,
                result.chunk.text,
            )
            for result in results
        ]

        scores = self.model.predict(pairs)

        for result, score in zip(results, scores):
            result.score = float(score)

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        for rank, result in enumerate(results, start=1):
            result.rank = rank

        return results[:k]
