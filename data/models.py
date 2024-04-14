from datetime import date
from pydantic import BaseModel


class StatusCode:
    OK = 200
    NO_CONTENT = 204

    NOT_MODIFIED = 304

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404


class User(BaseModel):
    user_id: int | None = None
    username: str
    email: str
    first_name: str
    last_name: str
    is_admin: bool | None = None

    @classmethod
    def from_query(cls, user_id, username, email, first_name, last_name, is_admin):
        return cls(
            user_id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin
        )


class Category(BaseModel):
    category_id: int | None = None
    name: str
    is_locked: bool | None = None
    is_private: bool | None = None

    @classmethod
    def from_query(cls, category_id, name, is_locked, is_private):
        return cls(
            category_id=category_id,
            name=name,
            is_locked=is_locked,
            is_private=is_private,
        )
