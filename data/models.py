from datetime import date
from pydantic import BaseModel


class User(BaseModel):
    user_id: int | None = None
    username: str
    email: str
    first_name: str
    last_name: str
    is_admin: bool = False

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
