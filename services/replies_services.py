from data.models import Reply
from data.database import read_query, update_query, insert_query


def get_all(id: int):
    data = read_query(
        '''SELECT reply_id, text, user_id, topic_id
        FROM replies WHERE topic_id = ?''', (id, ))

    replies = [Reply.from_query(*row) for row in data]
    return replies if replies else None


def get_by_id(id: int):
    data = read_query(
        '''SELECT reply_id, text, user_id, topic_id
        FROM replies WHERE reply_id = ?''', (id, )
    )

    return Reply.from_query(*data[0]) if data else None


def create_reply(topic_id: int, reply: Reply, user_id: int):
    reply_id = insert_query(
            'INSERT INTO replies(text, user_id, topic_id) VALUES(?,?,?)',
            (reply.text, user_id, topic_id)
        )
    
    return f'Reply with id {reply_id} successfully added'


def update_reply(id: int, text: str):
    return update_query(
        '''UPDATE replies SET text = ? WHERE reply_id = ?''', (text, id)
    )
