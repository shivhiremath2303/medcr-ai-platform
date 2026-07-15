import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional


class HealthCheck(ABC):
    """
    Interface for a single health check.
    Supports critical and non-critical (degraded) status.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def critical(self) -> bool:
        """If True, failure marks the whole service as DOWN (Readiness = False)."""
        return True

    @abstractmethod
    async def check(self) -> Dict[str, Any]:
        """Returns health details for this component."""
        pass


class HealthService:
    """
    Enterprise Health Service.
    Coordinates deep health checks with caching and degraded state support.
    Implements Milestone 10.2.5.
    """

    def __init__(self, version: str, environment: str, cache_ttl: int = 30):
        self.version = version
        self.environment = environment
        self.readiness_checks: List[HealthCheck] = []
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Any] | None = None
        self._last_check: float = 0

    def add_readiness_check(self, check: HealthCheck) -> None:
        self.readiness_checks.append(check)

    def get_liveness(self) -> Dict[str, Any]:
        """Simple liveness probe: App is alive."""
        return {
            "status": "up",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def get_readiness(self, force: bool = False) -> Dict[str, Any]:
        """
        Readiness probe: App can accept traffic.
        Returns 'down' if any critical dependency is down.
        """
        now = time.time()
        if not force and self._cache and (now - self._last_check) < self.cache_ttl:
            return self._cache

        overall_status = "up"
        check_results = {}
        has_degraded = False

        for check in self.readiness_checks:
            try:
                result = await check.check()
                status = result.get("status", "down")
                check_results[check.name] = result

                if status != "up":
                    if check.critical:
                        overall_status = "down"
                    else:
                        has_degraded = True
            except Exception as e:
                check_results[check.name] = {"status": "down", "error": str(e)}
                if check.critical:
                    overall_status = "down"
                else:
                    has_degraded = True

        if overall_status == "up" and has_degraded:
            overall_status = "degraded"

        report = {
            "status": overall_status,
            "version": self.version,
            "environment": self.environment,
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": check_results,
        }

        self._cache = report
        self._last_check = now
        return report

    async def get_health(self) -> Dict[str, Any]:
        """Full health report for administration."""
        return await self.get_readiness(force=True)
