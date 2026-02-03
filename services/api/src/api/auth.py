from fastapi import Header

from api.config import get_settings


def get_user(x_user: str | None = Header(default=None, alias="X-User")) -> str:
    if x_user:
        return x_user
    return get_settings().DEV_USER
