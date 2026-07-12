from app.core.config.base import BASE_DIR, Settings


class TestingSettings(Settings):
    """
    Settings for automated testing.
    """

    environment: str = "testing"
    debug: bool = True
    log_level: str = "DEBUG"

    # Isolated storage for tests - relative to BASE_DIR
    upload_dir: str = str(BASE_DIR / "tests" / "uploads")
    faiss_dir: str = str(BASE_DIR / "tests" / "data" / "faiss")
    metadata_dir: str = str(BASE_DIR / "tests" / "data" / "metadata")
    log_directory: str = str(BASE_DIR / "tests" / "logs")

    # Speed up tests
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Allow tests to run without real API key if they mock the provider
    gemini_api_key: str = "test-key"
    jwt_secret_key: str = "test-secret-key-for-testing-only"

    # Test CORS
    cors_allowed_origins: list[str] = ["http://testserver", "http://localhost"]
    cors_allowed_methods: list[str] = ["GET", "POST", "OPTIONS"]
    cors_allowed_headers: list[str] = ["*"]

    # High rate limits for tests (effectively unlimited)
    rate_limit_auth_requests: int = 1000
    rate_limit_upload_requests: int = 1000
    rate_limit_rag_requests: int = 1000
    rate_limit_general_requests: int = 1000
