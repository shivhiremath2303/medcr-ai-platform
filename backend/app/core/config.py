from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = medcr-ai-platform/
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str
    app_version: str
    app_description: str
    gemini_api_key: str

    debug: bool

    host: str
    port: int

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


print("BASE_DIR:", BASE_DIR)
print("ENV FILE:", BASE_DIR / ".env")

settings = Settings()