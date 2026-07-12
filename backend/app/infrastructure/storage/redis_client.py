from typing import Optional

import redis

from app.core.observability.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """
    Wrapper for Redis connection management.
    """

    def __init__(self, redis_url: str, timeout: int = 5):
        self.redis_url = redis_url
        self.timeout = timeout
        self._client: Optional[redis.Redis] = None

    def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self._client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=self.timeout,
            )
            self._client.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None

    @property
    def client(self) -> redis.Redis:
        """Get the active Redis client."""
        if self._client is None:
            self.connect()
        if self._client is None:
            raise ConnectionError("Redis client is not connected.")
        return self._client

    def is_available(self) -> bool:
        """Check if Redis is reachable."""
        try:
            if self._client is None:
                self.connect()
            return self._client.ping() if self._client else False
        except Exception:
            return False
