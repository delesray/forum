from pydantic import BaseModel


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
