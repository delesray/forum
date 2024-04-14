from pydantic import BaseModel


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
