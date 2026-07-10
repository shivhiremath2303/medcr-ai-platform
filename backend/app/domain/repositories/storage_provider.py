from abc import ABC, abstractmethod
from pathlib import Path
from fastapi import UploadFile


class StorageProvider(ABC):
    """
    Interface for file storage operations.
    """

    @abstractmethod
    def save(self, file: UploadFile) -> Path:
        """
        Save an uploaded file and return its path.
        """
