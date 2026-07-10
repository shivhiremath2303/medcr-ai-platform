from app.services.llm.llm_service import LLMService
from app.services.rag.conversation_memory import ConversationMemory
from app.services.retrieval.context_builder import ContextBuilder
from app.services.rag.query_rewriter import QueryRewriter
from app.services.retrieval.retrieval_service import RetrievalService


class RAGService:
    """
    Coordinates the Retrieval-Augmented Generation workflow.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        context_builder: ContextBuilder | None = None,
        llm_service: LLMService | None = None,
        memory: ConversationMemory | None = None,
        query_rewriter: QueryRewriter | None = None,
    ):
        # Allow constructor injection for all collaborators. Backwards-compatible
        # defaults create the original components when not provided (useful for
        # tests that directly instantiate RAGService).
        self.retrieval_service = retrieval_service if retrieval_service is not None else RetrievalService()
        self.context_builder = context_builder if context_builder is not None else ContextBuilder()
        self.llm_service = llm_service if llm_service is not None else LLMService()
        self.memory = memory if memory is not None else ConversationMemory()
        # Ensure QueryRewriter uses the same LLMService instance to avoid
        # creating multiple genai.Client instances.
        if query_rewriter is not None:
            self.query_rewriter = query_rewriter
        else:
            self.query_rewriter = QueryRewriter(llm_service=self.llm_service)

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

        # Rewrite the question (currently returns the original question)
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
        answer = self.llm_service.generate_answer(
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
