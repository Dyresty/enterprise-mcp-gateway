import pytest

from app.auth.authentication import (
    AuthenticationContext,
    create_authentication_context,
)
from app.auth.jwt import create_access_token
from app.auth.models import AuthenticatedUser
from app.mcp import server


def test_authenticate_request_with_jwt():
    user = AuthenticatedUser(
        user_id="user-002",
        username="developer",
        role="developer",
    )

    token = create_access_token(user)

    context = server.authenticate_request(token)

    assert isinstance(context, AuthenticationContext)
    assert context.user.user_id == "user-002"
    assert context.user.username == "developer"
    assert context.user.role == "developer"


def test_authenticate_request_rejects_invalid_jwt():
    with pytest.raises(
        ValueError,
        match="Invalid JWT access token",
    ):
        server.authenticate_request(
            "invalid.jwt.token"
        )


def test_authenticate_request_uses_development_fallback():
    context = server.authenticate_request()

    assert context.user.username == server.settings.AUTH_USERNAME


def test_set_authentication_context():
    user = AuthenticatedUser(
        user_id="user-002",
        username="developer",
        role="developer",
    )

    context = AuthenticationContext(user=user)

    server.set_authentication_context(context)

    assert server.AUTH_CONTEXT.user.username == "developer"
    assert server.AUTH_CONTEXT.user.role == "developer"