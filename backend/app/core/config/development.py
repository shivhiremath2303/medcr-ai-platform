from app.core.config.base import Settings


class DevelopmentSettings(Settings):
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"

    # Development CORS - permissive for local development
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    cors_allowed_methods: list[str] = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
        "PATCH",
    ]
    cors_allowed_headers: list[str] = [
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "X-Correlation-ID",
        "Accept",
        "Origin",
    ]

    # Relaxed rate limits for development
    rate_limit_auth_requests: int = 60
    rate_limit_upload_requests: int = 20
    rate_limit_rag_requests: int = 120
    rate_limit_general_requests: int = 300
