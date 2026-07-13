from app.domain.repositories.revocation_repository import RevocationRepository
from app.infrastructure.storage.redis_client import RedisClient


class RedisRevocationRepository(RevocationRepository):
    """
    Redis implementation for token revocation, session management,
    and account lockout tracking.
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_wrapper = redis_client
        self.revoked_prefix = "revoked:"
        self.session_prefix = "sessions:"
        self.failed_login_prefix = "failed_login:"
        self.lockout_prefix = "lockout:"

    def revoke(self, identifier: str, ttl: int) -> None:
        key = f"{self.revoked_prefix}{identifier}"
        self.redis_wrapper.client.setex(key, ttl, "1")

    def is_revoked(self, identifier: str) -> bool:
        key = f"{self.revoked_prefix}{identifier}"
        return self.redis_wrapper.client.exists(key) > 0

    def add_session(self, user_id: str, sid: str, ttl: int) -> None:
        key = f"{self.session_prefix}{user_id}"
        # Store session ID in a set for the user
        self.redis_wrapper.client.sadd(key, sid)
        self.redis_wrapper.client.expire(key, ttl)

    def remove_session(self, user_id: str, sid: str) -> None:
        key = f"{self.session_prefix}{user_id}"
        self.redis_wrapper.client.srem(key, sid)

    def get_user_sessions(self, user_id: str) -> list[str]:
        key = f"{self.session_prefix}{user_id}"
        sessions = self.redis_wrapper.client.smembers(key)
        return [s.decode("utf-8") if isinstance(s, bytes) else s for s in sessions]

    def increment_failed_login(self, identifier: str, window: int) -> int:
        key = f"{self.failed_login_prefix}{identifier}"
        count = self.redis_wrapper.client.incr(key)
        if count == 1:
            self.redis_wrapper.client.expire(key, window)
        return count

    def reset_failed_login(self, identifier: str) -> None:
        key = f"{self.failed_login_prefix}{identifier}"
        self.redis_wrapper.client.delete(key)

    def set_lockout(self, identifier: str, duration: int) -> None:
        key = f"{self.lockout_prefix}{identifier}"
        self.redis_wrapper.client.setex(key, duration, "1")

    def is_locked_out(self, identifier: str) -> bool:
        key = f"{self.lockout_prefix}{identifier}"
        return self.redis_wrapper.client.exists(key) > 0
