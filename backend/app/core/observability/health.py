from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List


class HealthCheck(ABC):
    """
    Interface for a single health check.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def check(self) -> Dict[str, Any]:
        pass


class HealthService:
    """
    Coordinates health checks for the application.
    """

    def __init__(self, version: str, environment: str):
        self.version = version
        self.environment = environment
        self.readiness_checks: List[HealthCheck] = []

    def add_readiness_check(self, check: HealthCheck) -> None:
        self.readiness_checks.append(check)

    def get_liveness(self) -> Dict[str, Any]:
        return {
            "status": "up",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_readiness(self) -> Dict[str, Any]:
        overall_status = "up"
        check_results = {}

        for check in self.readiness_checks:
            result = await check.check()
            check_results[check.name] = result
            if result.get("status") != "up":
                overall_status = "down"

        return {
            "status": overall_status,
            "version": self.version,
            "environment": self.environment,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": check_results,
        }

    async def get_health(self) -> Dict[str, Any]:
        # Full health report including readiness details
        return await self.get_readiness()
