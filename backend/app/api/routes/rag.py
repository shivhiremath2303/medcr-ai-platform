from fastapi import APIRouter, HTTPException, Depends, Request

from app.schemas.answer import AnswerResponse
from app.schemas.question import QuestionRequest
from app.services.rag.rag_service import RAGService
from app.di import get_rag_service, get_rate_limiter_service
from app.core.security.dependencies import get_current_active_user, CurrentUser
from app.core.security.rate_limiter import RateLimiterService
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
    request: Request, # for router path
    question_request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service),
    current_user: CurrentUser = Depends(get_current_active_user),
    limiter: RateLimiterService = Depends(get_rate_limiter_service),
):
    """
    Ask a question about the uploaded legal documents.
    """

    # Rate limit by user
    if not await limiter.check(current_user.user_id, request.url.path, request.method):
        raise HTTPException(status_code=429, detail="Too Many Requests")

    try:
        answer_data = rag_service.answer_question(
            question=question_request.question,
            k=question_request.k,
        )

        logger.info(
            "RAG question asked",
            extra_data={
                "user_id": current_user.user_id,
                "question_len": len(question_request.question),
            },
        )

        return AnswerResponse(**answer_data)

    except Exception as e:
        logger.error(f"RAG error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )
