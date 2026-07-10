from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from app.core.constants import EMBEDDING_MODEL
from app.domain.repositories.embedding_repository import EmbeddingRepository


class HuggingFaceEmbeddingAdapter(EmbeddingRepository, Embeddings):
    """
    Adapter for HuggingFace embeddings using LangChain.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = HuggingFaceEmbeddings(
            model_name=model_name,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.model.embed_query(text)
