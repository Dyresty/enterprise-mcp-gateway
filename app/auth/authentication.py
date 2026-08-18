from dataclasses import dataclass


class AuthenticationError(Exception):
    """Raised when authentication fails."""


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    username: str
    role: str


@dataclass(frozen=True)
class AuthenticationContext:
    """
    Represents the authenticated identity for the current execution context.
    """

    user: AuthenticatedUser


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
    Authenticate a user and return the authenticated identity.

    Raises:
        AuthenticationError: If the user does not exist.
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
    Authenticate a user and create an authentication context.
    """

    user = authenticate(username)

    return AuthenticationContext(user=user)