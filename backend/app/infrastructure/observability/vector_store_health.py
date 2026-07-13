from typing import Any, Dict

from app.core.observability.health import HealthCheck
from app.domain.repositories.vector_store_repository import VectorStoreRepository


class VectorStoreHealthCheck(HealthCheck):
    """
    Enterprise Health check for the FAISS Vector Store.
    Integrated with scaling and lazy loading (10.3.4).
    """

    def __init__(self, vector_store: VectorStoreRepository):
        self.vector_store = vector_store

    @property
    def name(self) -> str:
        return "vector_store"

    @property
    def critical(self) -> bool:
        return True

    async def check(self) -> Dict[str, Any]:
        try:
            # 1. Check readiness (10.3.4)
            if not self.vector_store.is_ready:
                # Attempt background load if not yet ready
                # In a real system, this might be handled by a background task
                return {
                    "status": "up",
                    "chunk_count": 0,
                    "info": "Vector store warming up / loading",
                }

            # 2. Detailed count check (Async)
            chunks = await self.vector_store.get_all_chunks()
            chunks_count = len(chunks)

            return {"status": "up", "chunk_count": chunks_count, "ready": True}
        except Exception as e:
            return {"status": "down", "error": str(e)}
