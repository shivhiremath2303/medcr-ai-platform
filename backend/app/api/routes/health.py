from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.observability.health import HealthService
from app.di import get_health_service

router = APIRouter(
    prefix="/health",
    tags=["Observability"],
)


@router.get("", summary="Full health report")
async def health(health_service: HealthService = Depends(get_health_service)):
    report = await health_service.get_health()
    status_code = 200 if report["status"] == "up" else 503
    return JSONResponse(content=report, status_code=status_code)


@router.get("/live", summary="Liveness probe")
async def live(health_service: HealthService = Depends(get_health_service)):
    return health_service.get_liveness()


@router.get("/ready", summary="Readiness probe")
async def ready(health_service: HealthService = Depends(get_health_service)):
    report = await health_service.get_readiness()
    status_code = 200 if report["status"] == "up" else 503
    return JSONResponse(content=report, status_code=status_code)
