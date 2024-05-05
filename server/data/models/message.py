from pydantic import BaseModel


class Message(BaseModel):
    message_id: int | None = None
    text: str
    sender_id: int
    receiver_id: int

    @classmethod
    def from_query(cls, message_id, text, sender_id, receiver_id):
        return cls(
            message_id=message_id,
            text=text,
            sender_id=sender_id,
            receiver_id=receiver_id
        )


class MessageText(BaseModel):
    text: str
