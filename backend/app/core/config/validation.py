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

        if settings.jwt_secret_key == "development-secret-key-change-me-in-production":
            errors.append("JWT_SECRET_KEY must be changed in production environment.")

    # Generic validation
    if settings.chunk_overlap >= settings.chunk_size:
        errors.append(f"chunk_overlap ({settings.chunk_overlap}) must be smaller than chunk_size ({settings.chunk_size}).")

    if settings.default_top_k <= 0:
        errors.append(f"default_top_k ({settings.default_top_k}) must be greater than zero.")

    # Path validation - ensure we can write to required directories
    required_paths = [
        settings.upload_dir,
        settings.faiss_dir,
        settings.metadata_dir,
        settings.log_directory
    ]

    for path in required_paths:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create or access directory {path}: {e}")

    if errors:
        error_msg = "\n".join([f"- {err}" for err in errors])
        raise ValueError(f"Configuration validation failed:\n{error_msg}")
