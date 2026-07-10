from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from app.core.config import settings
from app.domain.repositories.storage_provider import StorageProvider


class LocalStorageAdapter(StorageProvider):
    """
    Adapter for local file system storage.
    """

    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    def save(self, file: UploadFile) -> Path:
        extension = Path(file.filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        settings.upload_dir.mkdir(parents=True, exist_ok=True)

        unique_filename = f"{uuid4().hex}{extension}"
        destination = settings.upload_dir / unique_filename

        with destination.open("wb") as buffer:
            buffer.write(file.file.read())

        return destination
