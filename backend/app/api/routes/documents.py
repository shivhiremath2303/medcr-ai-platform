from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, Query

from app.core.observability.logger import get_logger
from app.core.security.authorization import AuthorizationService
from app.core.security.dependencies import (
    CurrentUser,
    check_payload_size,
    get_authorization_service,
    get_current_active_user,
    rate_limit,
    require_permission,
)
from app.di import (
    get_audit_service,
    get_authorization_service,
    get_document_service,
    get_storage_provider,
    get_background_task_provider,
)
from app.domain.models.background_task import TaskPriority
from app.domain.models.audit import AuditEventType
from app.domain.models.authorization import Permission
from app.domain.repositories.storage_provider import StorageProvider
from app.services.audit.audit_service import AuditService
from app.services.document.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(rate_limit)],
)

logger = get_logger(__name__)


@router.post("/upload", dependencies=[Depends(check_payload_size)])
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    storage: StorageProvider = Depends(get_storage_provider),
    document_service: DocumentService = Depends(get_document_service),
    audit_service: AuditService = Depends(get_audit_service),
    background_tasks: BackgroundTaskProvider = Depends(get_background_task_provider),
    current_user: CurrentUser = Depends(get_current_active_user),
    _permission: CurrentUser = Depends(require_permission(Permission.DOC_UPLOAD)),
):
    """
    Upload and index a legal document in the background.
    Requires Permission.DOC_UPLOAD.
    """

    try:
        # 1. Synchronous validation and saving to storage
        saved_path = storage.save(file)

        # 2. Enqueue Ingestion for background processing (10.3.2)
        task_id = await background_tasks.enqueue(
            name="ingest_document",
            payload={
                "file_path": str(saved_path),
                "owner_id": current_user.user_id
            },
            priority=TaskPriority.DEFAULT
        )

        audit_service.log(
            AuditEventType.DOC_UPLOAD,
            action="upload_document_async",
            status="success",
            user_id=current_user.user_id,
            details={"filename": file.filename, "task_id": task_id},
        )

        return {
            "message": "Document upload accepted and processing started",
            "filename": file.filename,
            "task_id": task_id,
        }

    except ValueError as e:
        audit_service.log(
            AuditEventType.DOC_UPLOAD,
            action="upload_document",
            status="failure",
            user_id=current_user.user_id,
            details={"reason": "validation_error", "error": str(e)},
        )
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    except Exception as e:
        audit_service.log(
            AuditEventType.DOC_UPLOAD,
            action="upload_document",
            status="failure",
            user_id=current_user.user_id,
            details={"reason": "internal_error", "error": str(e)},
        )
        logger.error(
            "Upload processing error",
            extra_data={"user_id": current_user.user_id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        ) from e


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: CurrentUser = Depends(get_current_active_user),
    _permission: CurrentUser = Depends(require_permission(Permission.DOC_READ)),
):
    """
    Retrieve document metadata.
    Validates granular permissions and resource ownership.
    """
    document = document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Policy Check: Ownership or Admin
    if not authz_service.is_resource_owner(current_user.to_user(), document.owner_id):
        # Service already logs ownership failure
        raise HTTPException(
            status_code=403, detail="Access denied to this specific resource"
        )

    audit_service.log(
        AuditEventType.DOC_READ,
        action="read_document_metadata",
        user_id=current_user.user_id,
        resource_id=document_id,
    )

    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "page_count": document.page_count,
        "owner_id": document.owner_id,
    }


@router.get("/", summary="List documents with pagination")
async def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    document_service: DocumentService = Depends(get_document_service),
    current_user: CurrentUser = Depends(get_current_active_user),
    _permission: CurrentUser = Depends(require_permission(Permission.DOC_READ)),
):
    """
    List all documents accessible to the user with pagination support (10.3.7).
    """
    documents = await document_service.list_documents(limit=limit, offset=offset)

    # In a full implementation, we would filter by owner_id here or in the repo
    return {
        "total": len(documents), # Simplified for 10.3.7
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "document_id": doc.document_id,
                "filename": doc.filename,
                "page_count": doc.page_count,
                "owner_id": getattr(doc, "owner_id", None)
            }
            for doc in documents
        ]
    }
