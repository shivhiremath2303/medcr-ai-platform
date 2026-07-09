from app.services.llm.llm_service import LLMService
from app.services.rag.conversation_memory import ConversationMemory
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.query_rewriter import QueryRewriter
from app.services.retrieval.retrieval_service import RetrievalService


class RAGService:
    """
    Coordinates the Retrieval-Augmented Generation workflow.
    """

    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.context_builder = ContextBuilder()
        self.llm_service = LLMService()
        self.memory = ConversationMemory()
        self.query_rewriter = QueryRewriter()

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
