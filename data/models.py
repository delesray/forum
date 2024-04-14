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


class Topic(BaseModel):
    topic_id: int | None = None
    title: str
    is_locked: bool
    category_id: int 
    user_id: int
    best_reply: int


class Reply(BaseModel):
    reply_id: int | None = None
    text: str
    user_id: int
    topic_id: int


    @classmethod
    def from_query(cls, reply_id, text, user_id, topic_id):
        return cls(
            reply_id=reply_id,
            text=text,
            user_id=user_id,
            topic_id=topic_id
        )
    

class Vote(BaseModel):
    user_id: int
    reply_id: int
    type: bool


    @classmethod
    def from_query(cls, user_id, reply_id, type):
        return cls(
            user_id=user_id,
            reply_id=reply_id,
            type=type
        )

    
class Message(BaseModel):
    message_id: int | None = None
    text: str
    timestamp: date
    sender_id: int
    receiver_id: int


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
