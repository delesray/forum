from typing import Annotated
from pydantic import BaseModel, StringConstraints


class User(BaseModel):
    user_id: int | None = None
    username: str
    password: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool | None = None

    @classmethod
    def from_query(cls, user_id, username, password, email, first_name, last_name, is_admin):
        return cls(
            user_id=user_id,
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin
        )


class UserRegister(BaseModel):
    username: Annotated[str, StringConstraints(min_length=4)]
    password: Annotated[str, StringConstraints(min_length=4)]
    email: Annotated[str, StringConstraints(pattern=r'^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')]
    first_name: Annotated[str, StringConstraints(min_length=2)] = None
    last_name: Annotated[str, StringConstraints(min_length=2)] = None


class UserUpdate(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=2)] = None
    last_name: Annotated[str, StringConstraints(min_length=2)] = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: Annotated[str, StringConstraints(min_length=4)]
    confirm_password: Annotated[str, StringConstraints(min_length=4)]


class UserDelete(BaseModel):
    current_password: str


class UserInfo(BaseModel):
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None

    @classmethod
    def from_query(cls, username, email, first_name, last_name):
        return cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )


class AnonymousUser:
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    is_admin: bool
