from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from app.core.observability.logger import get_logger
from app.core.security.dependencies import (
    CurrentUser,
    RoleChecker,
    get_current_active_user,
)
from app.core.security.rate_limiter import RateLimiterService
from app.di import get_document_service, get_rate_limiter_service, get_storage_provider
from app.domain.models.user import UserRole
from app.domain.repositories.storage_provider import StorageProvider
from app.services.document.document_service import DocumentService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    storage: StorageProvider = Depends(get_storage_provider),
    document_service: DocumentService = Depends(get_document_service),
    current_user: CurrentUser = Depends(get_current_active_user),
    _role: CurrentUser = Depends(RoleChecker([UserRole.ADMIN, UserRole.LAWYER])),
    limiter: RateLimiterService = Depends(get_rate_limiter_service),
):
    """
    Upload and index a legal document.
    """

    # Rate limit by user id
    if not await limiter.check(current_user.user_id, request.url.path, request.method):
        raise HTTPException(status_code=429, detail="Too Many Requests")

    try:
        # Save will validate file type/size/etc. and raise ValueError on invalid uploads
        saved_path = storage.save(file)

        result = document_service.ingest_document(str(saved_path))

        logger.info(
            "Document uploaded",
            extra_data={"user_id": current_user.user_id, "filename": file.filename},
        )

        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "chunks": result["chunk_count"],
        }

    except ValueError as e:
        logger.warning(
            "Upload validation failed",
            extra_data={"user_id": current_user.user_id, "reason": str(e)},
        )
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.error(
            "Upload processing error",
            extra_data={"user_id": current_user.user_id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        ) from e
