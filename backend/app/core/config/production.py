from pydantic import Field
from app.core.config.base import Settings

class ProductionSettings(Settings):
    """
    Production settings with strict validation.
    Environment variables are automatically mapped (e.g., GEMINI_API_KEY).
    """
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"

    # In production, we require these to be set.
    # Field(..., min_length=1) ensures they are provided and not empty.
    gemini_api_key: str = Field(..., min_length=1, description="Google Gemini API Key")
    jwt_secret_key: str = Field(..., min_length=1, description="JWT Secret Key")

    # Must be a valid JSON list when set via environment variable.
    # e.g., CORS_ALLOWED_ORIGINS=["https://app.medcr.ai"]
    cors_allowed_origins: list[str] = Field(..., min_length=1, description="Allowed CORS origins")

    cors_allowed_methods: list[str] = ["GET", "POST"]
    cors_allowed_headers: list[str] = [
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "X-Correlation-ID",
        "Accept",
    ]

    # Production rate limits
    rate_limit_auth_requests: int = 10
    rate_limit_upload_requests: int = 5
    rate_limit_rag_requests: int = 30
    rate_limit_general_requests: int = 100

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
