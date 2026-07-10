from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Interface for Large Language Model interactions.
    """

    @abstractmethod
    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Generate an answer using the provided context.
        """

    @abstractmethod
    def rewrite_question(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """
        Rewrite a follow-up question into a standalone question.
        """
