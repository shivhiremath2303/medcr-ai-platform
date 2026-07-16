import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Set

from fastapi import UploadFile

from app.domain.repositories.storage_provider import StorageProvider

logger = logging.getLogger(__name__)


class LocalStorageAdapter(StorageProvider):
    """
    Optimized Local filesystem implementation of StorageProvider.
    Supports physical isolation via tenant-specific subdirectories (10.4.5).
    """

    def __init__(
        self,
        upload_dir: Path,
        max_size_mb: int = 20,
        allowed_extensions: Set[str] | None = None,
    ):
        self.upload_dir = upload_dir
        self.max_size_mb = max_size_mb
        self.allowed_extensions = allowed_extensions or {".pdf", ".docx"}
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file: UploadFile, tenant_id: Optional[str] = None) -> Path:
        """
        Saves an uploaded file to the local directory.
        If tenant_id is provided, saves to {upload_dir}/{tenant_id}/{filename}.
        """
        filename = os.path.basename(file.filename or "unnamed_file")
        extension = Path(filename).suffix.lower()

        # 1. Validation (Security/Sanity)
        if extension not in self.allowed_extensions:
            raise ValueError(f"File extension {extension} not allowed.")

        # 2. Resolve Tenant-specific path
        target_dir = self.upload_dir
        if tenant_id:
            target_dir = self.upload_dir / tenant_id
            target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / filename

        # 3. Optimized Streaming Write (Buffered)
        buffer_size = 1024 * 1024  # 1MB buffer

        try:
            with open(target_path, "wb") as buffer:
                while True:
                    chunk = file.file.read(buffer_size)
                    if not chunk:
                        break
                    buffer.write(chunk)

            logger.info(
                f"File saved successfully to {target_path} (Tenant: {tenant_id})"
            )
            return target_path

        except Exception as e:
            logger.error(f"Failed to save file {filename} for tenant {tenant_id}: {e}")
            if target_path.exists():
                target_path.unlink()
            raise OSError(f"Could not persist file to storage: {e}") from e

    def delete(self, file_path: Path) -> bool:
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def exists(self, file_path: Path) -> bool:
        return file_path.exists()
