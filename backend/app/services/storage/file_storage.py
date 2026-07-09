from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class FileStorageService:
    """
    Handles storing uploaded files on disk.
    """

    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    def save(self, file: UploadFile) -> Path:
        """
        Save an uploaded file and return its saved path.
        """

        extension = Path(file.filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        # Ensure upload directory exists
        settings.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        unique_filename = (
            f"{uuid4().hex}{extension}"
        )

        destination = (
            settings.upload_dir / unique_filename
        )

        with destination.open("wb") as buffer:
            buffer.write(file.file.read())

        return destination