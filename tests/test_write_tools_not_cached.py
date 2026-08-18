from app.mcp import server


def test_write_tool_does_not_use_cache(monkeypatch):
    server.AUTH_CONTEXT = server.create_authentication_context("developer")

    tool = {
        "name": "github.create_issue",
        "required_role": "developer",
        "cache_enabled": False,
        "cache_ttl_seconds": 60,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    cache_calls = []

    class FakeCache:
        def get(self, key):
            cache_calls.append(("get", key))
            return None

        def set(self, key, value, ttl_seconds):
            cache_calls.append(("set", key))
            
    monkeypatch.setattr(
        server,
        "cache",
        FakeCache(),
    )

    result = server.execute_with_cache(
        tool_name="github.create_issue",
        arguments={
            "owner": "Dyresty",
            "repo": "enterprise-mcp-gateway",
            "title": "Test issue",
        },
        execute_function=lambda: {
            "number": 1,
            "title": "Test issue",
        },
    )

    assert result == {
        "number": 1,
        "title": "Test issue",
    }

    assert cache_calls == []