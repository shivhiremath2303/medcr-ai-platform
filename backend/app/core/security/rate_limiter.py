from typing import Tuple
from app.core.config.base import Settings
from app.domain.repositories.rate_limiter import RateLimiter
from app.core.observability.logger import get_logger

logger = get_logger(__name__)

class RateLimiterService:
    """
    High-level rate limiter service.
    Endpoint-specific limiting logic.
    """

    def __init__(self, limiter: RateLimiter, settings: Settings):
        self._limiter = limiter
        self._settings = settings

    async def check(
        self,
        identifier: str,
        path: str,
        method: str = "GET"
    ) -> bool:
        """
        Check rate limit for a request.
        Returns True if allowed, False if limited.
        """
        if not self._settings.rate_limit_enabled:
            return True

        limit, window = self._get_limit_for_endpoint(path, method)
        key = f"{identifier}:{path}:{method}"

        is_limited = await self._limiter.is_rate_limited(key, limit, window)

        if is_limited:
            logger.warning(
                f"Rate limit exceeded: identifier={identifier}, path={path}, "
                f"method={method}, limit={limit}, window={window}s"
            )

        return not is_limited

    def _get_limit_for_endpoint(self, path: str, method: str) -> Tuple[int, int]:
        """Get rate limit and window for a specific endpoint."""
        path = path.lower()

        if path.startswith("/auth/"):
            return self._settings.rate_limit_auth_requests, self._settings.rate_limit_window_seconds
        elif path.startswith("/documents/upload") or path.startswith("/documents/"):
            return self._settings.rate_limit_upload_requests, self._settings.rate_limit_window_seconds
        elif path.startswith("/rag/"):
            return self._settings.rate_limit_rag_requests, self._settings.rate_limit_window_seconds
        else:
            return self._settings.rate_limit_general_requests, self._settings.rate_limit_window_seconds
