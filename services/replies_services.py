from __future__ import annotations
from typing import Union
from data.models import Reply, ReplyResponse, Topic, Category
from data.database import read_query, update_query, insert_query
from services.categories_services import get_by_id as get_cat_by_id, has_write_access


def get_all(id: int) -> Union[list[Reply], None]:
    data = read_query(
        '''SELECT r.reply_id, r.text, u.username, r.topic_id
        FROM replies r 
        JOIN users u ON r.user_id = u.user_id
        WHERE topic_id = ?''', (id, ))

    replies = [ReplyResponse.from_query(*row) for row in data]
    return replies if replies else None


def get_by_id(id: int) -> Union[Reply, None]:
    data = read_query(
        '''SELECT reply_id, text, user_id, topic_id
        FROM replies WHERE reply_id = ?''', (id, )
    )

    return Reply.from_query(*data[0]) if data else None


def create_reply(topic_id: int, reply: Reply, user_id: int) -> str:
    reply_id = insert_query(
            'INSERT INTO replies(text, user_id, topic_id) VALUES(?,?,?)',
            (reply.text, user_id, topic_id)
        )
    
    return f'Reply with id {reply_id} successfully added'


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
    topic: Topic = get_topic_by_id(topic_id)
    category: Category = get_cat_by_id(topic.category_id)

    if category.is_private and not has_write_access(user_id, category.category_id):
        return False, 'You don\'t have permissions to post or modify replies in this topic'

    if topic.status == 'locked':
        return False, 'This topic is read-only'
    
    return True, "OK"


from services.topics_services import get_by_id as get_topic_by_id
