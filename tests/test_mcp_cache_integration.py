from app.mcp import server


def test_cached_tool_uses_cache_after_first_execution(monkeypatch):
    server.AUTH_CONTEXT = server.create_authentication_context("analyst")

    tool = {
        "name": "github.get_repository",
        "required_role": "analyst",
        "cache_enabled": True,
        "cache_ttl_seconds": 60,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    calls = []

    def fake_get_repository(owner, repo):
        calls.append((owner, repo))

        return {
            "name": repo,
            "owner": owner,
        }

    monkeypatch.setattr(
        server,
        "get_repository",
        fake_get_repository,
    )

    cache_data = {}

    class FakeCache:
        def get(self, key):
            return cache_data.get(key)

        def set(self, key, value, ttl_seconds):
            cache_data[key] = value

    monkeypatch.setattr(
        server,
        "cache",
        FakeCache(),
    )

    arguments = {
        "owner": "Dyresty",
        "repo": "enterprise-mcp-gateway",
    }

    first_result = server.execute_with_cache(
        tool_name="github.get_repository",
        arguments=arguments,
        execute_function=lambda: server.get_repository(
            owner="Dyresty",
            repo="enterprise-mcp-gateway",
        ),
    )

    second_result = server.execute_with_cache(
        tool_name="github.get_repository",
        arguments=arguments,
        execute_function=lambda: server.get_repository(
            owner="Dyresty",
            repo="enterprise-mcp-gateway",
        ),
    )

    assert first_result == second_result

    assert calls == [
        ("Dyresty", "enterprise-mcp-gateway"),
    ]