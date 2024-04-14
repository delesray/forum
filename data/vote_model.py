from pydantic import BaseModel


class Reply(BaseModel):
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
