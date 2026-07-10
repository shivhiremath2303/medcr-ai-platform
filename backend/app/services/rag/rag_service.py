from app.domain.repositories.llm_provider import LLMProvider
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.retriever import Retriever
from app.domain.repositories.query_rewriter import QueryRewriter
from app.domain.repositories.context_builder import ContextBuilder


class RAGService:
    """
    Coordinates the Retrieval-Augmented Generation workflow.
    """

    def __init__(
        self,
        retrieval_service: Retriever,
        llm_provider: LLMProvider,
        query_rewriter: QueryRewriter,
        memory: ConversationRepository,
        context_builder: ContextBuilder,
    ):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.query_rewriter = query_rewriter
        self.memory = memory
        self.context_builder = context_builder

    def answer_question(
        self,
        question: str,
        k: int = 3,
    ) -> dict:
        """
        Retrieve context, generate an answer and return its sources.
        """

        # Store the user's question
        self.memory.add_user_message(question)

        # Get conversation history
        memory_context = self.memory.get_context()

        # Rewrite the question
        retrieval_query = self.query_rewriter.rewrite(
            question=question,
            conversation_context=memory_context,
        )

        # Retrieve relevant chunks
        results = self.retrieval_service.retrieve(
            query=retrieval_query,
            k=k,
        )

        # Build LLM context
        context = self.context_builder.build(results)

        # Generate answer
        answer = self.llm_provider.generate_answer(
            question=question,
            context=context,
        )

        # Store assistant response
        self.memory.add_assistant_message(answer)

        # Build source list
        sources = [
            {
                "filename": result.chunk.metadata.filename,
                "page_number": result.chunk.metadata.page_number,
            }
            for result in results
        ]

        return {
            "answer": answer,
            "sources": sources,
        }
