import pytest

from app.auth.authentication import create_authentication_context
from app.auth import authentication
from app.mcp import server


def make_tool(name: str, required_role: str) -> dict:
    return {
        "name": name,
        "required_role": required_role,
    }


def test_analyst_cannot_execute_developer_tool(monkeypatch):
    server.AUTH_CONTEXT = create_authentication_context("analyst")

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: make_tool(name, "developer"),
    )

    with pytest.raises(
        ValueError,
        match="not authorized",
    ):
        server.get_authorized_tool("github.create_issue")


def test_developer_can_execute_developer_tool(monkeypatch):
    server.AUTH_CONTEXT = create_authentication_context("developer")

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: make_tool(name, "developer"),
    )

    tool = server.get_authorized_tool("github.create_issue")

    assert tool["name"] == "github.create_issue"
    assert tool["required_role"] == "developer"


def test_analyst_can_execute_read_tool(monkeypatch):
    server.AUTH_CONTEXT = create_authentication_context("analyst")

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: make_tool(name, "analyst"),
    )

    tool = server.get_authorized_tool("github.get_issue")

    assert tool["name"] == "github.get_issue"
    assert tool["required_role"] == "analyst"


def test_unknown_tool_is_rejected(monkeypatch):
    server.AUTH_CONTEXT = create_authentication_context("developer")

    monkeypatch.setattr(
        server.registry,
        "get_tool",
        lambda name: None,
    )

    with pytest.raises(
        ValueError,
        match="not registered or is disabled",
    ):
        server.get_authorized_tool("github.nonexistent")