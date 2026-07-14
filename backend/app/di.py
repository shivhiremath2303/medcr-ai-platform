from __future__ import annotations

from typing import Optional

from fastapi import BackgroundTasks, Depends
from google import genai

from app.core.config import get_settings
from app.core.observability.concurrency import ConcurrencyLimiter
from app.core.observability.health import HealthService
from app.core.observability.metrics import MetricsRegistry, NoOpMetricsProvider
from app.core.observability.resource_guard import ResourceGuard
from app.core.security.auth_service import AuthService
from app.core.security.authorization import AuthorizationService
from app.core.security.jwt import JWTManager
from app.core.security.password import PasswordHasher
from app.core.security.rate_limiter import RateLimiterService
from app.domain.models.user import User, UserRole
from app.domain.repositories import (
    CacheProvider,
    Chunker,
    ConversationRepository,
    DocumentParser,
    DocumentRepository,
    EmbeddingRepository,
    KeywordRetriever,
    LLMProvider,
    MetricsProvider,
    RateLimiter,
    Reranker,
    Retriever,
    RevocationRepository,
    StorageProvider,
    UserRepository,
    VectorStoreRepository,
)
from app.domain.repositories.background_tasks import BackgroundTaskProvider
from app.domain.repositories.benchmark_repository import BenchmarkRepository
from app.domain.repositories.context_builder import ContextBuilder as IContextBuilder
from app.domain.repositories.query_rewriter import QueryRewriter as IQueryRewriter
from app.domain.repositories.security.secret_provider import SecretProvider
from app.infrastructure.background.fastapi_background_tasks import (
    FastAPIBackgroundTaskProvider,
)
from app.infrastructure.background.redis_job_queue import RedisJobQueueProvider
from app.infrastructure.embeddings.huggingface_adapter import (
    HuggingFaceEmbeddingAdapter,
)
from app.infrastructure.llm.gemini_adapter import GeminiLLMAdapter
from app.infrastructure.observability.ai_provider_health import AIProviderHealthCheck
from app.infrastructure.observability.prometheus_metrics import (
    PrometheusMetricsProvider,
)
from app.infrastructure.observability.redis_health import RedisHealthCheck
from app.infrastructure.observability.storage_health import StorageHealthCheck
from app.infrastructure.observability.vector_store_health import VectorStoreHealthCheck
from app.infrastructure.parser.document_parser_adapter import DocumentParserAdapter
from app.infrastructure.parser.langchain_chunker_adapter import LangChainChunkerAdapter
from app.infrastructure.retrieval.bm25_adapter import BM25Adapter
from app.infrastructure.retrieval.cross_encoder_adapter import CrossEncoderAdapter
from app.infrastructure.retrieval.hybrid_retriever_adapter import HybridRetrieverAdapter
from app.infrastructure.security.secret_providers import MultiSourceSecretProvider
from app.infrastructure.storage.filesystem_document_repository import (
    FilesystemDocumentRepository,
)
from app.infrastructure.storage.local_storage_adapter import LocalStorageAdapter
from app.infrastructure.storage.memory_benchmark_repository import (
    MemoryBenchmarkRepository,
)
from app.infrastructure.storage.memory_cache_provider import MemoryCacheProvider
from app.infrastructure.storage.memory_conversation_repository import (
    MemoryConversationRepository,
)
from app.infrastructure.storage.memory_user_repository import MemoryUserRepository
from app.infrastructure.storage.multi_level_cache_provider import (
    MultiLevelCacheProvider,
)
from app.infrastructure.storage.noop_rate_limiter import NoOpRateLimiter
from app.infrastructure.storage.redis_cache_provider import RedisCacheProvider
from app.infrastructure.storage.redis_client import RedisClient
from app.infrastructure.storage.redis_conversation_repository import (
    RedisConversationRepository,
)
from app.infrastructure.storage.redis_rate_limiter import RedisRateLimiter
from app.infrastructure.storage.redis_revocation_repository import (
    RedisRevocationRepository,
)
from app.infrastructure.storage.redis_user_repository import RedisUserRepository
from app.infrastructure.vectorstore.faiss_repository import FAISSVectorRepository
from app.services.audit.audit_service import AuditService
from app.services.background.worker_service import WorkerService
from app.services.cache.cache_warming_service import CacheWarmingService
from app.services.document.document_service import DocumentService
from app.services.maintenance.cleanup_service import CleanupService
from app.services.rag.evaluation_engine import EvaluationEngine
from app.services.rag.grounding_engine import GroundingEngine
from app.services.rag.query_rewriter import QueryRewriter
from app.services.rag.rag_service import RAGService
from app.services.rag.reasoning_engine import ReasoningEngine
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.retrieval_service import RetrievalService

# Load settings - validation happens inside get_settings()
settings = get_settings()

