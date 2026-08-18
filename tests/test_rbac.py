import pytest

from app.auth.rbac import (
    AuthorizationError,
    authorize_tool,
)


def make_tool(name: str, required_role: str) -> dict:
    return {
        "name": name,
        "required_role": required_role,
    }


def test_analyst_can_execute_analyst_tool():
    tool = make_tool("github.get_issue", "analyst")

    authorize_tool(
        user_role="analyst",
        tool=tool,
    )


def test_analyst_cannot_execute_developer_tool():
    tool = make_tool("github.create_issue", "developer")

    with pytest.raises(AuthorizationError):
        authorize_tool(
            user_role="analyst",
            tool=tool,
        )


def test_developer_can_execute_analyst_tool():
    tool = make_tool("github.get_issue", "analyst")

    authorize_tool(
        user_role="developer",
        tool=tool,
    )


def test_developer_can_execute_developer_tool():
    tool = make_tool("github.create_issue", "developer")

    authorize_tool(
        user_role="developer",
        tool=tool,
    )


def test_admin_can_execute_analyst_tool():
    tool = make_tool("github.get_issue", "analyst")

    authorize_tool(
        user_role="admin",
        tool=tool,
    )


def test_admin_can_execute_developer_tool():
    tool = make_tool("github.create_issue", "developer")

    authorize_tool(
        user_role="admin",
        tool=tool,
    )


def test_unknown_user_role_is_rejected():
    tool = make_tool("github.get_issue", "analyst")

    with pytest.raises(AuthorizationError):
        authorize_tool(
            user_role="unknown",
            tool=tool,
        )


def test_invalid_required_role_is_rejected():
    tool = make_tool("github.test", "superuser")

    with pytest.raises(AuthorizationError):
        authorize_tool(
            user_role="admin",
            tool=tool,
        )