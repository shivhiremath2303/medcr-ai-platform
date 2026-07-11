from abc import ABC, abstractmethod


class RevocationRepository(ABC):
    """
    Interface for managing revoked tokens (e.g., JWT blacklisting).
    """

    @abstractmethod
    def revoke(self, token_id: str, ttl: int) -> None:
        """Revoke a token for a given TTL."""

    @abstractmethod
    def is_revoked(self, token_id: str) -> bool:
        """Check if a token has been revoked."""