# --- Security: Secret Abstraction (10.1.4) ---
_secret_provider: SecretProvider = MultiSourceSecretProvider()

# --- Observability ---
_metrics_provider: MetricsProvider
if settings.metrics_enabled:
    _metrics_provider = PrometheusMetricsProvider()
else:
    _metrics_provider = NoOpMetricsProvider()

_metrics_registry = MetricsRegistry(provider=_metrics_provider)

_health_service = HealthService(
    version=settings.app_version, environment=settings.environment
)

# Resource Management & Concurrency (10.3.9)
_resource_guard = ResourceGuard(
    metrics=_metrics_registry,
    memory_limit_mb=2048.0,  # In production this would come from pod limits
)

_concurrency_limiter = ConcurrencyLimiter(
    resource_guard=_resource_guard,
    max_concurrent_tasks=20,
    max_workers=settings.worker_count * 2,
)

# --- Persistence: Redis ---
_redis_client = None
if settings.redis_url:
    _redis_client = RedisClient(
        redis_url=settings.redis_url, timeout=settings.redis_timeout
    )
    _redis_client.connect()

# --- Repositories & Adapters (Singletons) ---

_jwt_manager = JWTManager(settings=settings)

_user_repository: UserRepository
_revocation_repository: RevocationRepository
_conversation_repository: ConversationRepository
_rate_limiter: RateLimiter
_cache_provider: CacheProvider

# Distributed Session & User Architecture (10.3.5)
if _redis_client and _redis_client.is_available():
    _user_repository = RedisUserRepository(redis_client=_redis_client)
    _revocation_repository = RedisRevocationRepository(redis_client=_redis_client)
    _conversation_repository = RedisConversationRepository(
        redis_client=_redis_client,
        ttl=settings.conversation_ttl,
        max_messages=settings.max_conversation_messages,
    )
    _rate_limiter = RedisRateLimiter(redis_client=_redis_client)

    # 10.3.1: Multi-Level Caching (L1: Memory, L2: Redis)
    _l2_cache = RedisCacheProvider(
        redis_client=_redis_client,
        metrics=_metrics_registry,
        default_ttl=settings.cache_ttl,
    )
    _cache_provider = MultiLevelCacheProvider(
        l2_provider=_l2_cache, metrics=_metrics_registry, l1_max_size=2000
    )
else:
    from app.infrastructure.storage.memory_revocation_repository import (
        MemoryRevocationRepository,
    )

    _revocation_repository = MemoryRevocationRepository()
    _user_repository = MemoryUserRepository()
    _conversation_repository = MemoryConversationRepository(
        max_messages=settings.max_conversation_messages
    )
    _rate_limiter = NoOpRateLimiter()
    _cache_provider = MemoryCacheProvider()

_cache_warming_service = CacheWarmingService(cache_provider=_cache_provider)

_audit_service = AuditService()

_auth_service = AuthService(
    user_repository=_user_repository,
    jwt_manager=_jwt_manager,
    revocation_repository=_revocation_repository,
    audit_service=_audit_service,
    metrics=_metrics_registry,
)

_authorization_service = AuthorizationService(audit_service=_audit_service)

# AI Infrastructure
_genai_client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())

_embedding_provider = HuggingFaceEmbeddingAdapter(
    model_name=settings.embedding_model,
    limiter=_concurrency_limiter,
    device=settings.embedding_device,
)

_vector_repository = FAISSVectorRepository(
    embedding_provider=_embedding_provider,
    faiss_dir=settings.faiss_dir,
    index_name=settings.faiss_index_name,
    default_top_k=settings.default_top_k,
    limiter=_concurrency_limiter,
)

_llm_provider = GeminiLLMAdapter(
    client=_genai_client,
    model_name=settings.gemini_model,
    metrics=_metrics_registry,
    limiter=_concurrency_limiter,
    temperature=settings.llm_temperature,
    max_tokens=settings.llm_max_tokens,
)

_storage_provider = LocalStorageAdapter(upload_dir=settings.upload_dir)
_document_repository = FilesystemDocumentRepository(storage_dir=settings.metadata_dir)
_parser = DocumentParserAdapter(supported_extensions=settings.supported_extensions)
_chunker = LangChainChunkerAdapter(
    chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
)
_keyword_retriever = BM25Adapter()
_reranker = CrossEncoderAdapter(
    model_name=settings.reranker_model,
    metrics=_metrics_registry,
    limiter=_concurrency_limiter,
)

_grounding_engine = GroundingEngine()
_reasoning_engine = ReasoningEngine()
_evaluation_engine = EvaluationEngine()
_benchmark_repo = MemoryBenchmarkRepository()

_hybrid_retriever = HybridRetrieverAdapter(
    vector_store=_vector_repository,
    keyword_retriever=_keyword_retriever,
    vector_weight=settings.hybrid_weight_vector,
    similarity_threshold=settings.similarity_threshold,
)

