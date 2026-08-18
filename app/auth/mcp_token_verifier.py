from mcp.server.auth.provider import AccessToken

from app.auth.jwt import (
    JWTAuthenticationError,
    decode_access_token,
)


class MCPJWTTokenVerifier:
    """
    Adapter between the gateway's JWT authentication
    and the MCP SDK TokenVerifier interface.
    """

    async def verify_token(
        self,
        token: str,
    ) -> AccessToken | None:
        """
        Verify a gateway JWT and convert it into
        an MCP AccessToken.

        Returns:
            AccessToken:
                If the JWT is valid.

            None:
                If the JWT is invalid.
        """

        try:
            user = decode_access_token(token)

        except JWTAuthenticationError:
            return None

        return AccessToken(
            token=token,
            client_id=user.username,
            scopes=[user.role],
            expires_at=None,
            subject=user.user_id,
            claims={
                "username": user.username,
                "role": user.role,
            },
        )