from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth.authentication import AuthenticatedUser
from app.auth.jwt import (
    JWTAuthenticationError,
    create_access_token,
    decode_access_token,
)
from app.config import settings


def test_create_access_token_contains_user_identity():
    user = AuthenticatedUser(
        user_id="user-002",
        username="developer",
        role="developer",
    )

    token = create_access_token(user)

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    assert payload["sub"] == "user-002"
    assert payload["username"] == "developer"
    assert payload["role"] == "developer"
    assert "iat" in payload
    assert "exp" in payload


def test_decode_access_token_returns_authenticated_user():
    user = AuthenticatedUser(
        user_id="user-002",
        username="developer",
        role="developer",
    )

    token = create_access_token(user)

    decoded_user = decode_access_token(token)

    assert decoded_user == user


def test_invalid_token_is_rejected():
    with pytest.raises(
        JWTAuthenticationError,
        match="Invalid JWT access token",
    ):
        decode_access_token("this-is-not-a-valid-jwt")


def test_token_signed_with_wrong_secret_is_rejected():
    user = AuthenticatedUser(
        user_id="user-002",
        username="developer",
        role="developer",
    )

    token = jwt.encode(
        {
            "sub": user.user_id,
            "username": user.username,
            "role": user.role,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        "this-is-a-different-secret-key-32-bytes",
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(
        JWTAuthenticationError,
        match="Invalid JWT access token",
    ):
        decode_access_token(token)


def test_expired_token_is_rejected():
    payload = {
        "sub": "user-002",
        "username": "developer",
        "role": "developer",
        "iat": datetime.now(timezone.utc) - timedelta(minutes=2),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(
        JWTAuthenticationError,
        match="JWT access token has expired",
    ):
        decode_access_token(token)


def test_token_missing_required_claim_is_rejected():
    payload = {
        "sub": "user-002",
        "username": "developer",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=30),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(
        JWTAuthenticationError,
        match="JWT is missing required user claims",
    ):
        decode_access_token(token)