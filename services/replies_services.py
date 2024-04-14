from data.models import Reply
from data.database import read_query, update_query, insert_query


def get_all(id: int):
    data = read_query(
        '''SELECT reply_id, text, user_id, topic_id
        FROM replies WHERE topic_id = ?''', (id, ))

    replies = [Reply.from_query(*row) for row in data]
    return replies if replies else None


def create_reply(id: int, reply: Reply):
    insert_query(
            'INSERT INTO replies(reply_id, text, user_id, topic_id) VALUES(?,?,?,?)',
            (reply.reply_id, reply.text, reply.user_id, reply.topic_id)
        )
    
    return f'Reply with {reply.id} successfully added'
