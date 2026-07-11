from app.core.observability.logger import get_logger
from app.domain.repositories import RevocationRepository
from app.core.config.base import Settings

logger = get_logger(__name__)

class CleanupService:
    """
    Service for periodic maintenance tasks.
    """
    def __init__(self, settings: Settings, revocation_repository: RevocationRepository):
        self.settings = settings
        self.revocation_repository = revocation_repository

    async def run_cleanup(self) -> None:
        """
        Execute all registered cleanup tasks.
        """
        logger.info("Starting background maintenance cleanup...")

        try:
            # Note: For Redis implementations, TTL handles cleanup automatically.
            # This is primarily for in-memory or custom file-based fallbacks.
            if hasattr(self.revocation_repository, "cleanup_expired"):
                self.revocation_repository.cleanup_expired()
                logger.info("Token revocation cleanup completed.")

            # Future: Temporary file cleanup
            # Future: Expired conversation cleanup if not using Redis TTL

        except Exception as e:
            logger.error(f"Maintenance cleanup failed: {e}")

        logger.info("Background maintenance cleanup finished.")
