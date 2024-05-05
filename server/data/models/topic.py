from pydantic import BaseModel, Field
from common.utils import PaginationInfo, Links
from data.models.reply import ReplyResponse


class Status:
    OPEN = 'open'
    LOCKED = 'locked'
    str_int = {'open': 0, 'locked': 1}
    int_str = {0: 'open', 1: 'locked'}
    opposite = {'open': 'locked', 'locked': 'open'}


UNCATEGORIZED_ID = 1  # 'Uncategorized' category is created on db initialization


class TopicUpdate(BaseModel):
    # title: str | None = None
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


class TopicsPaginate(BaseModel):
    topics: list[TopicResponse]
    pagination_info: PaginationInfo
    links: Links


class TopicRepliesPaginate(BaseModel):
    topic: TopicResponse
    replies: list[ReplyResponse]
    pagination_info: PaginationInfo
    links: Links


class Topic(BaseModel):
    topic_id: int | None = None
    title: str
    user_id: int
    status: str = Status.OPEN
    best_reply_id: int | None = None
    category_id: int = UNCATEGORIZED_ID

    @classmethod
    def from_query(cls, topic_id, title, user_id, status, best_reply_id, category_id):
        return cls(
            topic_id=topic_id,
            title=title,
            user_id=user_id,
            status=Status.int_str[status],
            best_reply_id=best_reply_id,
            category_id=category_id
        )
