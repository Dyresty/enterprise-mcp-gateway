import time

from app.redis import get_redis


class RateLimitExceeded(Exception):
    """Raised when a tool's rate limit has been exceeded."""


class RateLimiter:

    def __init__(self):
        self.redis = get_redis()

    def check(
        self,
        user: str,
        tool_name: str,
        limit: int,
    ) -> bool:
        """
        Check whether a user is allowed to execute a tool.

        Returns True when the request is allowed.
        Raises RateLimitExceeded when the limit is exceeded.
        """

        if limit <= 0:
            raise ValueError("Rate limit must be greater than zero.")

        window = int(time.time() // 60)

        key = f"rate_limit:{user}:{tool_name}:{window}"

        count = self.redis.incr(key)

        if count == 1:
            self.redis.expire(key, 60)

        if count > limit:
            raise RateLimitExceeded(
                f"Rate limit exceeded for tool '{tool_name}'. "
                f"Maximum {limit} requests per minute."
            )

        return True