from __future__ import annotations

from google import genai
from fastapi import Depends, BackgroundTasks
from app.core.config import get_settings
from app.domain.repositories import (
    DocumentParser, VectorStoreRepository, EmbeddingRepository,
    LLMProvider, StorageProvider, KeywordRetriever, Reranker,
    Chunker, Retriever, DocumentRepository, ConversationRepository,
    UserRepository, RevocationRepository, RateLimiter, CacheProvider,
    MetricsProvider
)
from app.domain.repositories.query_rewriter import QueryRewriter as IQueryRewriter
from app.domain.repositories.context_builder import ContextBuilder as IContextBuilder
from app.domain.repositories.background_tasks import BackgroundTaskProvider

from app.infrastructure.llm.gemini_adapter import GeminiLLMAdapter
from app.infrastructure.embeddings.huggingface_adapter import HuggingFaceEmbeddingAdapter
from app.infrastructure.vectorstore.faiss_repository import FAISSVectorRepository
from app.infrastructure.storage.local_storage_adapter import LocalStorageAdapter
from app.infrastructure.storage.filesystem_document_repository import FilesystemDocumentRepository
from app.infrastructure.storage.memory_conversation_repository import MemoryConversationRepository
from app.infrastructure.storage.redis_conversation_repository import RedisConversationRepository
from app.infrastructure.storage.memory_user_repository import MemoryUserRepository
from app.infrastructure.storage.redis_revocation_repository import RedisRevocationRepository
from app.infrastructure.storage.redis_rate_limiter import RedisRateLimiter
from app.infrastructure.storage.noop_rate_limiter import NoOpRateLimiter
from app.infrastructure.storage.redis_cache_provider import RedisCacheProvider
from app.infrastructure.storage.memory_cache_provider import MemoryCacheProvider
from app.infrastructure.storage.redis_client import RedisClient

from app.infrastructure.parser.document_parser_adapter import DocumentParserAdapter
from app.infrastructure.parser.langchain_chunker_adapter import LangChainChunkerAdapter
from app.infrastructure.retrieval.bm25_adapter import BM25Adapter
from app.infrastructure.retrieval.cross_encoder_adapter import CrossEncoderAdapter
from app.infrastructure.retrieval.hybrid_retriever_adapter import HybridRetrieverAdapter
from app.infrastructure.background.fastapi_background_tasks import FastAPIBackgroundTaskProvider

from app.services.document.document_service import DocumentService
from app.services.retrieval.retrieval_service import RetrievalService
from app.services.retrieval.context_builder import ContextBuilder
from app.services.rag.rag_service import RAGService
from app.services.rag.query_rewriter import QueryRewriter
from app.services.rag.grounding_engine import GroundingEngine
from app.services.rag.reasoning_engine import ReasoningEngine
from app.services.rag.evaluation_engine import EvaluationEngine

from app.domain.repositories.benchmark_repository import BenchmarkRepository
from app.infrastructure.storage.memory_benchmark_repository import MemoryBenchmarkRepository

from app.core.observability.health import HealthService
from app.core.observability.metrics import NoOpMetricsProvider, MetricsRegistry
from app.infrastructure.observability.prometheus_metrics import PrometheusMetricsProvider
from app.infrastructure.observability.vector_store_health import VectorStoreHealthCheck
from app.infrastructure.observability.storage_health import StorageHealthCheck

from app.core.security.jwt import JWTManager
from app.core.security.auth_service import AuthService
from app.domain.models.user import User, UserRole
from app.core.security.password import PasswordHasher

# Load settings - validation happens inside get_settings()
settings = get_settings()

# --- Observability ---
_metrics_provider: MetricsProvider
if settings.metrics_enabled:
    _metrics_provider = PrometheusMetricsProvider()
else:
    _metrics_provider = NoOpMetricsProvider()

_metrics_registry = MetricsRegistry(provider=_metrics_provider)

_health_service = HealthService(
    version=settings.app_version,
    environment=settings.environment
)

# --- Persistence: Redis ---
_redis_client = None
if settings.redis_url:
    _redis_client = RedisClient(redis_url=settings.redis_url, timeout=settings.redis_timeout)
    _redis_client.connect()

# --- Repositories & Adapters (Singletons) ---

_jwt_manager = JWTManager(settings=settings)
_user_repository = MemoryUserRepository() # TODO: Move to DB in next milestone

# Revocation
if _redis_client and _redis_client.is_available():
    _revocation_repository = RedisRevocationRepository(redis_client=_redis_client)
    _conversation_repository = RedisConversationRepository(
        redis_client=_redis_client,
        ttl=settings.conversation_ttl,
        max_messages=settings.max_conversation_messages
    )
    _rate_limiter = RedisRateLimiter(redis_client=_redis_client)
    _cache_provider = RedisCacheProvider(
        redis_client=_redis_client,
        metrics=_metrics_registry,
        default_ttl=settings.cache_ttl
    )
else:
    # Fallback to in-memory if Redis is not configured or unavailable
    from app.infrastructure.storage.memory_revocation_repository import MemoryRevocationRepository
    _revocation_repository = MemoryRevocationRepository()
    _conversation_repository = MemoryConversationRepository(
        max_messages=settings.max_conversation_messages
    )
    _rate_limiter = NoOpRateLimiter()
    _cache_provider = MemoryCacheProvider()

_auth_service = AuthService(
    user_repository=_user_repository,
    jwt_manager=_jwt_manager,
    revocation_repository=_revocation_repository
)

# Initialize with a default admin user for development
def init_dev_user():
    if not _user_repository.get_by_username("admin"):
        _user_repository.save(User(
            user_id="admin-001",
            username="admin",
            email="admin@medcr.ai",
            hashed_password=PasswordHasher.hash("admin-password"),
            role=UserRole.ADMIN,
            full_name="System Administrator"
        ))

