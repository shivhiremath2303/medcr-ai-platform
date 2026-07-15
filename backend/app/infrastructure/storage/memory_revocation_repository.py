import time
from typing import Dict

from app.domain.repositories.revocation_repository import RevocationRepository


class MemoryRevocationRepository(RevocationRepository):
    """
    In-memory implementation for token revocation.
    """

    def __init__(self):
        self._revoked_tokens: Dict[str, float] = {}
        self._sessions: Dict[str, Dict[str, float]] = {}
        self._failed_logins: Dict[str, tuple[int, float]] = {}
        self._lockouts: Dict[str, float] = {}

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

    def add_session(self, user_id: str, sid: str, ttl: int) -> None:
        self._sessions.setdefault(user_id, {})[sid] = time.time() + ttl

    def remove_session(self, user_id: str, sid: str) -> None:
        sessions = self._sessions.get(user_id, {})
        sessions.pop(sid, None)

    def get_user_sessions(self, user_id: str) -> list[str]:
        now = time.time()
        sessions = self._sessions.get(user_id, {})
        expired = [sid for sid, expiry in sessions.items() if expiry <= now]
        for sid in expired:
            del sessions[sid]
        return list(sessions)

    def increment_failed_login(self, identifier: str, window: int) -> int:
        now = time.time()
        count, expiry = self._failed_logins.get(identifier, (0, now + window))
        if expiry <= now:
            count, expiry = 0, now + window
        count += 1
        self._failed_logins[identifier] = (count, expiry)
        return count

    def reset_failed_login(self, identifier: str) -> None:
        self._failed_logins.pop(identifier, None)

    def set_lockout(self, identifier: str, duration: int) -> None:
        self._lockouts[identifier] = time.time() + duration

    def is_locked_out(self, identifier: str) -> bool:
        expiry = self._lockouts.get(identifier)
        if expiry is None:
            return False
        if expiry <= time.time():
            del self._lockouts[identifier]
            return False
        return True
