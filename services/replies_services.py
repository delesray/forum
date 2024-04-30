from __future__ import annotations
from typing import Union
from data.models import ReplyCreateUpdate, ReplyResponse, Category, TopicResponse
from data.database import read_query, update_query, insert_query
from services.categories_services import get_by_id as get_cat_by_id, has_write_access


def get_all(id: int) -> Union[list[ReplyResponse], None]:
    data = read_query(
        '''SELECT r.reply_id, r.text, u.username, r.topic_id
        FROM replies r 
        JOIN users u ON r.user_id = u.user_id
        WHERE topic_id = ?''', (id, ))

    return [ReplyResponse.from_query(*row) for row in data]


def get_by_id(id: int) -> Union[ReplyResponse, None]:
    data = read_query(
        '''SELECT r.reply_id, r.text, u.username, r.topic_id
        FROM replies r 
        JOIN users u ON r.user_id = u.user_id
        WHERE reply_id = ?''', (id, )
    )

    return ReplyResponse.from_query(*data[0]) if data else None


def create_reply(topic_id: int, reply: ReplyCreateUpdate, user_id: int) -> str:
    return insert_query(
            'INSERT INTO replies(text, user_id, topic_id) VALUES(?,?,?)',
            (reply.text, user_id, topic_id)
        )


def update_reply(id: int, text: str) -> bool:
    edited = 1 # True
    update_query(
        '''UPDATE replies SET text = ?, edited = ? WHERE reply_id = ?''', (text, edited, id)
    )


def delete_reply(id: int):
    update_query(
        '''DELETE from replies WHERE reply_id = ?''', (id,)
    )


# same logic is needed for post/edit/delete reply
def can_user_modify_reply(topic_id: int, user_id: int) -> Union[bool, str]:
    topic: TopicResponse = get_topic_by_id(topic_id)
    category: Category = get_cat_by_id(topic.category_id)

    if category.is_private and not has_write_access(user_id, category.category_id):
        return False, 'You don\'t have permissions to post or modify replies in this topic'

    if topic.status == 'locked':
        return False, 'This topic is read-only'
    
    return True, "OK"


from services.topics_services import get_by_id as get_topic_by_id
