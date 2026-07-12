from app.core.config.base import Settings
from pydantic import Field, AliasChoices

class ProductionSettings(Settings):
    """
    Production settings with strict validation.
    Required environment variables must be provided.
    """
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"

    # In production, we require these to be set via environment variables.
    # AliasChoices allows mapping from different environment variable names.
    gemini_api_key: str = Field(
        ...,
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key")
    )

    jwt_secret_key: str = Field(
        ...,
        validation_alias=AliasChoices("JWT_SECRET_KEY", "jwt_secret_key")
    )

    # Production CORS - strict origins required.
    # Must be a JSON string like '["https://api.example.com"]' when set via env var.
    cors_allowed_origins: list[str] = Field(
        ...,
        validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS", "cors_allowed_origins")
    )

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
