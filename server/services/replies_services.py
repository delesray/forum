from __future__ import annotations
from typing import Union
from data.models.category import Category
from data.models.reply import ReplyCreateUpdate, ReplyResponse
from data.models.topic import TopicResponse
from data.database import read_query, update_query, insert_query
from services.topics_services import get_by_id as get_topic_by_id
from services.categories_services import get_by_id as get_cat_by_id, has_write_access
from common.utils import get_pagination_info, create_links
from starlette.requests import Request


def get_all(topic_id: int, request: Request, page: int, size: int) -> list[ReplyResponse]:
    params = (topic_id,)

    sql = '''SELECT r.reply_id, r.text, u.username, r.topic_id
            FROM replies r 
            JOIN users u ON r.user_id = u.user_id
            WHERE topic_id = ?'''

    pagination_sql = sql + ' LIMIT ? OFFSET ?'
    params += (size, size * (page - 1))

    data = read_query(pagination_sql, params)
    replies = [ReplyResponse.from_query(*row) for row in data]
    pagination_info = get_pagination_info(len(replies), page, size)
    links = create_links(request, pagination_info)
    
    return replies, pagination_info, links


def get_by_id(id: int) -> Union[ReplyResponse, None]:
    data = read_query(
        '''SELECT r.reply_id, r.text, u.username, r.topic_id
        FROM replies r 
        JOIN users u ON r.user_id = u.user_id
        WHERE reply_id = ?''', (id,)
    )

    return ReplyResponse.from_query(*data[0]) if data else None


def create_reply(topic_id: int, reply: ReplyCreateUpdate, user_id: int) -> int:
    return insert_query(
        'INSERT INTO replies(text, user_id, topic_id) VALUES(?,?,?)',
        (reply.text, user_id, topic_id,)
    )


def update_reply(id: int, text: str):
    edited = 1  # True
    update_query(
        '''UPDATE replies SET text = ?, edited = ? WHERE reply_id = ?''', (
            text, edited, id)
    )


def delete_reply(id: int):
    update_query(
        '''DELETE from replies WHERE reply_id = ?''', (id,)
    )


def can_user_access_topic_content(topic_id: int, user_id: int) -> tuple[bool, str]:
    topic: TopicResponse = get_topic_by_id(topic_id)
    category: Category = get_cat_by_id(topic.category_id)

    if category.is_private and not has_write_access(user_id, category.category_id):
        return False, 'You don\'t have permissions to post, modify replies or vote in this topic'

    if topic.status == 'locked':
        return False, 'This topic is read-only'

    return True, "OK"


def exists(reply_id: int, topic_id):
    return any(read_query('SELECT 1 FROM replies WHERE reply_id=? and topic_id=?', (reply_id, topic_id)))
