from app.core.config.base import Settings
from pydantic import Field

class ProductionSettings(Settings):
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"

    # In production, we require these to be set via environment variables
    # Pydantic will raise an error if they are missing and no default is provided
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")

    # Production often needs different host/port or behind a reverse proxy
    host: str = "0.0.0.0"
    port: int = 8000
