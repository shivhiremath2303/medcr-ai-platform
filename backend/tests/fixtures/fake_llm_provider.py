from typing import AsyncGenerator

from app.domain.repositories.llm_provider import LLMProvider


class FakeLLMProvider(LLMProvider):
    def __init__(self, answer: str = "Fake answer"):
        self.answer = answer
        self.received_questions = []
        self.received_contexts = []

    async def generate_answer(self, question: str, context: str) -> str:
        self.received_questions.append(question)
        self.received_contexts.append(context)
        return self.answer

    async def rewrite_question(self, question: str, conversation_context: str) -> str:
        return question

    async def stream_answer(
        self, question: str, context: str
    ) -> AsyncGenerator[str, None]:
        yield self.answer
