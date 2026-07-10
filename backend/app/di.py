from __future__ import annotations

from google import genai
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.core.constants import EMBEDDING_MODEL
from app.services.document.document_service import DocumentService
from app.services.document.embeddings import EmbeddingService
from app.services.document.vector_store import VectorStoreService
from app.services.llm.llm_service import LLMService
from app.services.rag.conversation_memory import ConversationMemory
from app.services.rag.query_rewriter import QueryRewriter
from app.services.rag.rag_service import RAGService
from app.services.retrieval.bm25_retriever import BM25Retriever
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.hybrid_retriever import HybridRetriever
from app.services.retrieval.retrieval_service import RetrievalService
from app.services.retrieval.reranker import Reranker
from app.services.storage.file_storage import FileStorageService


class AppContainer:
    def __init__(self) -> None:
        self._settings = settings
        self._storage_service: FileStorageService | None = None
        self._genai_client: genai.Client | None = None
        self._embedding_model: HuggingFaceEmbeddings | None = None
        self._embedding_service: EmbeddingService | None = None
        self._vector_store: VectorStoreService | None = None
        self._cross_encoder_model: CrossEncoder | None = None
        self._reranker: Reranker | None = None

    def get_settings(self):
        return self._settings

    def get_storage_service(self) -> FileStorageService:
        if self._storage_service is None:
            self._storage_service = FileStorageService()
        return self._storage_service

    def get_genai_client(self) -> genai.Client:
        if self._genai_client is None:
            self._genai_client = genai.Client(api_key=self._settings.gemini_api_key)
        return self._genai_client

    def get_embedding_model(self) -> HuggingFaceEmbeddings:
        if self._embedding_model is None:
            self._embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        return self._embedding_model

    def get_embedding_service(self) -> EmbeddingService:
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService(model=self.get_embedding_model())
        return self._embedding_service

    def get_vector_store(self) -> VectorStoreService:
        if self._vector_store is None:
            self._vector_store = VectorStoreService(
                embedding_service=self.get_embedding_service(),
            )
        return self._vector_store

    def get_cross_encoder_model(self) -> CrossEncoder:
        if self._cross_encoder_model is None:
            self._cross_encoder_model = CrossEncoder(Reranker.MODEL_NAME)
        return self._cross_encoder_model

    def get_reranker(self) -> Reranker:
        if self._reranker is None:
            self._reranker = Reranker(model=self.get_cross_encoder_model())
        return self._reranker

    def get_bm25_retriever(self) -> BM25Retriever:
        return BM25Retriever()

    def get_hybrid_retriever(self) -> HybridRetriever:
        return HybridRetriever(
            vector_store=self.get_vector_store(),
            bm25=self.get_bm25_retriever(),
        )

    def get_retrieval_service(self) -> RetrievalService:
        return RetrievalService(
            retriever=self.get_hybrid_retriever(),
            reranker=self.get_reranker(),
        )

    def get_llm_service(self) -> LLMService:
        return LLMService(client=self.get_genai_client())

    def get_document_service(self) -> DocumentService:
        return DocumentService(vector_store=self.get_vector_store())

    def get_conversation_memory(self) -> ConversationMemory:
        return ConversationMemory()

    def get_context_builder(self) -> ContextBuilder:
        return ContextBuilder()

    def get_query_rewriter(self) -> QueryRewriter:
        return QueryRewriter(llm_service=self.get_llm_service())

    def get_rag_service(self) -> RAGService:
        return RAGService(
            retrieval_service=self.get_retrieval_service(),
            context_builder=self.get_context_builder(),
            llm_service=self.get_llm_service(),
            memory=self.get_conversation_memory(),
            query_rewriter=self.get_query_rewriter(),
        )

    def init_vector_store(self) -> bool:
        try:
            return self.get_vector_store().load()
        except Exception:
            return False

    def shutdown_vector_store_save(self) -> None:
        try:
            self.get_vector_store().save()
        except Exception:
            pass


_container = AppContainer()


def get_settings():
    return _container.get_settings()


def get_storage_service() -> FileStorageService:
    return _container.get_storage_service()


def get_genai_client() -> genai.Client:
    return _container.get_genai_client()


def get_embedding_model() -> HuggingFaceEmbeddings:
    return _container.get_embedding_model()


def get_embedding_service() -> EmbeddingService:
    return _container.get_embedding_service()


def get_vector_store() -> VectorStoreService:
    return _container.get_vector_store()


def get_reranker() -> Reranker:
    return _container.get_reranker()


def get_bm25_retriever() -> BM25Retriever:
    return _container.get_bm25_retriever()


def get_hybrid_retriever() -> HybridRetriever:
    return _container.get_hybrid_retriever()


def get_retrieval_service() -> RetrievalService:
    return _container.get_retrieval_service()


def get_llm_service() -> LLMService:
    return _container.get_llm_service()


def get_document_service() -> DocumentService:
    return _container.get_document_service()


def get_conversation_memory() -> ConversationMemory:
    return _container.get_conversation_memory()


def get_context_builder() -> ContextBuilder:
    return _container.get_context_builder()


def get_query_rewriter() -> QueryRewriter:
    return _container.get_query_rewriter()


def get_rag_service() -> RAGService:
    return _container.get_rag_service()


def init_vector_store() -> bool:
    return _container.init_vector_store()


def shutdown_vector_store_save() -> None:
    _container.shutdown_vector_store_save()
