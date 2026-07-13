from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.observability.health import HealthService
from app.core.security.dependencies import rate_limit, require_permission
from app.di import get_health_service
from app.domain.models.authorization import Permission

router = APIRouter(
    prefix="/health",
    tags=["Observability"],
    dependencies=[Depends(rate_limit)],
)


@router.get(
    "",
    summary="Full health report",
    dependencies=[Depends(require_permission(Permission.ADMIN_SYSTEM_HEALTH))],
)
async def health(health_service: HealthService = Depends(get_health_service)):
    """
    Get full health diagnostic report.
    Requires Permission.ADMIN_SYSTEM_HEALTH.
    """
    report = await health_service.get_health()
    status_code = 200 if report["status"] == "up" else 503
    return JSONResponse(content=report, status_code=status_code)


@router.get("/live", summary="Liveness probe")
async def live(health_service: HealthService = Depends(get_health_service)):
    """Public probe for Kubernetes liveness checks."""
    return health_service.get_liveness()


@router.get("/ready", summary="Readiness probe")
async def ready(health_service: HealthService = Depends(get_health_service)):
    """Public probe for Kubernetes readiness checks."""
    report = await health_service.get_readiness()
    status_code = 200 if report["status"] == "up" else 503
    return JSONResponse(content=report, status_code=status_code)
