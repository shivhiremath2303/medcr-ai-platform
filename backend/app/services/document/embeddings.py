from langchain_huggingface import HuggingFaceEmbeddings

from app.core.constants import EMBEDDING_MODEL


class EmbeddingService:
    """
    Generates embeddings for document chunks.
    """

    def __init__(
        self,
        model=None,
    ):
        self.model = model or HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
        )

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
