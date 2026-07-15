import time

from app.domain.repositories.rate_limiter import RateLimiter
from app.infrastructure.storage.redis_client import RedisClient


class RedisRateLimiter(RateLimiter):
    """
    Distributed Redis-backed rate limiter with Atomic scripts.
    Prevents race conditions in horizontal multi-replica deployments.
    Implements Milestone 10.3.5.
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_wrapper = redis_client
        self.key_prefix = "ratelimit:"
        # Lua script for atomic increment and expire
        self._lua_script = """
        local current = redis.call("INCR", KEYS[1])
        if current == 1 then
            redis.call("EXPIRE", KEYS[1], ARGV[1])
        end
        return current
        """

    async def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        full_key = f"{self.key_prefix}{key}"
        client = self.redis_wrapper.client

        try:
            # Use Lua script for guaranteed atomicity (10.3.5)
            current_count = client.eval(self._lua_script, 1, full_key, window)

            if int(current_count) > limit:
                return True

            return False
        except Exception:
            # Fallback for transient Redis issues
            return False
