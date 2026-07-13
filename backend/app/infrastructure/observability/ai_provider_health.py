import time
from typing import Any, Dict

from google import genai
from app.core.observability.health import HealthCheck


class AIProviderHealthCheck(HealthCheck):
    """
    Health check for Google Gemini AI Provider.
    """

    def __init__(self, client: genai.Client, model_name: str):
        self.client = client
        self.model_name = model_name

    @property
    def name(self) -> str:
        return "ai_provider_gemini"

    @property
    def critical(self) -> bool:
        # Service can still function (e.g., retrieval) even if LLM is temporarily down
        return False

    async def check(self) -> Dict[str, Any]:
        start_time = time.perf_counter()
        try:
            # Simple metadata check to verify API key and connectivity
            # Using models.get to check if the configured model is available
            self.client.models.get(model=self.model_name)

            latency = (time.perf_counter() - start_time) * 1000
            return {
                "status": "up",
                "model": self.model_name,
                "latency_ms": round(latency, 2)
            }
        except Exception as e:
            return {
                "status": "down",
                "error": str(e),
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2)
            }
