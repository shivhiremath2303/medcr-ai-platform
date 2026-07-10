from app.services.llm.llm_service import LLMService


class QueryRewriter:
    """
    Rewrites follow-up questions into standalone questions.
    """

    def __init__(self, llm_service: LLMService | None = None):
        if llm_service is None:
            from app.di import get_llm_service

            self.llm_service = get_llm_service()
        else:
            self.llm_service = llm_service

    def rewrite(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """
        Rewrite the user's question into a standalone question.

        Disabled during development to avoid an extra LLM call.
        """

    # Development mode:
    # return the original question directly.
        return question

    # Production:
    # return self.llm_service.rewrite_question(
    #     question=question,
    #     conversation_context=conversation_context,
    # )
