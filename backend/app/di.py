from fastapi import Depends

from google import genai
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings
from app.core.constants import EMBEDDING_MODEL
from app.services.rag.rag_service import RAGService
from app.services.document.document_service import DocumentService
from app.services.storage.file_storage import FileStorageService
from app.services.llm.llm_service import LLMService
from app.services.document.embeddings import EmbeddingService
from app.services.document.vector_store import VectorStoreService
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.hybrid_retriever import HybridRetriever
from app.services.retrieval.bm25_retriever import BM25Retriever
from app.services.retrieval.retrieval_service import RetrievalService

# Composition root / dependency providers
# Singleton storage service (filesystem adapter)
_storage_singleton = FileStorageService()

# Singleton genai client for Gemini
_genai_client_singleton = genai.Client(api_key=settings.gemini_api_key)

# Singleton embedding model (HuggingFace)
_hf_embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
_embedding_service_singleton = EmbeddingService(model=_hf_embedding_model)

# Singleton CrossEncoder model and Reranker
_cross_encoder_model = CrossEncoder(Reranker.MODEL_NAME)
_reranker_singleton = Reranker(model=_cross_encoder_model)

# Singleton VectorStoreService (uses singleton embedding service)
_vector_store_singleton = VectorStoreService(embedding_service=_embedding_service_singleton)

# Hybrid retriever uses singleton vector store and a fresh BM25 retriever
_hybrid_retriever_singleton = HybridRetriever(vector_store=_vector_store_singleton, bm25=BM25Retriever())

# Retrieval service using singletons
_retrieval_service_singleton = RetrievalService(retriever=_hybrid_retriever_singleton, reranker=_reranker_singleton)


def get_vector_store() -> VectorStoreService:
    """Return the singleton VectorStoreService."""
    return _vector_store_singleton


def init_vector_store() -> bool:
    """Attempt to load the FAISS index into the singleton vector store.

    Returns True if an index was loaded, False otherwise.
    """
    try:
        return _vector_store_singleton.load()
    except Exception:
        return False


def shutdown_vector_store_save() -> None:
    """Attempt to save the FAISS index on shutdown. Exceptions are swallowed
    to avoid crashing the shutdown process.
    """
    try:
        _vector_store_singleton.save()
    except Exception:
        pass


def get_genai_client() -> genai.Client:
    """Return the singleton genai client."""
    return _genai_client_singleton


def get_llm_service() -> LLMService:
    """Return an LLMService that uses the shared genai client."""
    return LLMService(client=get_genai_client())


def get_storage_service() -> FileStorageService:
    """Return the singleton file storage service."""
    return _storage_singleton


def get_document_service() -> DocumentService:
    """Request-scoped DocumentService.

    DocumentService is constructed with the shared VectorStoreService singleton
    so the same FAISS index and embeddings are reused.
    """
    return DocumentService(vector_store=get_vector_store())


def get_reranker() -> Reranker:
    """Return the shared Reranker singleton."""
    return _reranker_singleton


def get_retrieval_service() -> RetrievalService:
    """Return the shared RetrievalService that uses the singleton retriever and reranker."""
    return _retrieval_service_singleton


def get_rag_service() -> RAGService:
    """Request-scoped RAGService.

    Provide shared retrieval and LLM services to the request-scoped RAGService.
    """
    llm = get_llm_service()
    # Create a QueryRewriter that uses the same LLMService instance
    from app.services.rag.query_rewriter import QueryRewriter
    from app.services.rag.conversation_memory import ConversationMemory
    from app.services.retrieval.context_builder import ContextBuilder

    qr = QueryRewriter(llm_service=llm)

    # Create a request-scoped ConversationMemory and ContextBuilder
    memory = ConversationMemory()
    context_builder = ContextBuilder()

    return RAGService(
        retrieval_service=get_retrieval_service(),
        context_builder=context_builder,
        llm_service=llm,
        memory=memory,
        query_rewriter=qr,
    )
