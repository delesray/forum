from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated


class User(BaseModel):
    user_id: int | None = None
    username: str
    password: str
    email: str  # constr(pattern='^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')
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
    email: str  # constr(pattern='^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')
    first_name: str | None = None
    last_name: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserUpdatePassword(BaseModel):
    old: str
    new: str
    re_new: str


class Message(BaseModel):
    message_id: int | None = None
    text: str
    sender_id: int
    receiver_id: int


class Category(BaseModel):
    category_id: int | None = None
    name: str
    is_locked: bool = False
    is_private: bool = False

    # users_ids: list[]
    # topics_ids: list[]

    @classmethod
    def from_query(cls, category_id, name, is_locked, is_private):
        return cls(
            category_id=category_id,
            name=name,
            is_locked=True if is_locked == 1 else False,
            is_private=True if is_private == 1 else False

        )


class ReplyCreateUpdate(BaseModel):
    text: str


class ReplyResponse(BaseModel):
    reply_id: int
    text: str
    username: str
    topic_id: int

    @classmethod
    def from_query(cls, reply_id, text, username, topic_id):
        return cls(
            reply_id=reply_id,
            text=text,
            username=username,
            topic_id=topic_id
        )


class VoteStatus:
    str_to_int = {'up': 1, 'down': 0}
    int_ti_str = {0: 'down', 1: 'up'}


class Status:
    OPEN = 'open'
    LOCKED = 'locked'
    str_int = {'open': 1, 'locked': 0}
    int_str = {1: 'open', 0: 'locked'}
    opposite = {'open': 'locked', 'locked': 'open'}


UNCATEGORIZED_ID = 1  # 'Uncategorized' category is created on db initialization


# class Topic(BaseModel):
#     topic_id: int | None = None
#     title: str
#     user_id: int
#     status: str = Status.OPEN
#     best_reply_id: int | None = None
#     category_id: int = UNCATEGORIZED_ID

#     @classmethod
#     def from_query(cls, topic_id, title, user_id, status, best_reply_id, category_id):
#         return cls(
#             topic_id=topic_id,
#             title=title,
#             user_id=user_id,
#             status=Status.int_str[status],
#             best_reply_id=best_reply_id,
#             category_id=category_id
#         )


class TopicUpdate(BaseModel):
    title: str | None = None
    best_reply_id: int | None = None


class TopicResponse(BaseModel):
    topic_id: int
    title: str
    user_id: int
    author: str
    status: str
    best_reply_id: int | None
    category_id: int = UNCATEGORIZED_ID
    category_name: str

    @classmethod
    def from_query(cls, topic_id, title, user_id, author, status, best_reply_id, category_id, category_name):
        return cls(
            topic_id=topic_id,
            title=title,
            user_id=user_id,
            author=author,
            status=Status.int_str[status],
            best_reply_id=best_reply_id,
            category_id=category_id,
            category_name=category_name
        )


class TopicCreate(BaseModel):
    title: str = Field(..., min_length=1)
    category_id: int = UNCATEGORIZED_ID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    is_admin: bool


class MessageCreate(BaseModel):
    text: str
    receiver_id: int