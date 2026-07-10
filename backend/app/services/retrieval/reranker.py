from sentence_transformers import CrossEncoder

from app.domain.models import SearchResult

class Reranker:
    """
    Reranks retrieval results using a CrossEncoder model.
    """

    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self, model: CrossEncoder):
        """
        Require an injected CrossEncoder model. The composition root provides
        the shared model instance.
        """
        self.model = model

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
