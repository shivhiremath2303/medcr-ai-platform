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
        if retrieval_service is None:
            from app.di import get_retrieval_service

            self.retrieval_service = get_retrieval_service()
        else:
            self.retrieval_service = retrieval_service

        if context_builder is None:
            from app.di import get_context_builder

            self.context_builder = get_context_builder()
        else:
            self.context_builder = context_builder

        if llm_service is None:
            from app.di import get_llm_service

            self.llm_service = get_llm_service()
        else:
            self.llm_service = llm_service

        if memory is None:
            from app.di import get_conversation_memory

            self.memory = get_conversation_memory()
        else:
            self.memory = memory

        if query_rewriter is not None:
            self.query_rewriter = query_rewriter
        else:
            from app.di import get_query_rewriter

            self.query_rewriter = get_query_rewriter()

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
