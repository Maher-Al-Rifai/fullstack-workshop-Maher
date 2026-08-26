from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

_ALGORITHM = "HS256"
_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": _ACCESS_TYPE},
        settings.secret_key,
        algorithm=_ALGORITHM,
    )


def create_refresh_token(user_id: int) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": _REFRESH_TYPE},
        settings.secret_key,
        algorithm=_ALGORITHM,
    )


def _decode(token: str, expected_type: str) -> int:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")
    if payload.get("type") != expected_type:
        raise UnauthorizedError("Wrong token type")
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Invalid token subject")
    try:
        return int(sub)
    except ValueError:
        raise UnauthorizedError("Invalid token subject")


def decode_access_token(token: str) -> int:
    return _decode(token, _ACCESS_TYPE)


def decode_refresh_token(token: str) -> int:
    return _decode(token, _REFRESH_TYPE)
