import time

from app.domain.repositories.rate_limiter import RateLimiter
from app.infrastructure.storage.redis_client import RedisClient


class RedisRateLimiter(RateLimiter):
    """
    Redis-backed fixed window rate limiter.
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_wrapper = redis_client
        self.key_prefix = "ratelimit:"

    async def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        full_key = f"{self.key_prefix}{key}"
        client = self.redis_wrapper.client

        # Use a Lua script or simple increment with expire
        # Simplified version:
        current = client.get(full_key)

        if current is not None and int(current) >= limit:
            return True

        # Atomically increment and set TTL if new
        pipeline = client.pipeline()
        pipeline.incr(full_key)
        pipeline.expire(full_key, window, nx=True)
        pipeline.execute()

        return False
