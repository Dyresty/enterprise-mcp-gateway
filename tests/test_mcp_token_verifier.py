import asyncio

from app.auth.authentication import authenticate
from app.auth.jwt import create_access_token
from app.auth.mcp_token_verifier import MCPJWTTokenVerifier


def test_valid_jwt_is_converted_to_mcp_access_token():
    user = authenticate("developer")
    token = create_access_token(user)

    verifier = MCPJWTTokenVerifier()

    access_token = asyncio.run(
        verifier.verify_token(token)
    )

    assert access_token is not None
    assert access_token.token == token
    assert access_token.client_id == "developer"
    assert access_token.scopes == ["developer"]
    assert access_token.subject == "user-002"
    assert access_token.claims["username"] == "developer"
    assert access_token.claims["role"] == "developer"


def test_invalid_jwt_returns_none():
    verifier = MCPJWTTokenVerifier()

    access_token = asyncio.run(
        verifier.verify_token("invalid.jwt.token")
    )

    assert access_token is None


def test_wrong_secret_jwt_returns_none():
    import jwt

    token = jwt.encode(
        {
            "sub": "user-002",
            "username": "developer",
            "role": "developer",
        },
        "wrong-secret-that-is-at-least-32-bytes-long",
        algorithm="HS256",
    )

    verifier = MCPJWTTokenVerifier()

    access_token = asyncio.run(
        verifier.verify_token(token)
    )

    assert access_token is None