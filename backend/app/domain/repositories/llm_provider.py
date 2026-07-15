from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class LLMProvider(ABC):
    """
    Enterprise Interface for Large Language Model interactions.
    Updated to support Model Routing and Complexity hints (10.5.4).
    """

    @abstractmethod
    async def generate_answer(
        self,
        question: str,
        context: str,
        complexity_hint: str | None = None,
    ) -> str:
        """
        Generate a full answer using the provided context.
        complexity_hint can be used for dynamic model routing (10.5.4).
        """

    @abstractmethod
    def stream_answer(
        self,
        question: str,
        context: str,
        complexity_hint: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream an answer using the provided context.
        """

    @abstractmethod
    async def rewrite_question(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """
        Rewrite a follow-up question into a standalone question.
        """
