from datetime import datetime

import pytest

from app.core.observability.health import HealthCheck, HealthService


class HealthyCheck(HealthCheck):
    @property
    def name(self):
        return "healthy"

    async def check(self):
        return {"status": "up"}


class UnhealthyCheck(HealthCheck):
    @property
    def name(self):
        return "database"

    async def check(self):
        return {"status": "down"}


def test_liveness():
    service = HealthService(
        version="1.0.0",
        environment="test",
    )

    result = service.get_liveness()

    assert result["status"] == "up"

    datetime.fromisoformat(result["timestamp"])


@pytest.mark.asyncio
async def test_readiness_all_up():
    service = HealthService(
        version="1.0.0",
        environment="test",
    )

    service.add_readiness_check(HealthyCheck())

    result = await service.get_readiness()

    assert result["status"] == "up"
    assert result["version"] == "1.0.0"
    assert result["environment"] == "test"
    assert result["checks"]["healthy"]["status"] == "up"


@pytest.mark.asyncio
async def test_readiness_failure():
    service = HealthService(
        version="1.0.0",
        environment="test",
    )

    service.add_readiness_check(HealthyCheck())
    service.add_readiness_check(UnhealthyCheck())

    result = await service.get_readiness()

    assert result["status"] == "down"
    assert result["checks"]["healthy"]["status"] == "up"
    assert result["checks"]["database"]["status"] == "down"


@pytest.mark.asyncio
async def test_health_delegates_to_readiness():
    service = HealthService(
        version="1.0.0",
        environment="test",
    )

    service.add_readiness_check(HealthyCheck())

    result = await service.get_health()

    assert result["status"] == "up"
