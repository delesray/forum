from fastapi import HTTPException, Depends
from typing import Annotated
from data.models import User
from services.users_services import is_authenticated, from_token


def get_user_or_raise_401(token: str) -> User | HTTPException:
    if not is_authenticated(token):
        raise HTTPException(status_code=401)

    return from_token(token)


def is_admin_or_raise_401_403(token: str) -> bool | HTTPException:
    user = get_user_or_raise_401(token)
    if not user.is_admin:
        raise HTTPException(status_code=401)
    return True

UserAuthDep = Annotated[User, Depends(get_user_or_raise_401)]