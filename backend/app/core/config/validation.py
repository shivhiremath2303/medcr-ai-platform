from app.core.config.base import Settings


def validate_config(settings: Settings) -> None:
    """
    Performs additional validation on the settings object.
    Fails fast with descriptive errors.
    """
    errors = []

    # Production-specific validation
    if settings.environment == "production":
        if not settings.gemini_api_key:
            errors.append("GEMINI_API_KEY must be set in production environment.")

        if (
            not settings.jwt_secret_key
            or settings.jwt_secret_key
            == "development-secret-key-change-me-in-production"  # noqa: S105
        ):
            errors.append("JWT_SECRET_KEY must be changed in production environment.")

        if not settings.cors_allowed_origins or settings.cors_allowed_origins == ["*"]:
            errors.append(
                "CORS_ALLOWED_ORIGINS must be explicitly set in production (no wildcards)."
            )

        if settings.debug:
            errors.append("DEBUG must be false in production environment.")

        if "*" in settings.cors_allowed_methods:
            errors.append(
                "CORS_ALLOWED_METHODS must not contain wildcards in production."
            )

        if "*" in settings.cors_allowed_headers:
            errors.append(
                "CORS_ALLOWED_HEADERS must not contain wildcards in production."
            )

    # Generic validation
    if settings.chunk_overlap >= settings.chunk_size:
        errors.append(
            f"chunk_overlap ({settings.chunk_overlap}) must be smaller than chunk_size ({settings.chunk_size})."
        )

    if settings.default_top_k <= 0:
        errors.append(
            f"default_top_k ({settings.default_top_k}) must be greater than zero."
        )

    if settings.max_upload_size_mb <= 0:
        errors.append("max_upload_size_mb must be greater than zero.")

    if not settings.supported_extensions:
        errors.append("supported_extensions must not be empty.")

    # Rate limit validation
    for attr in [
        "rate_limit_auth_requests",
        "rate_limit_upload_requests",
        "rate_limit_rag_requests",
        "rate_limit_general_requests",
    ]:
        if hasattr(settings, attr) and getattr(settings, attr) <= 0:
            errors.append(f"{attr} must be greater than zero.")

    # Path validation - ensure we can write to required directories
    required_paths = [
        settings.upload_dir,
        settings.faiss_dir,
        settings.metadata_dir,
        settings.log_directory,
    ]

    for path in required_paths:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create or access directory {path}: {e}")

    if errors:
        error_msg = "\n".join([f"- {err}" for err in errors])
        raise ValueError(f"Configuration validation failed:\n{error_msg}")
