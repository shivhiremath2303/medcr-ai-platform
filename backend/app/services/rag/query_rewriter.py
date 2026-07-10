from app.domain.repositories.llm_provider import LLMProvider


class QueryRewriter:
    """
    Rewrites follow-up questions into standalone questions.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def rewrite(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """
        Rewrite the user's question into a standalone question.

        Note: Currently returns the original question to avoid extra LLM calls
        during development, but can be switched to production mode.
        """
        # Production mode:
        # return self.llm_provider.rewrite_question(
        #     question=question,
        #     conversation_context=conversation_context,
        # )

        # Development mode:
        return question
