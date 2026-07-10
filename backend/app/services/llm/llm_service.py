from google import genai

from app.core.config import settings
from app.prompts.legal_prompt import LEGAL_RAG_PROMPT


class LLMService:
    """
    Handles interactions with the Large Language Model.

    NOTE: Per DI rules the genai.Client must be injected by the composition root.
    """

    MODEL_NAME = "gemini-2.5-pro"

    def __init__(self, client: genai.Client):
        """
        Require an injected genai.Client. Do NOT create clients inside services.
        """
        if client is None:
            raise ValueError("genai.Client must be provided via dependency injection")
        self.client = client

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Generate an answer using the retrieved context.
        """

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
        """
        Rewrite a follow-up question into a standalone question.
        """

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
            # If rewriting fails, continue with the original question.
            return question
