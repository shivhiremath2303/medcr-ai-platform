from abc import ABC, abstractmethod
from app.domain.models.retrieval import QueryUnderstanding

class QueryRewriter(ABC):
    """
    Enterprise Interface for query rewriting.
    Updated to support async horizontal scaling (10.3.3).
    """

    @abstractmethod
    async def rewrite(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        """
        Rewrite the user's question into a standalone question.
        """

    @abstractmethod
    async def understand_query(
        self,
        question: str,
        conversation_context: str,
    ) -> QueryUnderstanding:
        """
        Perform deep legal understanding and expansion of the query.
        """
