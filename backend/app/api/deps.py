from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.db.session import SessionLocal
from app.models.user import User


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


async def get_current_user(db: Session = Depends(get_db)) -> User:
    """Stub replaced by JWT verification in Module 08."""
    raise UnauthorizedError("Authentication not implemented — override in tests")
