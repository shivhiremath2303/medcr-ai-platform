from app.domain.repositories.rate_limiter import RateLimiter


class NoOpRateLimiter(RateLimiter):
    """
    Rate limiter implementation that always allows requests.
    """

    async def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        return False
