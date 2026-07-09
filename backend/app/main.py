from fastapi import FastAPI
from app.api.routes.documents import router as document_router
from app.api.routes.rag import router as rag_router
from app.api.router import router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.include_router(router)
app.include_router(document_router)