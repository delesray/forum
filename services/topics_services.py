from __future__ import annotations

from data.models.topic import Status, TopicResponse, TopicCreate, TopicWithReplies
from data.models.user import User
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError
from fastapi import HTTPException
from common.responses import NotFound, Forbidden
from data.models.reply import ReplyResponse
from services.users_services import exists_by_username
from services.categories_services import exists_by_name

_TOPIC_BEST_REPLY = None


def exists(id: int):
    return any(read_query('SELECT 1 from topics WHERE topic_id=?', (id,)))


def get_total_count(sql=None, params=None):
    if sql:
        return read_query(f'SELECT COUNT(*) FROM ({sql}) as filtered_topics', params)[0][0]
    return read_query(f'SELECT COUNT(*) FROM topics')[0][0] #ToDo discuss: sql is never None, we never get here -> to be used somewhere else


def get_all(
        page: int,
        size: int,
        search: str = None,
        username: str = None,
        category: str = None,
        status: str = None,
        sort: str = None,
        sort_by: str = None
):
    query_params = ()
    sql = '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
             FROM topics t 
             JOIN users u ON t.user_id = u.user_id
             JOIN categories c ON t.category_id = c.category_id'''

    if search:
        sql += ' WHERE t.title LIKE ?'
        query_params += (f'%{search}%',)

    if username:
        if search:
            sql += ' AND '
        else:
            sql += ' WHERE'
        sql += ' u.username = ?'
        query_params += (username,)

    if category:
        if search or username:
            sql += 'AND '
        else:
            sql += ' WHERE'
        sql += ' c.name = ? '
        query_params += (category,)

    if status:
        if search or username or category:
            sql += ' AND'
        else:
            sql += ' WHERE' 
        sql += ' t.is_locked = ? '
        query_params += (Status.str_int[status],)

    if sort:
        sql += f' ORDER BY {sort_by} {sort}'

    total_count = get_total_count(sql, query_params)

    pagination_sql = sql + ' LIMIT ? OFFSET ?'
    query_params += (size, size * (page - 1))

    data = read_query(pagination_sql, query_params)
    topics = [TopicResponse.from_query(*row) for row in data]
    return topics, total_count


def get_by_id(topic_id: int):
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
               FROM topics t 
               JOIN users u ON t.user_id = u.user_id
               JOIN categories c ON t.category_id = c.category_id WHERE t.topic_id = ?''', (topic_id,))

    return next((TopicResponse.from_query(*row) for row in data), None)


def create(topic: TopicCreate, customer: User):
    try:
        generated_id = insert_query(
            'INSERT INTO topics(title, user_id, is_locked, best_reply_id, category_id) VALUES(?,?,?,?,?)',
            (topic.title, customer.user_id, Status.str_int["open"], _TOPIC_BEST_REPLY, topic.category_id))

        return generated_id  # return TopicResponse()
    except IntegrityError as e:
        return e


def update_title(topic_id, title):
    update_query(
        '''UPDATE topics SET
           title = ?
           WHERE topic_id = ? 
        ''',
        (title, topic_id))

    return f"Project title updated to {title}"


def update_best_reply(topic_id, best_reply_id):
    update_query(
        '''UPDATE topics SET
           best_reply_id = ?
           WHERE topic_id = ? 
        ''',
        (best_reply_id, topic_id))

    return f"Project Best Reply Id updated to {best_reply_id}"


def custom_sort(topics: list[TopicResponse], attribute, reverse=False):
    return sorted(
        topics,
        key=lambda t: getattr(t, attribute) if getattr(t, attribute) is not None else float('inf'),
        # float('inf') - positive infinity, None values are treated as if are greater than any real val
        reverse=reverse)


def get_topic_replies(topic_id: int) -> list[int]:
    data = read_query(
        '''SELECT reply_id
        FROM replies WHERE topic_id = ?''', (topic_id,))

    replies_ids = [tupl[0] for tupl in data]
    return replies_ids


def get_categories_names():
    data = read_query(
        '''SELECT name FROM categories''')

    categories_names = [tupl[0] for tupl in data]

    return categories_names


def get_usernames():
    data = read_query(
        '''SELECT username FROM users''')

    usernames = [tupl[0] for tupl in data]
    return usernames


def validate_topic_access(topic_id: int, user: User):
    existing_topic = get_by_id(topic_id)

    if not existing_topic:
        return NotFound(f"Topic #ID:{topic_id} does not exist")

    if existing_topic.status == Status.LOCKED:
        return Forbidden(f"Topic #ID:{existing_topic.topic_id} is locked")

    if existing_topic.user_id != user.user_id:
        return Forbidden('You are not allowed to edit topics created by other users')

    return None


def update_locking(locking: bool, topic_id: int):
    update_query('UPDATE topics SET is_locked = ? WHERE topic_id = ?',
                 (locking, topic_id))


def is_owner(topic_id: int, user_id: int):
    data = read_query('SELECT FROM topics = ? WHERE topic_id = ? AND user_id = ?',
                      (topic_id, topic_id))
    if not data:
        return False
    return True


def dto(data):
    replies = []

    for tid, t_title, tuserid, u_username, tislocked, tbrid, tcategoryid, cname, r_replyid, rtext, r_username in data:
        if any(data[0][8:]):
            replies.append(
                ReplyResponse.from_query(*(r_replyid, rtext, r_username, tid))
            )

    topic = TopicResponse.from_query(tid, t_title, tuserid, u_username, tislocked, tbrid, tcategoryid, cname)

    topic_with_replies = TopicWithReplies.from_query(topic, replies)
    return topic_with_replies


def get_topic_by_id_with_replies(topic_id: int):
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id,
           t.category_id, c.name, r.reply_id, r.text, ur.username 
           FROM topics t 
           JOIN users u ON t.user_id = u.user_id
           JOIN categories c ON t.category_id = c.category_id
           LEFT JOIN replies r ON t.topic_id = r.topic_id
           LEFT JOIN users ur ON r.user_id = ur.user_id
           WHERE t.topic_id = ?''', (topic_id,))

    if not data:
        return None

    topic_dto = dto(data)
    return topic_dto
