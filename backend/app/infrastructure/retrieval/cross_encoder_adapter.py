from sentence_transformers import CrossEncoder
from app.domain.models import SearchResult
from app.domain.repositories.reranker import Reranker


class CrossEncoderAdapter(Reranker):
    """
    Adapter for CrossEncoder reranking.
    """

    def __init__(self, model_name: str):
        """
        Initialize with a model name.
        """
        self.model = CrossEncoder(model_name)

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
