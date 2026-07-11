from typing import Dict, Any
from app.core.observability.health import HealthCheck
from app.domain.repositories.vector_store_repository import VectorStoreRepository

class VectorStoreHealthCheck(HealthCheck):
    def __init__(self, vector_store: VectorStoreRepository):
        self.vector_store = vector_store

    @property
    def name(self) -> str:
        return "vector_store"

    async def check(self) -> Dict[str, Any]:
        try:
            # Simple check to see if vector store is loaded and has chunks
            # In a real scenario, this might perform a simple heartbeat search
            chunks = self.vector_store.get_all_chunks()
            return {
                "status": "up",
                "chunk_count": len(chunks)
            }
        except Exception as e:
            return {
                "status": "down",
                "error": str(e)
            }
