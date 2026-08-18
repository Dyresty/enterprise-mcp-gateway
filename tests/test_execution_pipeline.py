from app.mcp import server


def test_execute_tool_runs_successfully(monkeypatch):
    server.AUTH_CONTEXT = (
        server.create_authentication_context("analyst")
    )

    tool = {
        "name": "test.tool",
        "required_role": "analyst",
        "timeout_seconds": 2,
        "max_retries": 0,
        "retry_backoff_seconds": 0,
        "rate_limit_per_minute": 30,
        "cache_enabled": False,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    result = server.execute_tool(
        tool_name="test.tool",
        arguments={},
        execute_function=lambda: "success",
    )

    assert result == "success"


def test_execute_tool_retries_failed_execution(monkeypatch):
    server.AUTH_CONTEXT = (
        server.create_authentication_context("analyst")
    )

    tool = {
        "name": "test.tool",
        "required_role": "analyst",
        "timeout_seconds": 2,
        "max_retries": 2,
        "retry_backoff_seconds": 0,
        "rate_limit_per_minute": 30,
        "cache_enabled": False,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    calls = []

    def failing_then_success():
        calls.append(1)

        if len(calls) < 3:
            raise RuntimeError("temporary failure")

        return "success"

    result = server.execute_tool(
        tool_name="test.tool",
        arguments={},
        execute_function=failing_then_success,
    )

    assert result == "success"
    assert len(calls) == 3


def test_execute_tool_does_not_cache_write_tool(monkeypatch):
    server.AUTH_CONTEXT = (
        server.create_authentication_context("developer")
    )

    tool = {
        "name": "test.write",
        "required_role": "developer",
        "timeout_seconds": 2,
        "max_retries": 0,
        "retry_backoff_seconds": 0,
        "rate_limit_per_minute": 30,
        "cache_enabled": False,
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

    result = server.execute_tool(
        tool_name="test.write",
        arguments={"value": "test"},
        execute_function=lambda: "created",
    )

    assert result == "created"
    assert cache_calls == []


def test_execute_tool_uses_cache(monkeypatch):
    server.AUTH_CONTEXT = (
        server.create_authentication_context("analyst")
    )

    tool = {
        "name": "test.cached",
        "required_role": "analyst",
        "timeout_seconds": 2,
        "max_retries": 0,
        "retry_backoff_seconds": 0,
        "rate_limit_per_minute": 30,
        "cache_enabled": True,
        "cache_ttl_seconds": 60,
    }

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: tool,
    )

    calls = []

    class FakeCache:
        def __init__(self):
            self.data = {}

        def get(self, key):
            return self.data.get(key)

        def set(self, key, value, ttl_seconds):
            self.data[key] = value

    fake_cache = FakeCache()

    monkeypatch.setattr(
        server,
        "cache",
        fake_cache,
    )

    def execute():
        calls.append(1)
        return {"result": "cached"}

    first_result = server.execute_tool(
        tool_name="test.cached",
        arguments={"id": 1},
        execute_function=execute,
    )

    second_result = server.execute_tool(
        tool_name="test.cached",
        arguments={"id": 1},
        execute_function=execute,
    )

    assert first_result == second_result
    assert len(calls) == 1