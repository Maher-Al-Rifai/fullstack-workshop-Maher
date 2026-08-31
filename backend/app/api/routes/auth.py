from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import UnauthorizedError
from app.core.tokens import create_access_token, create_refresh_token, decode_refresh_token
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repository
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_NAME = "refresh_token"
_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


class _LoginBody(BaseModel):
    email: str
    password: str


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)) -> User:
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(
    data: _LoginBody,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        user = auth_service.authenticate(db, data.email, data.password)
    except UnauthorizedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    token = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        user_id = decode_refresh_token(token)
    except UnauthorizedError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = user_repository.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    _set_refresh_cookie(response, new_refresh)
    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(_COOKIE_NAME)
