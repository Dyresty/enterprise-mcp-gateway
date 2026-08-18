from app.auth.models import (
    AuthenticatedUser,
    AuthenticationContext,
)

from app.auth.jwt import (
    JWTAuthenticationError,
    decode_access_token,
)


class AuthenticationError(Exception):
    """Raised when authentication fails."""


# Temporary development users.
# These will later be replaced by a real authentication backend.
USERS = {
    "analyst": AuthenticatedUser(
        user_id="user-001",
        username="analyst",
        role="analyst",
    ),
    "developer": AuthenticatedUser(
        user_id="user-002",
        username="developer",
        role="developer",
    ),
    "admin": AuthenticatedUser(
        user_id="user-003",
        username="admin",
        role="admin",
    ),
}


def authenticate(username: str) -> AuthenticatedUser:
    """
    Authenticate a user by username.

    Raises:
        AuthenticationError:
            If the user does not exist.
    """

    user = USERS.get(username)

    if user is None:
        raise AuthenticationError(
            f"Authentication failed for user '{username}'."
        )

    return user


def create_authentication_context(
    username: str,
) -> AuthenticationContext:
    """
    Authenticate a user by username and create an authentication context.
    """

    user = authenticate(username)

    return AuthenticationContext(user=user)


def create_authentication_context_from_token(
    token: str,
) -> AuthenticationContext:
    """
    Authenticate a user using a JWT access token.
    """

    try:
        user = decode_access_token(token)

    except JWTAuthenticationError as exc:
        raise AuthenticationError(
            str(exc)
        ) from exc

    return AuthenticationContext(user=user)