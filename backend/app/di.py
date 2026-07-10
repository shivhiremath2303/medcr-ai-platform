from fastapi import Depends
from app.domain.repositories.document_parser import DocumentParser
from app.domain.repositories.vector_store_repository import VectorStoreRepository
from app.domain.repositories.embedding_repository import EmbeddingRepository
from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.storage_provider import StorageProvider
from app.domain.repositories.keyword_retriever import KeywordRetriever
from app.domain.repositories.reranker import Reranker
from app.domain.repositories.chunker import Chunker
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.document_repository import DocumentRepository
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.query_rewriter import QueryRewriter as IQueryRewriter
from app.domain.repositories.context_builder import ContextBuilder as IContextBuilder

from app.infrastructure.llm.gemini_adapter import GeminiLLMAdapter
from app.infrastructure.embeddings.huggingface_adapter import HuggingFaceEmbeddingAdapter
from app.infrastructure.vectorstore.faiss_repository import FAISSVectorRepository
from app.infrastructure.storage.local_storage_adapter import LocalStorageAdapter
from app.infrastructure.storage.filesystem_document_repository import FilesystemDocumentRepository
from app.infrastructure.storage.memory_conversation_repository import MemoryConversationRepository
from app.infrastructure.parser.document_parser_adapter import DocumentParserAdapter
from app.infrastructure.parser.langchain_chunker_adapter import LangChainChunkerAdapter
from app.infrastructure.retrieval.bm25_adapter import BM25Adapter
from app.infrastructure.retrieval.cross_encoder_adapter import CrossEncoderAdapter
from app.infrastructure.retrieval.hybrid_retriever_adapter import HybridRetrieverAdapter

from app.services.document.document_service import DocumentService
from app.services.retrieval.retrieval_service import RetrievalService
from app.services.retrieval.context_builder import ContextBuilder
from app.services.rag.rag_service import RAGService
from app.services.rag.query_rewriter import QueryRewriter

# Singletons
_embedding_provider = HuggingFaceEmbeddingAdapter()
_vector_repository = FAISSVectorRepository(embedding_provider=_embedding_provider)
_llm_provider = GeminiLLMAdapter()
_storage_provider = LocalStorageAdapter()
_document_repository = FilesystemDocumentRepository()
_conversation_repository = MemoryConversationRepository()
_parser = DocumentParserAdapter()
_chunker = LangChainChunkerAdapter()
_keyword_retriever = BM25Adapter()
_reranker = CrossEncoderAdapter()

# Adapters that require other adapters (also Singletons for efficiency)
_hybrid_retriever = HybridRetrieverAdapter(
    vector_store=_vector_repository,
    keyword_retriever=_keyword_retriever
)

# Providers
def get_llm_provider() -> LLMProvider:
    return _llm_provider

def get_vector_repository() -> VectorStoreRepository:
    return _vector_repository

def get_storage_provider() -> StorageProvider:
    return _storage_provider

def get_document_repository() -> DocumentRepository:
    return _document_repository

def get_conversation_repository() -> ConversationRepository:
    return _conversation_repository

def get_document_parser() -> DocumentParser:
    return _parser

def get_chunker() -> Chunker:
    return _chunker

def get_keyword_retriever() -> KeywordRetriever:
    return _keyword_retriever

def get_reranker() -> Reranker:
    return _reranker

def get_retriever() -> Retriever:
    return _hybrid_retriever

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
    document_repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentService:
    return DocumentService(
        chunker=chunker,
        vector_store=vector_store,
        parser=parser,
        document_repository=document_repository
    )

def get_retrieval_service(
    retriever: Retriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
) -> Retriever:
    return RetrievalService(retriever=retriever, reranker=reranker)

def get_context_builder() -> IContextBuilder:
    return ContextBuilder()

def get_query_rewriter(
    llm_provider: LLMProvider = Depends(get_llm_provider)
) -> IQueryRewriter:
    return QueryRewriter(llm_provider=llm_provider)

def get_rag_service(
    retrieval_service: Retriever = Depends(get_retrieval_service),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
    query_rewriter: IQueryRewriter = Depends(get_query_rewriter),
    context_builder: IContextBuilder = Depends(get_context_builder),
) -> RAGService:
    return RAGService(
        retrieval_service=retrieval_service,
        llm_provider=llm_provider,
        query_rewriter=query_rewriter,
        memory=conversation_repository,
        context_builder=context_builder
    )

# Lifecycle management
def init_vector_store() -> bool:
    return _vector_repository.load()

def shutdown_vector_store_save() -> None:
    _vector_repository.save()
