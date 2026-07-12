from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from app.domain.repositories.embedding_repository import EmbeddingRepository


class HuggingFaceEmbeddingAdapter(EmbeddingRepository, Embeddings):
    """
    Adapter for Hugging Face Sentence-Transformers using LangChain.
    """

    def __init__(self, model_name: str, device: str = "cpu"):
        self.model = HuggingFaceEmbeddings(
            model_name=model_name, model_kwargs={"device": device}
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.model.embed_query(text)
