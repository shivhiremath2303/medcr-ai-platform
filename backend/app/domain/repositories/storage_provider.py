from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from fastapi import UploadFile


class StorageProvider(ABC):
    """
    Interface for file storage operations.
    Enhanced with Multi-Tenant isolation (10.4.5).
    """

    @abstractmethod
    def save(self, file: UploadFile, tenant_id: Optional[str] = None) -> Path:
        """
        Save an uploaded file and return its path.
        If tenant_id is provided, the file should be isolated to that tenant.
        """

    @abstractmethod
    def delete(self, file_path: Path) -> bool:
        """Delete a file from storage."""

    @abstractmethod
    def exists(self, file_path: Path) -> bool:
        """Check if a file exists."""