# AI Infrastructure
_genai_client = genai.Client(api_key=settings.gemini_api_key)

_embedding_provider = HuggingFaceEmbeddingAdapter(
    model_name=settings.embedding_model,
    device=settings.embedding_device
)

_vector_repository = FAISSVectorRepository(
    embedding_provider=_embedding_provider,
    faiss_dir=settings.faiss_dir,
    index_name=settings.faiss_index_name,
    default_top_k=settings.default_top_k
)

_llm_provider = GeminiLLMAdapter(
    client=_genai_client,
    model_name=settings.gemini_model,
    metrics=_metrics_registry,
    temperature=settings.llm_temperature,
    max_tokens=settings.llm_max_tokens
)

_storage_provider = LocalStorageAdapter(
    upload_dir=settings.upload_dir
)

_document_repository = FilesystemDocumentRepository(
    storage_dir=settings.metadata_dir
)

_parser = DocumentParserAdapter(
    supported_extensions=settings.supported_extensions
)

_chunker = LangChainChunkerAdapter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)

_keyword_retriever = BM25Adapter()

_reranker = CrossEncoderAdapter(
    model_name=settings.reranker_model
)

_grounding_engine = GroundingEngine()
_reasoning_engine = ReasoningEngine()
_evaluation_engine = EvaluationEngine()
_benchmark_repo = MemoryBenchmarkRepository()

_hybrid_retriever = HybridRetrieverAdapter(
    vector_store=_vector_repository,
    keyword_retriever=_keyword_retriever,
    vector_weight=settings.hybrid_weight_vector,
    similarity_threshold=settings.similarity_threshold
)

# --- Health Check Registrations ---
_health_service.add_readiness_check(VectorStoreHealthCheck(_vector_repository))
_health_service.add_readiness_check(StorageHealthCheck(settings.upload_dir))
if _redis_client:
    from app.infrastructure.observability.redis_health import RedisHealthCheck
    _health_service.add_readiness_check(RedisHealthCheck(_redis_client))

# --- Dependency Injection Providers ---

def get_settings_provider():
    return settings

def get_genai_client() -> genai.Client:
    return _genai_client

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

def get_user_repository() -> UserRepository:
    return _user_repository

def get_revocation_repository() -> RevocationRepository:
    return _revocation_repository

def get_rate_limiter() -> RateLimiter:
    return _rate_limiter

def get_rate_limiter_service(
    limiter: RateLimiter = Depends(get_rate_limiter),
    settings = Depends(get_settings_provider),
) -> RateLimiterService:
    from app.core.security.rate_limiter import RateLimiterService
    return RateLimiterService(limiter, settings)

def get_cache_provider() -> CacheProvider:
    return _cache_provider

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

def get_grounding_engine() -> GroundingEngine:
    return _grounding_engine

def get_reasoning_engine() -> ReasoningEngine:
    return _reasoning_engine

def get_evaluation_engine() -> EvaluationEngine:
    return _evaluation_engine

def get_benchmark_repository() -> BenchmarkRepository:
    return _benchmark_repo

def get_health_service() -> HealthService:
    return _health_service

def get_metrics_registry() -> MetricsRegistry:
    return _metrics_registry

def get_metrics_provider() -> MetricsProvider:
    return _metrics_provider

def get_jwt_manager() -> JWTManager:
    return _jwt_manager

def get_auth_service() -> AuthService:
    return _auth_service

def get_cleanup_service() -> CleanupService:
    from app.services.maintenance.cleanup_service import CleanupService
    return CleanupService(settings, _revocation_repository)

def get_background_task_provider(background_tasks: BackgroundTasks) -> BackgroundTaskProvider:
    return FastAPIBackgroundTaskProvider(background_tasks)

# --- Application Services ---

def get_document_service(
    chunker: Chunker = Depends(get_chunker),
    vector_store: VectorStoreRepository = Depends(get_vector_repository),
    parser: DocumentParser = Depends(get_document_parser),
    document_repository: DocumentRepository = Depends(get_document_repository),
    metrics: MetricsRegistry = Depends(get_metrics_registry),
) -> DocumentService:
    return DocumentService(
        chunker=chunker,
        vector_store=vector_store,
        parser=parser,
        document_repository=document_repository,
        metrics=metrics
    )

def get_retrieval_service(
    retriever: Retriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
    metrics: MetricsRegistry = Depends(get_metrics_registry),
) -> Retriever:
    return RetrievalService(
        retriever=retriever,
        reranker=reranker,
        metrics=metrics,
        candidate_multiplier=settings.retrieval_candidate_multiplier,
        min_candidates=settings.min_retrieval_candidates
    )

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
    grounding_engine: GroundingEngine = Depends(get_grounding_engine),
    reasoning_engine: ReasoningEngine = Depends(get_reasoning_engine),
    evaluation_engine: EvaluationEngine = Depends(get_evaluation_engine),
    benchmark_repo: BenchmarkRepository = Depends(get_benchmark_repository),
    metrics: MetricsRegistry = Depends(get_metrics_registry),
) -> RAGService:
    return RAGService(
        retrieval_service=retrieval_service,
        llm_provider=llm_provider,
        query_rewriter=query_rewriter,
        memory=conversation_repository,
        context_builder=context_builder,
        grounding_engine=grounding_engine,
        reasoning_engine=reasoning_engine,
        evaluation_engine=evaluation_engine,
        benchmark_repo=benchmark_repo,
        metrics=metrics
    )

# --- Lifecycle Management ---

def init_vector_store() -> bool:
    init_dev_user()
    return _vector_repository.load()

def shutdown_vector_store_save() -> None:
    _vector_repository.save()
