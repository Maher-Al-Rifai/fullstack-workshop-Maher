from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.core.tokens import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserRegister


def register(db: Session, data: UserRegister) -> User:
    email = data.email.lower().strip()
    if user_repository.get_by_email(db, email):
        raise ConflictError("Email already registered")
    user = User(
        email=email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        is_active=True,
    )
    user_repository.add(db, user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> tuple[str, str]:
    user = user_repository.get_by_email(db, email.lower().strip())
    # Generic error regardless of whether email exists — prevents user enumeration
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")
    if not user.is_active:
        raise UnauthorizedError("Invalid credentials")
    return create_access_token(user.id), create_refresh_token(user.id)


def refresh_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
    user_id = decode_refresh_token(refresh_token)
    user = user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("Invalid credentials")
    return create_access_token(user.id), create_refresh_token(user.id)
