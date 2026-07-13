from abc import ABC, abstractmethod


class RevocationRepository(ABC):
    """
    Interface for managing revoked tokens and sessions.
    Supports blacklisting of JTI (JWT IDs) and SID (Session IDs).
    """

    @abstractmethod
    def revoke(self, identifier: str, ttl: int) -> None:
        """Revoke a token or session ID for a given TTL."""

    @abstractmethod
    def is_revoked(self, identifier: str) -> bool:
        """Check if an identifier (JTI or SID) has been revoked."""

    @abstractmethod
    def add_session(self, user_id: str, sid: str, ttl: int) -> None:
        """Track an active session for a user."""

    @abstractmethod
    def remove_session(self, user_id: str, sid: str) -> None:
        """Remove a specific active session."""

    @abstractmethod
    def get_user_sessions(self, user_id: str) -> list[str]:
        """List active session IDs for a user."""

    @abstractmethod
    def increment_failed_login(self, identifier: str, window: int) -> int:
        """Increment and return failed login count for a user/IP."""

    @abstractmethod
    def reset_failed_login(self, identifier: str) -> None:
        """Reset failed login count."""

    @abstractmethod
    def set_lockout(self, identifier: str, duration: int) -> None:
        """Set a lockout flag for an identifier."""

    @abstractmethod
    def is_locked_out(self, identifier: str) -> bool:
        """Check if an identifier is currently locked out."""
