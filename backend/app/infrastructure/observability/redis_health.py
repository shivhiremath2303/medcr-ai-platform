from typing import Dict, Any
from app.core.observability.health import HealthCheck
from app.infrastructure.storage.redis_client import RedisClient

class RedisHealthCheck(HealthCheck):
    def __init__(self, redis_client: RedisClient):
        self.redis_wrapper = redis_client

    @property
    def name(self) -> str:
        return "redis"

    async def check(self) -> Dict[str, Any]:
        if self.redis_wrapper.is_available():
            return {"status": "up"}
        return {"status": "down", "error": "Redis is unreachable"}
