from abc import ABC, abstractmethod


class EmbeddingRepository(ABC):
    """
    Repository contract for embedding generation.
    """

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Create embeddings for a batch of texts."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Create an embedding for a single query."""
