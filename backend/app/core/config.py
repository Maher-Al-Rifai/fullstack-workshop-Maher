from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Workboard API"
    app_version: str = "0.1.0"
    # "development" | "staging" | "production"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+psycopg://workboard:workboard-local-only@db:5432/workboard"
    )

    # Parsed as a JSON array in .env: CORS_ORIGINS='["http://localhost:3000"]'
    cors_origins: list[str] = ["http://localhost:3000"]

    # Secret — never expose in status/logs
    secret_key: str = "changeme-not-for-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
