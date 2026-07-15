from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.security.dependencies import rate_limit, require_permission
from app.di import get_metrics_provider
from app.domain.models.authorization import Permission
from app.infrastructure.observability.prometheus_metrics import (
    PrometheusMetricsProvider,
)

router = APIRouter(
    tags=["Observability"],
    dependencies=[Depends(rate_limit)],
)


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    dependencies=[Depends(require_permission(Permission.ADMIN_METRICS))],
)
async def metrics():
    """
    Expose Prometheus metrics for scraping.
    Requires Permission.ADMIN_METRICS.
    """
    provider = get_metrics_provider()
    if isinstance(provider, PrometheusMetricsProvider):
        return Response(
            content=generate_latest(provider.registry), media_type=CONTENT_TYPE_LATEST
        )
    return Response(content=b"", media_type=CONTENT_TYPE_LATEST)
