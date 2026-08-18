import pytest

from app.rate_limit.limiter import RateLimiter, RateLimitExceeded


class FakeRedis:

    def __init__(self):
        self.data = {}
        self.expirations = {}

    def incr(self, key):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    def expire(self, key, seconds):
        self.expirations[key] = seconds


def test_first_request_is_allowed(monkeypatch):
    limiter = RateLimiter()
    fake_redis = FakeRedis()

    limiter.redis = fake_redis

    assert limiter.check(
        user="analyst",
        tool_name="github.get_issue",
        limit=3,
    ) is True


def test_requests_within_limit_are_allowed(monkeypatch):
    limiter = RateLimiter()
    fake_redis = FakeRedis()

    limiter.redis = fake_redis

    for _ in range(3):
        assert limiter.check(
            user="analyst",
            tool_name="github.get_issue",
            limit=3,
        ) is True


def test_request_over_limit_is_rejected():
    limiter = RateLimiter()
    fake_redis = FakeRedis()

    limiter.redis = fake_redis

    for _ in range(3):
        limiter.check(
            user="analyst",
            tool_name="github.get_issue",
            limit=3,
        )

    with pytest.raises(
        RateLimitExceeded,
        match="Rate limit exceeded",
    ):
        limiter.check(
            user="analyst",
            tool_name="github.get_issue",
            limit=3,
        )


def test_different_users_have_independent_limits():
    limiter = RateLimiter()
    fake_redis = FakeRedis()

    limiter.redis = fake_redis

    for _ in range(2):
        limiter.check(
            user="analyst",
            tool_name="github.get_issue",
            limit=2,
        )

    assert limiter.check(
        user="developer",
        tool_name="github.get_issue",
        limit=2,
    ) is True


def test_different_tools_have_independent_limits():
    limiter = RateLimiter()
    fake_redis = FakeRedis()

    limiter.redis = fake_redis

    for _ in range(2):
        limiter.check(
            user="analyst",
            tool_name="github.get_issue",
            limit=2,
        )

    assert limiter.check(
        user="analyst",
        tool_name="github.create_issue",
        limit=2,
    ) is True


def test_rate_limit_sets_expiration():
    limiter = RateLimiter()
    fake_redis = FakeRedis()

    limiter.redis = fake_redis

    limiter.check(
        user="analyst",
        tool_name="github.get_issue",
        limit=3,
    )

    assert len(fake_redis.expirations) == 1
    assert list(fake_redis.expirations.values())[0] == 60


def test_invalid_rate_limit_is_rejected():
    limiter = RateLimiter()
    fake_redis = FakeRedis()

    limiter.redis = fake_redis

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        limiter.check(
            user="analyst",
            tool_name="github.get_issue",
            limit=0,
        )