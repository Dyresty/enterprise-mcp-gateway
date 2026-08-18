from app.cache.redis_cache import RedisCache


def test_redis_cache_set_and_get():
    cache = RedisCache()

    key = "test:redis-cache"
    value = {
        "message": "hello",
        "number": 123,
    }

    cache.set(
        key=key,
        value=value,
        ttl_seconds=60,
    )

    result = cache.get(key)

    assert result == value

    cache.delete(key)


def test_redis_cache_missing_key():
    cache = RedisCache()

    result = cache.get("test:missing-key")

    assert result is None


def test_redis_cache_exists():
    cache = RedisCache()

    key = "test:redis-exists"

    cache.set(
        key=key,
        value={"status": "ok"},
        ttl_seconds=60,
    )

    assert cache.exists(key) is True

    cache.delete(key)

    assert cache.exists(key) is False