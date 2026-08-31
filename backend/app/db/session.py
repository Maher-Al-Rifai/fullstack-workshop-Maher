from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


def database_is_ready() -> bool:
    with engine.connect() as connection:
        return connection.scalar(text("SELECT 1")) == 1


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
