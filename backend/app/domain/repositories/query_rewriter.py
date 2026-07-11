from abc import ABC, abstractmethod
from app.domain.models.retrieval import QueryUnderstanding


class QueryRewriter(ABC):
    """
    Interface for rewriting and understanding questions based on conversation context.
    """

    @abstractmethod
    def rewrite(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """
        Legacy: Rewrite the user's question into a standalone question.
        """

    @abstractmethod
    def understand_query(
        self,
        question: str,
        conversation_context: str,
    ) -> QueryUnderstanding:
        """
        Perform deep legal understanding and expansion of the query.
        """
