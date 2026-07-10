class EmbeddingService:
    """
    Generates embeddings for document chunks.
    """

    def __init__(
        self,
        model=None,
    ):
        if model is None:
            from app.di import get_embedding_model

            self.model = get_embedding_model()
        else:
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
