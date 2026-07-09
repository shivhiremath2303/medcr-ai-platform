from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document.document_service import DocumentService
from app.services.storage.file_storage import FileStorageService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

storage = FileStorageService()
document_service = DocumentService()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
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