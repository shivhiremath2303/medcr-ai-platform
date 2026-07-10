from sentence_transformers import CrossEncoder
from app.domain.models import SearchResult
from app.domain.repositories.reranker import Reranker


class CrossEncoderAdapter(Reranker):
    """
    Adapter for CrossEncoder reranking.
    """

    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self, model: CrossEncoder | None = None):
        """
        Accept an injected CrossEncoder model. If none is provided, create one
        using the default MODEL_NAME. This allows the composition root to
        provide a shared model instance.
        """
        self.model = model if model is not None else CrossEncoder(self.MODEL_NAME)

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        k: int,
    ) -> list[SearchResult]:
        if not results:
            return []

        pairs = [(query, result.chunk.text) for result in results]
        scores = self.model.predict(pairs)

        for result, score in zip(results, scores):
            result.score = float(score)

        results.sort(key=lambda x: x.score, reverse=True)

        for rank, result in enumerate(results, start=1):
            result.rank = rank

        return results[:k]
