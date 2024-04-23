from data.models import Topic, User, TopicCreate, TopicResponse, Status
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError
from fastapi import HTTPException

_DEFAULT_STATUS = 'open'
_TOPIC_BEST_REPLY = None


def get_all(search: str = None, username: str = None, category: str = None, status: str = None) -> list[Topic]:
    query_params = ()
    sql = '''SELECT t.topic_id, t.title, u.username, t.is_locked, t.best_reply_id, c.name
               FROM topics t 
               JOIN users u ON t.user_id = u.user_id
               JOIN categories c ON t.category_id = c.category_id
               WHERE c.is_private != ?'''
    query_params += (1,)

    if search:
        sql += ' AND WHERE title LIKE ?'
        query_params += (f'%{search}%',)

    if username:
        if username not in get_usernames():
            raise HTTPException(status_code=400, detail="Invalid username")
        
        sql += ' AND WHERE u.username LIKE ?'
        query_params += (username,)

    if category:
        if category not in get_categories_names():
            raise HTTPException(status_code=400, detail="Invalid category")
    
        sql += ' AND WHERE c.name LIKE ? '
        query_params += (category,)

    if status:
        if status not in ['open', 'locked']:
            raise HTTPException(status_code=400, detail="Invalid status value")

        status_val = status_to_db_format(status)

        if search or username or category:
            sql_2 += ' AND'
        else:
            sql_2 += ' WHERE'
        sql_2 += ' t.is_locked = ?'
        query_params += (status_val,)

    sql = sql_1 + sql_2
    data = read_query(sql, query_params)

    topics = [Topic.from_query(*row) for row in data]
    return topics


def get_by_id(topic_id: int):
    data = read_query(
        '''SELECT topic_id, title, user_id, is_locked, best_reply_id, category_id
               FROM topics WHERE topic_id = ?''', (topic_id,))
    
    return next((Topic.from_query(*row) for row in data), None)
    


def create(topic: TopicCreate, customer: User):
   
    try:
        generated_id = insert_query(
            'INSERT INTO topics(title, user_id, is_locked, best_reply_id, category_id) VALUES(?,?,?,?,?)',
        (topic.title, customer.user_id, _DEFAULT_STATUS, _TOPIC_BEST_REPLY, get_category_id(topic.category_name)))
   
        return TopicResponse(
            topic_id=generated_id, 
            title=topic.title,
            username=customer.username,
            status=_DEFAULT_STATUS,
            best_reply_id=_TOPIC_BEST_REPLY,
            category=topic.category_name
        )

    except IntegrityError:
        
        return None



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
        (status_to_db_format(status), topic_id))

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


def custom_sort(topics: list[Topic], attribute, reverse=False):
    return sorted(
        topics,
        key=lambda t: getattr(t, attribute) if getattr(t, attribute) is not None else float('inf'),
        # float('inf') - positive infinity, None values are treated as if are greater than any real val
        reverse=reverse)


def status_to_db_format(status: str) -> int:
    if status == 'open':
        status_val = 0
    else:
        status_val = 1

    return status_val


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

def get_category_id(category_name: str) -> int:
    data = read_query(
        '''SELECT category_id
        FROM categories WHERE name = ?''', (category_name,))
    category_id, = data[0]
    return category_id
