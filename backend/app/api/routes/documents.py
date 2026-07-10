from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from app.services.document.document_service import DocumentService
from app.domain.repositories.storage_provider import StorageProvider
from app.api.dependencies import get_document_service, get_storage_provider

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    storage: StorageProvider = Depends(get_storage_provider),
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Upload and index a legal document.
    """

    try:
        saved_path = storage.save(file)

        result = document_service.ingest_document(
            str(saved_path)
        )

        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "chunks": result["chunk_count"],
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
