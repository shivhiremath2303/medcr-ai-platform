from abc import ABC, abstractmethod
from typing import Optional


class SecretProvider(ABC):
    """
    Interface for retrieving sensitive credentials and configuration.
    Decouples the application from the underlying secret storage (Env, Vault, Docker Secrets).
    """

    @abstractmethod
    def get_secret(self, key: str, default: str | None = None) -> str | None:
        """
        Fetch a secret by key.
        Returns the secret value or default if not found.
        """
        pass

    @abstractmethod
    def refresh(self) -> None:
        """
        Force a refresh of cached secrets (if applicable).
        Supports future dynamic key rotation without process restart.
        """
        pass
