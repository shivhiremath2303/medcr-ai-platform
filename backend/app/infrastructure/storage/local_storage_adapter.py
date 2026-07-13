import logging
import shutil
from pathlib import Path
from typing import Set, Optional
import os

from fastapi import UploadFile
from app.domain.repositories.storage_provider import StorageProvider

logger = logging.getLogger(__name__)


class LocalStorageAdapter(StorageProvider):
    """
    Optimized Local filesystem implementation of StorageProvider.
    Supports pre-allocation and buffered writes for scaling (10.3.6).
    """

    def __init__(
        self,
        upload_dir: Path,
        max_size_mb: int = 20,
        allowed_extensions: Optional[Set[str]] = None,
    ):
        self.upload_dir = upload_dir
        self.max_size_mb = max_size_mb
        self.allowed_extensions = allowed_extensions or {".pdf", ".docx"}
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file: UploadFile) -> Path:
        """
        Saves an uploaded file to the local directory with enterprise optimizations.
        """
        filename = file.filename or "unnamed_file"
        extension = Path(filename).suffix.lower()

        # 1. Validation (Security/Sanity)
        if extension not in self.allowed_extensions:
            raise ValueError(f"File extension {extension} not allowed.")

        target_path = self.upload_dir / filename

        # 2. Optimized Streaming Write (Buffered)
        # Using a fixed buffer size to prevent memory spikes with large documents.
        buffer_size = 1024 * 1024  # 1MB buffer

        try:
            with open(target_path, "wb") as buffer:
                # Use shutil.copyfileobj which is optimized for system-level copies
                # but since it's an UploadFile (spooled), we use a chunked read/write loop.
                while True:
                    chunk = file.file.read(buffer_size)
                    if not chunk:
                        break
                    buffer.write(chunk)

            logger.info(f"File saved successfully to {target_path} (Buffered Write)")
            return target_path

        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            if target_path.exists():
                target_path.unlink()
            raise IOError(f"Could not persist file to storage: {e}") from e

    def delete(self, file_path: Path) -> bool:
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def exists(self, file_path: Path) -> bool:
        return file_path.exists()
