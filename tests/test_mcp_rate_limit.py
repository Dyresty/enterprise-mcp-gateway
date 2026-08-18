import pytest

from app.auth.authentication import create_authentication_context
from app.mcp import server
from app.rate_limit.limiter import RateLimitExceeded


def test_mcp_allows_request_within_rate_limit(monkeypatch):
    server.AUTH_CONTEXT = create_authentication_context("analyst")

    tool = {
        "name": "github.get_issue",
        "required_role": "analyst",
        "rate_limit_per_minute": 2,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    calls = []

    class FakeRateLimiter:
        def check(self, user, tool_name, limit):
            calls.append((user, tool_name, limit))
            return True

    monkeypatch.setattr(
        server,
        "rate_limiter",
        FakeRateLimiter(),
    )

    result = server.get_authorized_tool("github.get_issue")

    assert result["name"] == "github.get_issue"
    assert calls == [
        ("analyst", "github.get_issue", 2)
    ]


def test_mcp_rejects_request_when_rate_limit_is_exceeded(monkeypatch):
    server.AUTH_CONTEXT = create_authentication_context("analyst")

    tool = {
        "name": "github.get_issue",
        "required_role": "analyst",
        "rate_limit_per_minute": 2,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    class FakeRateLimiter:
        def check(self, user, tool_name, limit):
            raise RateLimitExceeded(
                "Rate limit exceeded for tool 'github.get_issue'. "
                "Maximum 2 requests per minute."
            )

    monkeypatch.setattr(
        server,
        "rate_limiter",
        FakeRateLimiter(),
    )

    with pytest.raises(
        ValueError,
        match="Rate limit exceeded",
    ):
        server.get_authorized_tool("github.get_issue")


def test_mcp_uses_tool_rate_limit_configuration(monkeypatch):
    server.AUTH_CONTEXT = create_authentication_context("developer")

    tool = {
        "name": "github.create_issue",
        "required_role": "developer",
        "rate_limit_per_minute": 5,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    received = {}

    class FakeRateLimiter:
        def check(self, user, tool_name, limit):
            received["user"] = user
            received["tool_name"] = tool_name
            received["limit"] = limit
            return True

    monkeypatch.setattr(
        server,
        "rate_limiter",
        FakeRateLimiter(),
    )

    server.get_authorized_tool("github.create_issue")

    assert received == {
        "user": "developer",
        "tool_name": "github.create_issue",
        "limit": 5,
    }


def test_different_users_use_their_own_rate_limit_identity(monkeypatch):
    tool = {
        "name": "github.get_issue",
        "required_role": "analyst",
        "rate_limit_per_minute": 10,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    users = []

    class FakeRateLimiter:
        def check(self, user, tool_name, limit):
            users.append(user)
            return True

    monkeypatch.setattr(
        server,
        "rate_limiter",
        FakeRateLimiter(),
    )

    server.AUTH_CONTEXT = create_authentication_context("analyst")
    server.get_authorized_tool("github.get_issue")

    server.AUTH_CONTEXT = create_authentication_context("developer")

    # Developer cannot execute this analyst-only tool, so use
    # an appropriate tool for the second identity.
    developer_tool = {
        "name": "github.create_issue",
        "required_role": "developer",
        "rate_limit_per_minute": 10,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: developer_tool,
    )

    server.get_authorized_tool("github.create_issue")

    assert users == ["analyst", "developer"]