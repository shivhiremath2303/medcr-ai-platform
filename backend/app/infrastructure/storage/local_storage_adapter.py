import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.observability.logger import get_logger
from app.domain.repositories.storage_provider import StorageProvider

logger = get_logger(__name__)
settings = get_settings()


class LocalStorageAdapter(StorageProvider):
    """
    Local filesystem implementation of StorageProvider.
    """

    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir

    def save(self, file: UploadFile) -> Path:
        # Basic validations
        if not file or not file.filename:
            raise ValueError("No file provided")

        extension = Path(file.filename).suffix.lower()
        if extension not in settings.supported_extensions:
            raise ValueError("Unsupported file extension")

        if file.content_type not in settings.allowed_mime_types:
            raise ValueError("Unsupported MIME type")

        # Ensure directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        unique_filename = f"{uuid4()}{extension}"
        destination = self.upload_dir / unique_filename

        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        total_written = 0

        try:
            with destination.open("wb") as buffer:
                # Stream copy in chunks and enforce size limit
                while True:
                    chunk = file.file.read(8192)
                    if not chunk:
                        break
                    total_written += len(chunk)
                    if total_written > max_bytes:
                        # Cleanup partial file
                        buffer.close()
                        try:
                            destination.unlink(missing_ok=True)
                        except Exception:
                            pass
                        raise ValueError("File size exceeds the configured maximum")
                    buffer.write(chunk)
        finally:
            try:
                file.file.close()
            except Exception:
                pass

        logger.info(
            "File saved", extra_data={"path": str(destination), "size": total_written}
        )
        return destination
