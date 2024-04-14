from datetime import date
from pydantic import BaseModel


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
    
    
    
class Message(BaseModel):
    message_id: int | None = None
    text: str
    timestamp: date
    sender_id: int
    receiver_id: int
    
