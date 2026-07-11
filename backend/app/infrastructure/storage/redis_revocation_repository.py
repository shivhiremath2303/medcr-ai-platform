from app.domain.repositories.revocation_repository import RevocationRepository
from app.infrastructure.storage.redis_client import RedisClient


class RedisRevocationRepository(RevocationRepository):
    """
    Redis implementation for token revocation (blacklist).
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_wrapper = redis_client
        self.key_prefix = "revoked:"

    def revoke(self, token_id: str, ttl: int) -> None:
        key = f"{self.key_prefix}{token_id}"
        self.redis_wrapper.client.setex(key, ttl, "1")

    def is_revoked(self, token_id: str) -> bool:
        key = f"{self.key_prefix}{token_id}"
        return self.redis_wrapper.client.exists(key) > 0
