from google import genai
from app.domain.repositories.llm_provider import LLMProvider


class GeminiLLMAdapter(LLMProvider):
    """
    Adapter for Google Gemini AI.
    """

    def __init__(
        self,
        client: genai.Client,
        model_name: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ):
        """
        Accept an injected genai.Client and configuration.
        """
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

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
            # Note: The new genai SDK might use a different config structure.
            # We'll stick to what was working or adjust as per actual library usage if needed.
            # Assuming GenerateContentConfig is needed for temperature/max_tokens if available.

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
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
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.0, # Usually better for rewriting
                }
            )

            return response.text.strip()

        except Exception:
            return question
