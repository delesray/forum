from __future__ import annotations
from data.models import TopicResponse, Status, TopicCreate, User, Category, TopicUpdate, Topic
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError
from fastapi import HTTPException

_TOPIC_BEST_REPLY = None


def get_all(
        search: str = None,
        username: str = None,
        category: str = None,
        status: str = None
):
    query_params = ()
    sql = '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
             FROM topics t 
             JOIN users u ON t.user_id = u.user_id
             JOIN categories c ON t.category_id = c.category_id
             WHERE c.is_private = ?'''

    query_params += (0,)

    if search:
        sql += ' AND title LIKE ?'
        query_params += (f'%{search}%',)

    if username:
        if username not in get_usernames():
            raise HTTPException(status_code=400, detail="Invalid username")

        sql += ' AND u.username = ?'
        query_params += (username,)

    if category:
        if category not in get_categories_names():
            raise HTTPException(status_code=400, detail="Invalid category")

        sql += ' AND c.name = ? '
        query_params += (category,)

    if status:
        if status not in [Status.OPEN, Status.LOCKED]:
            raise HTTPException(status_code=400, detail="Invalid status value")

        sql += ' AND t.is_locked = ? '
        query_params += (Status.str_int[status],)

    data = read_query(sql, query_params)

    topics = [TopicResponse.from_query(*row) for row in data]
    return topics


def get_by_id(topic_id: int):
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
               FROM topics t 
               JOIN users u ON t.user_id = u.user_id
               JOIN categories c ON t.category_id = c.category_id WHERE t.topic_id = ?''', (topic_id,))

    return next((TopicResponse.from_query(*row) for row in data), None)


# def get_by_id_cat_id(topic_id: int) -> Topic | None:  # Miray
#     data = read_query(
#         '''SELECT topic_id, title, user_id, is_locked, best_reply_id, category_id 
#         FROM topics WHERE topic_id = ?''', (topic_id,))

#     return next((Topic.from_query(*row) for row in data), None)


def create(topic: TopicCreate, customer: User):
    try:
        generated_id = insert_query(
            'INSERT INTO topics(title, user_id, is_locked, best_reply_id, category_id) VALUES(?,?,?,?,?)',
            (topic.title, customer.user_id, Status.OPEN, _TOPIC_BEST_REPLY, topic.category_id))

        return generated_id
        # return TopicResponse(
        # )

    except IntegrityError as e:
        return e


def update_status(topic_id, status):
    # TODO
    # a user should not be able to change topic_id, user_id (author of the topic)
    # a user with write access can change title, is_locked
    # author can choose / change best reply
    # can category be changed?

    update_query(
        '''UPDATE topics SET
           is_locked = ?
           WHERE topic_id = ? 
        ''',
        (Status.str_int[status], topic_id))

    return f"Project status updated to {status}"


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


# def get_category_by_name(category_name: str) -> Category:
#     data = read_query(
#         '''SELECT category_id, name, is_locked, is_private
#         FROM categories WHERE name = ?''', (category_name,))

#     return next((Category.from_query(*row) for row in data), None)


def topic_with_replies(topic: TopicResponse):
    replies = get_all_replies(topic.topic_id)

    topic_with_replies = {
        "topic": topic,
        "replies": replies if replies else []
    }

    return topic_with_replies


def get_topics_from_private_categories(current_user: User) -> list[TopicResponse]:
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
           FROM topics t 
           JOIN users u ON t.user_id = u.user_id
           JOIN categories c ON t.category_id = c.category_id
           WHERE c.is_private = ?
           AND u.user_id = ?''', (1, current_user.user_id))

    topics = [TopicResponse.from_query(*row) for row in data]
    return topics


def topic_updates(topic_id: int, current_user: User, topic_update: TopicUpdate) -> str | None:
    if topic_update.title and len(topic_update.title) >= 1: #or return a message 'Title cannot be empty'?
        return update_title(topic_id, topic_update.title)

    if topic_update.status in [Status.OPEN, Status.LOCKED] and current_user.is_admin:#or return a message'Only administrators are authorized to change the status'
        return update_status(topic_id, topic_update.status)

    # todo only topic author can choose best reply - separate patch request
    if topic_update.best_reply_id:
        topic_replies_ids = get_topic_replies(topic_id)
        
        if not topic_replies_ids:
            return f"Topic with id:{topic_id} does not have replies"

        if topic_update.best_reply_id in topic_replies_ids:
            return update_best_reply(topic_id, topic_update.best_reply_id)

    return None


from services.replies_services import get_all as get_all_replies


def update_locking(locking: bool, topic_id: int):
    update_query('UPDATE topics SET is_locked = ? WHERE topic_id = ?',
                 (locking, topic_id))
