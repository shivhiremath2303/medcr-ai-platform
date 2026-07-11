from fastapi import APIRouter, HTTPException, Depends, Request

from app.schemas.answer import AnswerResponse
from app.schemas.question import QuestionRequest
from app.services.rag.rag_service import RAGService
from app.di import get_rag_service
from app.core.security.dependencies import get_current_active_user, CurrentUser
from app.core.security.rate_limiter import get_rate_limiter_service
from app.core.observability.logger import get_logger

logger = get_logger(__name__)

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
    current_user: CurrentUser = Depends(get_current_active_user),
    limiter=Depends(get_rate_limiter_service),
):
    """
    Ask a question about the uploaded legal documents.
    """

    # Rate limit by user
    rl = limiter.check_rate_limit(current_user.user_id, "/rag/ask", "POST")
    if not rl.allowed:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    try:
        answer_data = rag_service.answer_question(
            question=request.question,
            k=request.k,
        )

        logger.info(
            "RAG question asked",
            extra_data={
                "user_id": current_user.user_id,
                "question_len": len(request.question),
            },
        )

        return AnswerResponse(
            answer=answer_data["answer"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
