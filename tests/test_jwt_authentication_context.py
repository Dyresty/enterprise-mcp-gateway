import pytest

from app.auth.authentication import (
    AuthenticationError,
    create_authentication_context_from_token,
)
from app.auth.jwt import create_access_token
from app.auth.models import AuthenticatedUser


def test_jwt_creates_authentication_context():
    user = AuthenticatedUser(
        user_id="user-001",
        username="analyst",
        role="analyst",
    )

    token = create_access_token(user)

    context = create_authentication_context_from_token(token)

    assert context.user.user_id == "user-001"
    assert context.user.username == "analyst"
    assert context.user.role == "analyst"


def test_jwt_context_preserves_developer_role():
    user = AuthenticatedUser(
        user_id="user-002",
        username="developer",
        role="developer",
    )

    token = create_access_token(user)

    context = create_authentication_context_from_token(token)

    assert context.user.username == "developer"
    assert context.user.role == "developer"


def test_invalid_jwt_cannot_create_authentication_context():
    with pytest.raises(AuthenticationError):
        create_authentication_context_from_token(
            "invalid.jwt.token"
        )