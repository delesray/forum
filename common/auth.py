from fastapi import HTTPException
from data.models import User
from services.users_services import is_authenticated, from_token


def get_user_or_raise_401(token: str) -> User:
    if not is_authenticated(token):
        raise HTTPException(status_code=401)

    return from_token(token)
