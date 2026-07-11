from fastapi import HTTPException, Request, status, Depends
from app.domain.repositories.rate_limiter import RateLimiter
from app.di import get_rate_limiter, get_settings_provider

class RateLimit:
    """
    Dependency for applying rate limits to routes.
    """
    def __init__(self, limit: int = None, window: int = None, key_prefix: str = "gen"):
        self.limit = limit
        self.window = window
        self.key_prefix = key_prefix

    async def __call__(
        self,
        request: Request,
        rate_limiter: RateLimiter = Depends(get_rate_limiter),
        settings = Depends(get_settings_provider)
    ):
        if not settings.rate_limit_enabled:
            return

        # Default to settings if not provided in decorator
        limit = self.limit or settings.rate_limit_general_requests
        window = self.window or settings.rate_limit_window_seconds

        # Use IP or user_id as key
        user_id = getattr(request.state, "user_id", request.client.host)
        key = f"{self.key_prefix}:{user_id}"

        if await rate_limiter.is_rate_limited(key, limit, window):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
