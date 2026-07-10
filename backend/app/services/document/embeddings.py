from langchain_huggingface import HuggingFaceEmbeddings

from app.core.constants import EMBEDDING_MODEL


class EmbeddingService:
    """
    Generates embeddings for document chunks.

    NOTE: Per DI rules the underlying embedding model must be provided by the
    composition root. Do not instantiate heavy models inside services.
    """

    def __init__(
        self,
        model,
    ):
        if model is None:
            raise ValueError("Embedding model must be provided via dependency injection")
        self.model = model

    def embed_documents(
        self,
        chunks: list[str],
    ) -> list[list[float]]:
        return self.model.embed_documents(chunks)

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        return self.model.embed_query(query)
