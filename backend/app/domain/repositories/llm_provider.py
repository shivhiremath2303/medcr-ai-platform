from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class LLMProvider(ABC):
    """
    Enterprise Interface for Large Language Model interactions.
    Updated to support async horizontal scaling and streaming (10.3.7).
    """

    @abstractmethod
    async def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Generate a full answer using the provided context.
        """

    @abstractmethod
    async def stream_answer(
        self,
        question: str,
        context: str,
    ) -> AsyncGenerator[str, None]:
        """
        Stream an answer using the provided context (10.3.7).
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
