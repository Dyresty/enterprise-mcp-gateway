from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.auth.models import AuthenticatedUser

from app.config import settings


class JWTAuthenticationError(Exception):
    """Raised when a JWT is invalid or cannot be decoded."""


def create_access_token(
    user: AuthenticatedUser,
) -> str:
    """
    Create a signed JWT access token for an authenticated user.
    """

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> AuthenticatedUser:
    """
    Decode and validate a JWT access token.

    Raises:
        JWTAuthenticationError:
            If the token is invalid, expired, malformed,
            or missing required claims.
    """

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

    except jwt.ExpiredSignatureError as exc:
        raise JWTAuthenticationError(
            "JWT access token has expired."
        ) from exc

    except jwt.InvalidTokenError as exc:
        raise JWTAuthenticationError(
            "Invalid JWT access token."
        ) from exc

    user_id = payload.get("sub")
    username = payload.get("username")
    role = payload.get("role")

    if not user_id or not username or not role:
        raise JWTAuthenticationError(
            "JWT is missing required user claims."
        )

    return AuthenticatedUser(
        user_id=str(user_id),
        username=str(username),
        role=str(role),
    )