# --- Service Singletons (to support background workers and routes) ---

_document_service = DocumentService(
    chunker=_chunker,
    vector_store=_vector_repository,
    parser=_parser,
    document_repository=_document_repository,
    metrics=_metrics_registry,
)

_retrieval_service = RetrievalService(
    retriever=_hybrid_retriever,
    reranker=_reranker,
    metrics=_metrics_registry,
    candidate_multiplier=settings.retrieval_candidate_multiplier,
    min_candidates=settings.min_retrieval_candidates,
)

_context_builder = ContextBuilder()

_query_rewriter = QueryRewriter(llm_provider=_llm_provider)

_rag_service = RAGService(
    retrieval_service=_retrieval_service,
    llm_provider=_llm_provider,
    query_rewriter=_query_rewriter,
    memory=_conversation_repository,
    context_builder=_context_builder,
    grounding_engine=_grounding_engine,
    reasoning_engine=_reasoning_engine,
    evaluation_engine=_evaluation_engine,
    benchmark_repo=_benchmark_repo,
    metrics=_metrics_registry,
    cache=_cache_provider,
    limiter=_concurrency_limiter,
)


# --- Health Check Registrations ---
_health_service.add_readiness_check(VectorStoreHealthCheck(_vector_repository))
_health_service.add_readiness_check(StorageHealthCheck(settings.upload_dir))

_health_service.add_readiness_check(
    AIProviderHealthCheck(_genai_client, settings.gemini_model)
)

if _redis_client:
    _health_service.add_readiness_check(RedisHealthCheck(_redis_client))


# --- Dependency Injection Providers ---


def get_settings_provider():
    return settings


def get_secret_provider() -> SecretProvider:
    return _secret_provider


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


def get_db_session_provider():
    from app.infrastructure.storage.database_foundation import get_db_session

    return get_db_session


def get_conversation_repository() -> ConversationRepository:
    return _conversation_repository


def get_user_repository() -> UserRepository:
    return _user_repository


def get_revocation_repository() -> RevocationRepository:
    return _revocation_repository


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter


def get_cache_provider() -> CacheProvider:
    return _cache_provider


def get_cache_warming_service() -> CacheWarmingService:
    return _cache_warming_service


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


def get_authorization_service() -> AuthorizationService:
    return _authorization_service


def get_audit_service() -> AuditService:
    return _audit_service


def get_rate_limiter_service(
    limiter: RateLimiter = Depends(get_rate_limiter),
    settings=Depends(get_settings_provider),
    audit_service: AuditService = Depends(get_audit_service),
) -> RateLimiterService:
    return RateLimiterService(limiter, settings, audit_service)


def get_cleanup_service() -> CleanupService:
    return CleanupService(settings, _revocation_repository)


# Distributed Background Processing (10.3.2)
_background_task_provider: BackgroundTaskProvider | None
if _redis_client:
    _background_task_provider = RedisJobQueueProvider(
        redis_client=_redis_client, metrics=_metrics_registry
    )
else:
    _background_task_provider = None


def get_background_task_provider(
    background_tasks: BackgroundTasks,
) -> BackgroundTaskProvider:
    """
    Enterprise Background Task Provider with fallback (10.3.2/10.3.7).
    """
    if _background_task_provider:
        return _background_task_provider
    return FastAPIBackgroundTaskProvider(background_tasks)


_worker_service: WorkerService | None = (
    WorkerService(
        task_provider=_background_task_provider,
        metrics=_metrics_registry,
        resource_guard=_resource_guard,
    )
    if _background_task_provider
    else None
)


def get_worker_service() -> WorkerService:
    if not _worker_service:
        raise RuntimeError("Worker service not initialized")
    return _worker_service


# --- Application Services ---


def get_document_service(
    doc_service: DocumentService = _document_service,
) -> DocumentService:
    return doc_service


def get_retrieval_service(
    retrieval_service: Retriever = _retrieval_service,
) -> Retriever:
    return retrieval_service


def get_context_builder() -> IContextBuilder:
    return _context_builder


def get_query_rewriter(
    query_rewriter: IQueryRewriter = _query_rewriter,
) -> IQueryRewriter:
    return query_rewriter


def get_rag_service(
    rag_service: RAGService = _rag_service,
) -> RAGService:
    return rag_service


# --- Lifecycle Management ---


def init_dev_user():
    if not _user_repository.get_by_username("admin"):
        _user_repository.save(
            User(
                user_id="admin-001",
                username="admin",
                email="admin@medcr.ai",
                hashed_password=PasswordHasher.hash("admin-password"),
                role=UserRole.ADMIN,
                full_name="System Administrator",
            )
        )


async def init_vector_store() -> bool:
    init_dev_user()
    return await _vector_repository.load()


async def shutdown_vector_store_save() -> None:
    await _vector_repository.save()
