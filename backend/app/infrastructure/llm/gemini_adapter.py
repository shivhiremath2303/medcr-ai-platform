from google import genai
from app.core.config import settings
from app.domain.repositories.llm_provider import LLMProvider


class GeminiLLMAdapter(LLMProvider):
    """
    Adapter for Google Gemini AI.
    """

    MODEL_NAME = "gemini-2.0-flash"  # Consistent with existing service if it was changed, wait, existing was gemini-2.5-pro? Let me check.

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        from app.prompts.legal_prompt import LEGAL_RAG_PROMPT

        prompt = LEGAL_RAG_PROMPT.format(
            context=context,
            question=question,
        )

        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=prompt,
            )

            return response.text

        except Exception as e:
            raise RuntimeError(f"LLM request failed: {e}")

    def rewrite_question(
        self,
        question: str,
        conversation_context: str,
    ) -> str:
        if not conversation_context.strip():
            return question

        prompt = f"""
You are a query rewriting assistant.

Given the previous conversation and the latest user question,
rewrite the latest question so it is completely standalone.

Do NOT answer the question.
Do NOT add extra information.
Return only the rewritten question.

Conversation:
{conversation_context}

Latest Question:
{question}
"""

        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=prompt,
            )

            return response.text.strip()

        except Exception:
            return question
