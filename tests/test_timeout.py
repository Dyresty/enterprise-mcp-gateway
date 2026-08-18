import time

import pytest

from app.mcp import server


def test_execute_with_timeout_success():
    tool = {
        "name": "test.tool",
        "timeout_seconds": 2,
    }

    result = server.execute_with_timeout(
        tool,
        lambda: "success",
    )

    assert result == "success"


def test_execute_with_timeout_fails_when_tool_takes_too_long():
    tool = {
        "name": "test.tool",
        "timeout_seconds": 1,
    }

    def slow_function():
        time.sleep(2)
        return "too late"

    with pytest.raises(
        TimeoutError,
        match="timed out after 1 seconds",
    ):
        server.execute_with_timeout(
            tool,
            slow_function,
        )