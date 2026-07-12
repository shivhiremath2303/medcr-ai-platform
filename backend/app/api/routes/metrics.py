from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.di import get_metrics_provider
from app.infrastructure.observability.prometheus_metrics import PrometheusMetricsProvider

router = APIRouter(tags=["Observability"])

@router.get("/metrics", summary="Prometheus metrics")
async def metrics():
    provider = get_metrics_provider()
    if isinstance(provider, PrometheusMetricsProvider):
        return Response(content=generate_latest(provider.registry), media_type=CONTENT_TYPE_LATEST)
    return Response(content=b"", media_type=CONTENT_TYPE_LATEST)
