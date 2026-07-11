from app.core.config.base import Settings
from pydantic import Field

class ProductionSettings(Settings):
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"

    # In production, we require these to be set via environment variables
    # Pydantic will raise an error if they are missing and no default is provided
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")

    # Production CORS - strict origins required
    cors_allowed_origins: list[str] = Field(..., env="CORS_ALLOWED_ORIGINS")
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

    # Production often needs different host/port or behind a reverse proxy
    host: str = "0.0.0.0"
    port: int = 8000
