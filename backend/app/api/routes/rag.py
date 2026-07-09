from fastapi import APIRouter, HTTPException

from app.schemas.answer import AnswerResponse
from app.schemas.question import QuestionRequest
from app.services.rag.rag_service import RAGService

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)

rag_service = RAGService()


@router.post(
    "/ask",
    response_model=AnswerResponse,
)
async def ask_question(
    request: QuestionRequest,
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