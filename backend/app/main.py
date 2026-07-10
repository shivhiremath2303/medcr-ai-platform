from fastapi import FastAPI
from app.api.routes.documents import router as document_router
from app.api.routes.rag import router as rag_router
from app.api.router import router
from app.core.config import settings
from app.core.logger import get_logger

# Import composition root
from app import di

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: initializing vector store...")
    loaded = di.init_vector_store()
    if loaded:
        logger.info("Loaded existing FAISS index on startup.")
    else:
        logger.info("No FAISS index found during startup; a new index will be created on ingest.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown: persisting vector store...")
    di.shutdown_vector_store_save()
    logger.info("Shutdown complete.")


app.include_router(router)
app.include_router(document_router)
app.include_router(rag_router)