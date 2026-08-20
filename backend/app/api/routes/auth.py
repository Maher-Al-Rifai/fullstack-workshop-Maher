from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserRead, UserRegister
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"


def _set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        # Secure only in production — dev runs over plain HTTP
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
        # Scoped to auth path so the cookie is not sent on every API request
        path="/api/v1/auth",
    )


@router.post("/register", response_model=UserRead, status_code=201)
def register(body: UserRegister, db: Session = Depends(get_db)) -> User:
    return auth_service.register(db, body)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    access, refresh = auth_service.login(db, body.email, body.password)
    _set_refresh_cookie(response, refresh)
    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
) -> TokenResponse:
    if not refresh_token:
        raise UnauthorizedError("Refresh token missing")
    access, new_refresh = auth_service.refresh_tokens(db, refresh_token)
    _set_refresh_cookie(response, new_refresh)
    return TokenResponse(access_token=access)


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/v1/auth")


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
