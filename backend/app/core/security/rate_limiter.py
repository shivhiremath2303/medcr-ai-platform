from typing import Optional, Tuple

from app.core.config.base import Settings
from app.core.observability.logger import get_logger
from app.domain.models.audit import AuditEventType
from app.domain.repositories.rate_limiter import RateLimiter
from app.services.audit.audit_service import AuditService

logger = get_logger(__name__)


class RateLimiterService:
    """
    Enterprise API protection service.
    Implements multi-tiered rate limiting (Global, Tenant, IP, User).
    """

    def __init__(
        self, limiter: RateLimiter, settings: Settings, audit_service: AuditService
    ):
        self._limiter = limiter
        self._settings = settings
        self._audit_service = audit_service

    async def check_all(
        self,
        ip_address: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
        path: str = "/",
        method: str = "GET",
    ) -> bool:
        """
        Perform a tiered rate limit check.
        Returns True if all checks pass, False if any tier is limited.
        """
        if not self._settings.rate_limit_enabled:
            return True

        # 1. Global Rate Limit (System-wide circuit breaker)
        if await self._is_limited(
            "global",
            self._settings.rate_limit_global_requests,
            self._settings.rate_limit_window_seconds,
            "system",
        ):
            return False

        # 2. IP-based Rate Limit (Prevent scraping/DDoS)
        if await self._is_limited(
            f"ip:{ip_address}",
            self._settings.rate_limit_per_ip_requests,
            self._settings.rate_limit_window_seconds,
            ip_address,
        ):
            return False

        # 3. Tenant-based Rate Limit (SaaS fairness)
        if tenant_id:
            if await self._is_limited(
                f"tenant:{tenant_id}",
                self._settings.rate_limit_per_tenant_requests,
                self._settings.rate_limit_window_seconds,
                tenant_id,
            ):
                return False

        # 4. Endpoint-specific User/Identifier Limit
        limit, window = self._get_limit_for_endpoint(path, method)
        identifier = user_id or ip_address
        if await self._is_limited(
            f"endpoint:{path}:{identifier}",
            limit,
            window,
            identifier,
        ):
            return False

        return True

    async def _is_limited(
        self, key: str, limit: int, window: int, identifier: str
    ) -> bool:
        """Helper to check a specific limit and audit failures."""
        is_limited = await self._limiter.is_rate_limited(key, limit, window)
        if is_limited:
            logger.warning(f"Rate limit exceeded for {key}")
            self._audit_service.log(
                event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
                action="api_throttle",
                status="failure",
                details={
                    "limit_key": key,
                    "limit_value": limit,
                    "window": window,
                    "identifier": identifier,
                },
            )
            return True
        return False

    def _get_limit_for_endpoint(self, path: str, method: str) -> Tuple[int, int]:
        """Get rate limit and window for a specific endpoint."""
        path = path.lower()

        if path.startswith("/auth/"):
            return (
                self._settings.rate_limit_auth_requests,
                self._settings.rate_limit_window_seconds,
            )
        elif path.startswith("/documents/upload"):
            return (
                self._settings.rate_limit_upload_requests,
                self._settings.rate_limit_window_seconds,
            )
        elif path.startswith("/rag/"):
            return (
                self._settings.rate_limit_rag_requests,
                self._settings.rate_limit_window_seconds,
            )
        else:
            return (
                self._settings.rate_limit_general_requests,
                self._settings.rate_limit_window_seconds,
            )
