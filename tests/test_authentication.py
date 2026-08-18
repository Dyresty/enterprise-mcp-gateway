import pytest

from app.auth.authentication import (
    AuthenticationError,
    create_authentication_context,
)


def test_analyst_authentication():
    context = create_authentication_context("analyst")

    assert context.user.user_id == "user-001"
    assert context.user.username == "analyst"
    assert context.user.role == "analyst"


def test_developer_authentication():
    context = create_authentication_context("developer")

    assert context.user.user_id == "user-002"
    assert context.user.username == "developer"
    assert context.user.role == "developer"


def test_admin_authentication():
    context = create_authentication_context("admin")

    assert context.user.user_id == "user-003"
    assert context.user.username == "admin"
    assert context.user.role == "admin"


def test_unknown_user_authentication_fails():
    with pytest.raises(AuthenticationError):
        create_authentication_context("unknown-user")