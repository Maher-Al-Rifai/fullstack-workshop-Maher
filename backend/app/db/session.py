from sqlalchemy import create_engine, text

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)


def database_is_ready() -> bool:
    with engine.connect() as connection:
        return connection.scalar(text("SELECT 1")) == 1
