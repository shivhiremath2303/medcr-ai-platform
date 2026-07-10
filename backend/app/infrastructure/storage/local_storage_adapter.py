import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from app.domain.repositories.storage_provider import StorageProvider


class LocalStorageAdapter(StorageProvider):
    """
    Local filesystem implementation of StorageProvider.
    """

    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir

    def save(self, file: UploadFile) -> Path:
        extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid4()}{extension}"

        # Ensure directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        destination = self.upload_dir / unique_filename

        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            file.file.close()

        return destination
