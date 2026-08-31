import argon2

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate

_ph = argon2.PasswordHasher()


def register(db: Session, data: UserCreate) -> User:
    email = data.email.lower()
    if user_repository.get_by_email(db, email) is not None:
        raise ConflictError("Email already registered")
    user = User(
        email=email,
        full_name=data.full_name,
        password_hash=_ph.hash(data.password),
    )
    user_repository.add(db, user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email.lower())
    if user is None or not user.is_active:
        raise UnauthorizedError("Invalid credentials")
    try:
        _ph.verify(user.password_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        raise UnauthorizedError("Invalid credentials")
    return user
