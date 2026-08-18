class AuthorizationError(Exception):
    """Raised when a user is not authorized to execute a tool."""


ROLE_HIERARCHY = {
    "analyst": 1,
    "developer": 2,
    "admin": 3,
}


def authorize_tool(
    user_role: str,
    tool: dict,
) -> None:
    """
    Authorize a user against the policy metadata stored for a tool.

    Raises:
        AuthorizationError: If the user does not have sufficient privileges.
    """

    if user_role not in ROLE_HIERARCHY:
        raise AuthorizationError(
            f"Unknown user role: '{user_role}'."
        )

    required_role = tool.get("required_role")

    if required_role not in ROLE_HIERARCHY:
        raise AuthorizationError(
            f"Invalid required role configured for tool "
            f"'{tool.get('name')}': '{required_role}'."
        )

    user_level = ROLE_HIERARCHY[user_role]
    required_level = ROLE_HIERARCHY[required_role]

    if user_level < required_level:
        raise AuthorizationError(
            f"Role '{user_role}' is not authorized to execute "
            f"tool '{tool.get('name')}'. "
            f"Required role: '{required_role}'."
        )