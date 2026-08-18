import json
from typing import Any

from app.redis import get_redis


class RedisCache:

    def __init__(self):
        self.redis = get_redis()

    def get(self, key: str) -> Any | None:
        value = self.redis.get(key)

        if value is None:
            return None

        return json.loads(value)

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int,
    ) -> None:
        self.redis.set(
            key,
            json.dumps(value),
            ex=ttl_seconds,
        )

    def delete(self, key: str) -> None:
        self.redis.delete(key)

    def exists(self, key: str) -> bool:
        return bool(self.redis.exists(key))