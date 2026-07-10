from app.core.config.base import Settings, BASE_DIR

class TestingSettings(Settings):
    environment: str = "testing"
    debug: bool = True
    log_level: str = "DEBUG"

    # Isolated storage for tests
    upload_dir: str = str(BASE_DIR / "backend" / "tests" / "uploads")
    faiss_dir: str = str(BASE_DIR / "backend" / "tests" / "data" / "faiss")
    metadata_dir: str = str(BASE_DIR / "backend" / "tests" / "data" / "metadata")
    log_directory: str = str(BASE_DIR / "backend" / "tests" / "logs")

    # Speed up tests
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Allow tests to run without real API key if they mock the provider
    gemini_api_key: str = "test-key"
