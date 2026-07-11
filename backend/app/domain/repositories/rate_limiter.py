from abc import ABC, abstractmethod


class RateLimiter(ABC):
    """
    Interface for rate limiting operations.
    """

    @abstractmethod
    async def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        """
        Check if a given key has exceeded the rate limit.

        Args:
            key: Unique identifier (e.g., IP, user_id).
            limit: Maximum number of requests allowed.
            window: Time window in seconds.
        """
