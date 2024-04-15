from data.models import Topic, StatusCode
from data.database import read_query, update_query, insert_query
from helpers import helpers

def get_all(search: str = None):
    if search is None:
        data = read_query(
            '''SELECT topic_id, title, user_id, is_locked, best_reply, category_id
               FROM topics''')
    else:
        data = read_query(
            '''SELECT t.topic_id, t.title, t.user_id, t.is_locked, t.best_reply, t.category_id
               FROM topics t
               JOIN categories c ON t.category_id = c.category_id 
               JOIN users u ON t.user_id = u.user_id 
               WHERE u.username LIKE ? 
                  OR c.name LIKE ? 
                  OR CAST(t.topic_id AS TEXT) LIKE ?''',
            (f'%{search}%', f'%{search}%', f'%{search}%'))

    topics = [Topic.from_query_result(*row) for row in data]
    return topics

def get_by_id(topic_id: int):
    data = read_query(
        '''SELECT topic_id, title, user_id, is_locked, best_reply, category_id
               FROM topics WHERE topic_id = ?''', (topic_id,))

    topic = [Topic.from_query(*row) for row in data]
    if not topic:
        return None

    return topic[0]



def create(topic: Topic):
    data = insert_query(
        'INSERT INTO topics(title, user_id, is_locked, best_reply, category_id) VALUES(?,?,?,?,?)',
        (topic.title, topic.user_id, topic.is_locked, topic.best_reply, topic.category_id))

    if not isinstance(data, int):
        error_msg = helpers.humanize_error_msg(data)
        return error_msg, StatusCode.BAD_REQUEST

    generated_id = data
    return f'Topic {generated_id} was successfully created!', StatusCode.OK



def update(old: Topic, new: Topic):
    merged = Topic(
        topic_id=old.topic_id,
        title=new.title or old.title,
        user_id= old.user_id,
        is_locked=new.is_locked or old.is_locked,
        best_reply=new.best_reply or old.best_reply,
        category_id=old.category_id
    )
     
    data = update_query(
        'UPDATE topics SET title = ?, user_id = ?, is_locked = ?, best_reply = ?, category_id = ? WHERE topic_id = ?',
        (merged.title, merged.user_id, merged.is_locked, merged.best_reply, merged.category_id, merged.topic_id)
    )

    if data is not True:
        error_msg = helpers.humanize_error_msg(data)
        return error_msg, StatusCode.BAD_REQUEST

    return merged.__dict__, StatusCode.OK



def custom_sort(topics: list[Topic], *, attribute='topic_id', reverse=False):
    return sorted(
        topics,
        key=lambda t: getattr(t, attribute),
        reverse=reverse)