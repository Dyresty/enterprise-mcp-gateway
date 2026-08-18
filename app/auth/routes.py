from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth.authentication import (
    AuthenticationError,
    authenticate,
)
from app.auth.jwt import create_access_token
from app.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


class LoginRequest(BaseModel):
    username: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    request: LoginRequest,
) -> LoginResponse:
    """
    Authenticate a development user and issue a JWT access token.
    """

    try:
        user = authenticate(request.username)

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    access_token = create_access_token(user)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=(
            settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
    )
