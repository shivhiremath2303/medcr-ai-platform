import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import di
from app.api.router import router
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as document_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.rag import router as rag_router
from app.core.config import get_settings
from app.core.observability.context import get_request_id
from app.core.observability.logger import get_logger, setup_logging
from app.core.observability.middleware import ObservabilityMiddleware
from app.core.observability.telemetry import setup_telemetry
from app.core.security.middleware import setup_security

settings = get_settings()

# Setup logging as early as possible
setup_logging(
    app_name=settings.app_name,
    app_version=settings.app_version,
    environment=settings.environment,
    log_level=settings.log_level,
    json_format=settings.log_json,
)

logger = get_logger(__name__)


async def periodic_cleanup() -> None:
    """
    Background loop for maintenance tasks.
    """
    cleanup_service = di.get_cleanup_service()
    while True:
        await asyncio.sleep(settings.cleanup_interval_seconds)
        await cleanup_service.run_cleanup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    start_time = time.perf_counter()
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} in {settings.environment} mode"
    )

    logger.info("Initializing infrastructure and repositories...")
    loaded = di.init_vector_store()

    if loaded:
        logger.info("Loaded existing FAISS index on startup.")
    else:
        logger.info("No FAISS index found; a new one will be created on first ingestion.")

    # Start periodic cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())

    duration = time.perf_counter() - start_time
    logger.info(f"Application startup complete in {duration:.4f}s")

    yield

    # Shutdown logic
    logger.info("Application shutdown started: persisting resources...")
    cleanup_task.cancel()
    di.shutdown_vector_store_save()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# Setup Security (CORS, Headers)
setup_security(app, settings)

# Add observability middleware
app.add_middleware(ObservabilityMiddleware)

# Setup OpenTelemetry
if settings.otel_enabled:
    setup_telemetry(
        app,
        service_name=settings.otel_service_name,
        otel_endpoint=settings.otel_exporter_endpoint,
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = get_request_id()
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra_data={"request_id": request_id, "path": request.url.path},
        exc_info=True,
    )

    # In production, do not leak exception details
    detail = "Internal Server Error"
    if settings.environment != "production":
        detail = str(exc)

    return JSONResponse(
        status_code=500,
        content={"detail": detail, "request_id": request_id},
    )


@app.get("/version", tags=["Public"])
async def version():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


# Include routers
app.include_router(router)
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(rag_router)
app.include_router(health_router)
app.include_router(metrics_router)
