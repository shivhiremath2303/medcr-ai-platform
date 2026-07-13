from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.observability.logger import get_logger
from app.core.security.dependencies import (
    CurrentUser,
    get_current_active_user,
    rate_limit,
    require_permission,
)
from app.di import get_audit_service, get_rag_service
from app.domain.models.audit import AuditEventType
from app.domain.models.authorization import Permission
from app.schemas.answer import AnswerResponse
from app.schemas.question import QuestionRequest
from app.services.audit.audit_service import AuditService
from app.services.rag.rag_service import RAGService

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    dependencies=[Depends(rate_limit)],
)

logger = get_logger(__name__)


@router.post(
    "/ask",
    response_model=AnswerResponse,
)
async def ask_question(
    request: Request,
    question_request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: CurrentUser = Depends(get_current_active_user),
    _permission: CurrentUser = Depends(require_permission(Permission.CHAT_ASK)),
):
    """
    Ask a question about the uploaded legal documents.
    Supports traditional request-response for stable clients.
    """

    try:
        answer_data = await rag_service.answer_question(
            question=question_request.question,
            k=question_request.k,
        )

        audit_service.log(
            AuditEventType.AI_QUERY,
            action="rag_ask",
            status="success",
            user_id=current_user.user_id,
            username=current_user.username,
            details={
                "question_len": len(question_request.question),
                "grounding_score": answer_data.get("grounding_score"),
                "evidence_count": len(answer_data.get("evidence", [])),
            },
        )

        return AnswerResponse(**answer_data)

    except Exception as e:
        audit_service.log(
            AuditEventType.AI_QUERY,
            action="rag_ask",
            status="failure",
            user_id=current_user.user_id,
            details={"reason": "internal_error", "error": str(e)},
        )
        logger.error(f"RAG error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        ) from e

@router.post("/stream", summary="Streamed RAG response (10.3.7)")
async def stream_question(
    question_request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service),
    current_user: CurrentUser = Depends(get_current_active_user),
    _permission: CurrentUser = Depends(require_permission(Permission.CHAT_ASK)),
):
    """
    Streamed version of the RAG endpoint for faster TTFB.
    Returns chunks of the answer as they are generated.
    """

    async def event_generator():
        try:
            async for chunk in rag_service.stream_answer(
                question=question_request.question,
                k=question_request.k
            ):
                # Standard SSE format
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
