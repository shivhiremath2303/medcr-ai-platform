import asyncio
from typing import List

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.observability.concurrency import ConcurrencyLimiter
from app.domain.repositories.embedding_repository import EmbeddingRepository


class HuggingFaceEmbeddingAdapter(EmbeddingRepository, Embeddings):
    """
    Adapter for Hugging Face Sentence-Transformers with Scaling Support.
    Offloads CPU-bound embedding generation to a dedicated thread pool.
    Implements Milestone 10.3.3.
    """

    def __init__(
        self, model_name: str, limiter: ConcurrencyLimiter, device: str = "cpu"
    ):
        self.model = HuggingFaceEmbeddings(
            model_name=model_name, model_kwargs={"device": device}
        )
        self.limiter = limiter

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Sync version (fallback)
        return self.model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        # Sync version (fallback)
        return self.model.embed_query(text)

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async implementation offloading to thread pool."""
        return await self.limiter.run_in_thread(self.model.embed_documents, texts)

    async def aembed_query(self, text: str) -> List[float]:
        """Async implementation offloading to thread pool."""
        return await self.limiter.run_in_thread(self.model.embed_query, text)
