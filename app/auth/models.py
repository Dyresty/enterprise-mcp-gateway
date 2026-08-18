from dataclasses import dataclass


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