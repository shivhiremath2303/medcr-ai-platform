from abc import ABC, abstractmethod


class QueryRewriter(ABC):
    """
    Interface for rewriting questions based on conversation context.
    """

    @abstractmethod
    def rewrite(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """
        Rewrite the user's question into a standalone question.
        """
