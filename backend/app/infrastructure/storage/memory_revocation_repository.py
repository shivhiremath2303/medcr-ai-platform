import time
from typing import Dict
from app.domain.repositories.revocation_repository import RevocationRepository


class MemoryRevocationRepository(RevocationRepository):
    """
    In-memory implementation for token revocation.
    """

    def __init__(self):
        self._revoked_tokens: Dict[str, float] = {}

    def revoke(self, token_id: str, ttl: int) -> None:
        expiry = time.time() + ttl
        self._revoked_tokens[token_id] = expiry

    def is_revoked(self, token_id: str) -> bool:
        expiry = self._revoked_tokens.get(token_id)
        if not expiry:
            return False

        if time.time() > expiry:
            del self._revoked_tokens[token_id]
            return False

        return True

    def cleanup_expired(self) -> None:
        """Helper for background cleanup."""
        now = time.time()
        expired = [tid for tid, exp in self._revoked_tokens.items() if now > exp]
        for tid in expired:
            del self._revoked_tokens[tid]
