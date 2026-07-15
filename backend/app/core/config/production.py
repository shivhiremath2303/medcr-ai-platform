from pydantic import Field, SecretStr, field_validator

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
    # We use field_validators to ensure they are not empty and meet entropy requirements.
    gemini_api_key: SecretStr = Field(..., description="Google Gemini API Key")
    jwt_secret_key: SecretStr = Field(..., description="JWT Secret Key")

    @field_validator("gemini_api_key", "jwt_secret_key")
    @classmethod
    def validate_secret_not_empty(cls, v: SecretStr):
        if not v.get_secret_value() or len(v.get_secret_value()) < 1:
            raise ValueError("Secret cannot be empty in production")
        return v

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_entropy(cls, v: SecretStr):
        if len(v.get_secret_value()) < 32:
            raise ValueError("JWT secret must be at least 32 characters for HS256")
        return v

    # Must be a valid JSON list when set via environment variable.
    # e.g., CORS_ALLOWED_ORIGINS=["https://app.medcr.ai"]
    cors_allowed_origins: list[str] = Field(
        ..., min_length=1, description="Allowed CORS origins"
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
