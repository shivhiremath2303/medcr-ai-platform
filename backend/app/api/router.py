from fastapi import APIRouter

from app.api.routes.documents import router as document_router
from app.api.routes.rag import router as rag_router

router = APIRouter()

router.include_router(document_router)
router.include_router(rag_router)


@router.get("/")
def home():
    return {
        "message": "Welcome to MedCR AI Platform",
        "status": "Backend is running successfully!",
    }
