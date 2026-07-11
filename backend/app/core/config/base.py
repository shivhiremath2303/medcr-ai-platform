from pathlib import Path
from typing import Set, List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[4]

class Settings(BaseSettings):
    # --- Application Settings ---
    app_name: str = Field("medcr-ai-platform", description="Project name")
    app_version: str = Field("1.0.0", description="Application version")
    app_description: str = Field("Production-grade Legal AI RAG Platform", description="Application description")
    environment: str = Field("development", description="Current environment (development, testing, production)")
    debug: bool = Field(False, description="Debug mode flag")

    # --- Networking & API ---
    host: str = Field("0.0.0.0", description="API host")
    port: int = Field(8000, description="API port")
    worker_count: int = Field(1, description="Number of worker processes")
    http_timeout: float = Field(30.0, description="General HTTP timeout")
    connection_timeout: float = Field(10.0, description="Connection timeout")
    read_timeout: float = Field(30.0, description="Read timeout")
    write_timeout: float = Field(30.0, description="Write timeout")

    # --- Security ---
    gemini_api_key: str = Field("", description="Google Gemini API Key")

    # --- Rate Limiting ---
    rate_limit_enabled: bool = Field(True, description="Enable rate limiting")
    rate_limit_auth_requests: int = Field(10, description="Max auth requests per minute")
    rate_limit_upload_requests: int = Field(5, description="Max upload requests per minute")
    rate_limit_rag_requests: int = Field(30, description="Max RAG requests per minute")
    rate_limit_general_requests: int = Field(100, description="Max general requests per minute")
    rate_limit_window_seconds: int = Field(60, description="Rate limit window in seconds")

    # --- File Upload Security ---
    max_upload_size_mb: int = Field(20, description="Maximum upload size in MB")
    max_upload_files: int = Field(5, description="Maximum number of files per request")
    supported_extensions: Set[str] = Field({".pdf", ".docx"}, description="Supported file extensions")
    allowed_mime_types: Set[str] = Field(
        {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        description="Allowed MIME types for uploads"
    )
    file_encoding: str = Field("utf-8", description="Default file encoding")

    # --- Storage ---
    upload_dir: Path = Field(BASE_DIR / "backend" / "uploads" / "documents", description="Directory for uploaded documents")
    faiss_dir: Path = Field(BASE_DIR / "backend" / "data" / "faiss", description="Directory for FAISS index")
    metadata_dir: Path = Field(BASE_DIR / "backend" / "data" / "metadata", description="Directory for document metadata")
    temp_dir: Path = Field(BASE_DIR / "backend" / "data" / "temp", description="Directory for temporary files")
    cache_dir: Path = Field(BASE_DIR / "backend" / "data" / "cache", description="Directory for cached data")

    # --- AI - Embeddings ---
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", description="Model for document embeddings")
    embedding_device: str = Field("cpu", description="Device for embedding model (cpu, cuda)")
    embedding_batch_size: int = Field(32, description="Batch size for embedding")

    # --- AI - LLM ---
    gemini_model: str = Field("gemini-2.0-flash", description="Gemini model name")
    llm_temperature: float = Field(0.1, description="LLM temperature")
    llm_max_tokens: int = Field(2048, description="Maximum tokens for LLM response")
    llm_retry_count: int = Field(3, description="Number of retries for LLM calls")
    llm_streaming: bool = Field(False, description="Enable streaming for LLM responses")

    # --- AI - Reranker ---
    reranker_model: str = Field("cross-encoder/ms-marco-MiniLM-L-6-v2", description="Model for reranking")
    reranker_top_k: int = Field(5, description="Number of results to keep after reranking")

    # --- AI - Chunking ---
    chunk_size: int = Field(1000, description="Size of document chunks")
    chunk_overlap: int = Field(200, description="Overlap between chunks")

    # --- AI - Retrieval ---
    default_top_k: int = Field(3, description="Default number of results for similarity search")
    retrieval_candidate_multiplier: int = Field(4, description="Multiplier for initial retrieval candidates")
    min_retrieval_candidates: int = Field(20, description="Minimum number of retrieval candidates")
    faiss_index_name: str = Field("legal_documents", description="Name of the FAISS index file")
    hybrid_weight_vector: float = Field(0.7, description="Weight for vector search in hybrid retrieval")
    similarity_threshold: float = Field(0.0, description="Minimum similarity score for results")

    # --- Persistence & Cache ---
    redis_url: Optional[str] = Field(None, description="Redis connection URL (e.g., redis://localhost:6379/0)")
    redis_timeout: int = Field(5, description="Redis connection timeout")

    conversation_ttl: int = Field(3600 * 24, description="Conversation history TTL in seconds (24h)")
    token_revocation_ttl: int = Field(3600 * 2, description="Token revocation record TTL in seconds")
    cache_ttl: int = Field(3600, description="General cache TTL in seconds")

    cleanup_interval_seconds: int = Field(3600, description="Interval for background cleanup tasks")

    # --- Future Infrastructure Models (Not implemented) ---
    database_url: Optional[str] = Field(None, description="Database connection URL")
    database_pool_size: int = Field(5, description="Database connection pool size")
    database_echo: bool = Field(False, description="Enable SQL echoing")
    database_max_overflow: int = Field(10, description="Database pool max overflow")

    # Object Storage
    storage_provider: str = Field("local", description="Storage provider (local, s3)")
    s3_endpoint: Optional[str] = Field(None, description="S3 endpoint URL")
    s3_bucket: Optional[str] = Field(None, description="S3 bucket name")
    s3_region: Optional[str] = Field(None, description="S3 region")
    s3_access_key: Optional[str] = Field(None, description="S3 access key")
    s3_secret_key: Optional[str] = Field(None, description="S3 secret key")

    # Authentication
    jwt_secret_key: str = Field("development-secret-key-change-me-in-production", description="Secret key for JWT")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_access_token_minutes: int = Field(30, description="JWT access token expiration in minutes")
    jwt_refresh_token_days: int = Field(7, description="JWT refresh token expiration in days")
    cors_allowed_origins: List[str] = Field(["*"], description="Allowed CORS origins")
    cors_allowed_methods: List[str] = Field(["*"], description="Allowed CORS methods")
    cors_allowed_headers: List[str] = Field(["*"], description="Allowed CORS headers")

    # Observability
    metrics_enabled: bool = Field(False, description="Enable metrics collection")
    metrics_path: str = Field("/metrics", description="Endpoint for metrics")
    otel_enabled: bool = Field(False, description="Enable OpenTelemetry")
    otel_service_name: str = Field("medcr-ai-platform", description="Service name for OTEL")
    otel_exporter_endpoint: Optional[str] = Field(None, description="OTEL exporter endpoint")

    # Logging
    log_level: str = Field("INFO", description="Global log level")
    log_format: str = Field("text", description="Log format (text, json)")
    log_json: bool = Field(False, description="Enable JSON logging")
    log_directory: Path = Field(BASE_DIR / "backend" / "logs", description="Directory for log files")
    log_rotation_size: str = Field("10MB", description="Log file rotation size")
    log_retention_days: int = Field(7, description="Log file retention days")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("upload_dir", "faiss_dir", "metadata_dir", "temp_dir", "cache_dir", "log_directory", mode="before")
    @classmethod
    def ensure_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
