import time
from typing import Callable, TypeVar


T = TypeVar("T")


class RetryExhausted(Exception):
    """Raised when all retry attempts have failed."""


class RetryExecutor:
    def execute(
        self,
        function: Callable[[], T],
        max_retries: int = 0,
        backoff_seconds: float = 0.5,
    ) -> T:
        if max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to zero")

        if backoff_seconds < 0:
            raise ValueError("backoff_seconds must be greater than or equal to zero")

        attempts = 0

        while True:
            try:
                return function()

            except Exception:
                if attempts >= max_retries:
                    raise

                attempts += 1

                if backoff_seconds > 0:
                    time.sleep(backoff_seconds * (2 ** (attempts - 1)))