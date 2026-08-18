from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.auth.authentication import (
    AuthenticationError,
    create_authentication_context,
)
from app.auth.jwt import create_access_token
from app.mcp.server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="Enterprise MCP Tool Gateway",
    description="Secure tool gateway for AI agents",
    version="0.1.0",
    lifespan=lifespan,
)


class LoginRequest(BaseModel):
    username: str


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "enterprise-mcp-gateway",
        "version": "0.1.0",
    }


@app.post("/auth/login")
async def login(request: LoginRequest):
    try:
        context = create_authentication_context(
            request.username
        )

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    access_token = create_access_token(
        context.user
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,
    }


app.mount(
    "/mcp",
    mcp.streamable_http_app(),
)