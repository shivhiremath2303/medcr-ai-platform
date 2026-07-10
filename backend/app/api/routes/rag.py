from fastapi import APIRouter, HTTPException, Depends

from app.schemas.answer import AnswerResponse
from app.schemas.question import QuestionRequest
from app.services.rag.rag_service import RAGService
from app.di import get_rag_service

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post(
    "/ask",
    response_model=AnswerResponse,
)
async def ask_question(
    request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Ask a question about the uploaded legal documents.
    """

    try:
        answer = rag_service.answer_question(
            question=request.question,
            k=request.k,
        )

        return AnswerResponse(
            answer=answer,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )