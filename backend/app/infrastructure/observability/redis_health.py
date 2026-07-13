from typing import Any, Dict

from app.core.observability.health import HealthCheck
from app.infrastructure.storage.redis_client import RedisClient


class RedisHealthCheck(HealthCheck):
    """
    Health check for Redis persistence/cache.
    """

    def __init__(self, redis_client: RedisClient, critical: bool = True):
        self.redis_wrapper = redis_client
        self._critical = critical

    @property
    def name(self) -> str:
        return "redis"

    @property
    def critical(self) -> bool:
        return self._critical

    async def check(self) -> Dict[str, Any]:
        try:
            if self.redis_wrapper.is_available():
                return {"status": "up"}
            return {
                "status": "down",
                "error": "Redis is unreachable",
                "critical": self.critical
            }
        except Exception as e:
            return {
                "status": "down",
                "error": str(e),
                "critical": self.critical
            }
