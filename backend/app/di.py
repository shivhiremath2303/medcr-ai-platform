from fastapi import Depends
from app.domain.repositories.document_parser import DocumentParser
from app.domain.repositories.vector_store_repository import VectorStoreRepository
from app.domain.repositories.embedding_repository import EmbeddingRepository
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.storage_provider import StorageProvider
from app.domain.repositories.keyword_retriever import KeywordRetriever
from app.domain.repositories.reranker import Reranker
from app.domain.repositories.chunker import Chunker

from app.infrastructure.llm.gemini_adapter import GeminiLLMAdapter
from app.infrastructure.embeddings.huggingface_adapter import HuggingFaceEmbeddingAdapter
from app.infrastructure.vectorstore.faiss_repository import FAISSVectorRepository
from app.infrastructure.storage.local_storage_adapter import LocalStorageAdapter
from app.infrastructure.parser.document_parser_adapter import DocumentParserAdapter
from app.infrastructure.parser.langchain_chunker_adapter import LangChainChunkerAdapter
from app.infrastructure.retrieval.bm25_adapter import BM25Adapter
from app.infrastructure.retrieval.cross_encoder_adapter import CrossEncoderAdapter

from app.services.document.document_service import DocumentService
from app.services.retrieval.retrieval_service import RetrievalService
from app.services.retrieval.hybrid_retriever import HybridRetriever
from app.services.retrieval.context_builder import ContextBuilder
from app.services.rag.rag_service import RAGService
from app.services.rag.conversation_memory import ConversationMemory
from app.services.rag.query_rewriter import QueryRewriter

# Singletons
_embedding_provider = HuggingFaceEmbeddingAdapter()
_vector_repository = FAISSVectorRepository(embedding_provider=_embedding_provider)
_llm_provider = GeminiLLMAdapter()
_storage_provider = LocalStorageAdapter()
_parser = DocumentParserAdapter()
_chunker = LangChainChunkerAdapter()
_keyword_retriever = BM25Adapter()
_reranker = CrossEncoderAdapter()

# Providers
def get_llm_provider() -> LLMProvider:
    return _llm_provider

def get_vector_repository() -> VectorStoreRepository:
    return _vector_repository

def get_storage_provider() -> StorageProvider:
    return _storage_provider

def get_document_parser() -> DocumentParser:
    return _parser

def get_chunker() -> Chunker:
    return _chunker

def get_keyword_retriever() -> KeywordRetriever:
    return _keyword_retriever

def get_reranker() -> Reranker:
    return _reranker

# Legacy compatibility/Service aliases for routes if they use these names
def get_storage_service() -> StorageProvider:
    return _storage_provider

def get_llm_service() -> LLMProvider:
    return _llm_provider

# Services
def get_document_service(
    chunker: Chunker = Depends(get_chunker),
    vector_store: VectorStoreRepository = Depends(get_vector_repository),
    parser: DocumentParser = Depends(get_document_parser),
) -> DocumentService:
    return DocumentService(chunker=chunker, vector_store=vector_store, parser=parser)

def get_retrieval_service(
    vector_store: VectorStoreRepository = Depends(get_vector_repository),
    keyword_retriever: KeywordRetriever = Depends(get_keyword_retriever),
    reranker: Reranker = Depends(get_reranker),
) -> RetrievalService:
    hybrid_retriever = HybridRetriever(
        vector_store=vector_store,
        keyword_retriever=keyword_retriever
    )
    return RetrievalService(retriever=hybrid_retriever, reranker=reranker)

def get_context_builder() -> ContextBuilder:
    return ContextBuilder()

def get_conversation_memory() -> ConversationMemory:
    return ConversationMemory()

def get_query_rewriter(
    llm_provider: LLMProvider = Depends(get_llm_provider)
) -> QueryRewriter:
    return QueryRewriter(llm_provider=llm_provider)

def get_rag_service(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> RAGService:
    return RAGService(
        retrieval_service=retrieval_service,
        llm_provider=llm_provider,
        query_rewriter=QueryRewriter(llm_provider=llm_provider),
        memory=ConversationMemory(),
        context_builder=ContextBuilder()
    )

# Lifecycle management
def init_vector_store() -> bool:
    return _vector_repository.load()

def shutdown_vector_store_save() -> None:
    _vector_repository.save()
