from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = medcr-ai-platform/
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "medcr-ai-platform"
    app_version: str = "1.0.0"
    app_description: str = "Production-grade Legal AI RAG Platform"
    gemini_api_key: str = ""

    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    # ----------------------------
    # File Upload Settings
    # ----------------------------
    upload_dir: Path = BASE_DIR / "backend" / "uploads" / "documents"
    max_file_size_mb: int = 20

    faiss_dir: Path = BASE_DIR / "backend" / "data" / "faiss"
    metadata_dir: Path = BASE_DIR / "backend" / "data" / "metadata"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()