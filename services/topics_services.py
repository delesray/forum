from data.models import Topic, StatusCode
from data.database import read_query, update_query, insert_query
from helpers import helpers

def get_all(search: str = None):
    # will be changed
    if search is None:
        data = read_query(
            '''SELECT topic_id, title, user_id, is_locked, best_reply_id, category_id
               FROM topics''')
    else:
        data = read_query(
            '''SELECT t.topic_id, t.title, t.user_id, t.is_locked, t.best_reply_id, t.category_id
               FROM topics t
               JOIN categories c ON t.category_id = c.category_id 
               JOIN users u ON t.user_id = u.user_id 
               WHERE u.username LIKE ? 
                  OR c.name LIKE ? 
                  OR t.topic_id LIKE ?''',
            (f'%{search}%', f'%{search}%', f'%{search}%'))

    topics = [Topic.from_query(*row) for row in data]
    return topics

def get_by_id(topic_id: int):
    data = read_query(
        '''SELECT topic_id, title, user_id, is_locked, best_reply_id, category_id
               FROM topics WHERE topic_id = ?''', (topic_id,))

    topic = [Topic.from_query(*row) for row in data]
    if not topic:
        return None

    return topic[0]



def create(topic: Topic):
    data = insert_query(
        'INSERT INTO topics(title, user_id, is_locked, best_reply_id, category_id) VALUES(?,?,?,?,?)',
        (topic.title, topic.user_id, topic.is_locked, topic.best_reply_id, topic.category_id))

    if not isinstance(data, int):
        error_msg = helpers.humanize_error_msg(data)
        return error_msg, StatusCode.BAD_REQUEST

    generated_id = data
    return f'Topic {generated_id} was successfully created!', StatusCode.OK



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
    pass


def update_best_reply(topic_id, best_reply):
    pass




def custom_sort(topics: list[Topic], *, attribute='title', reverse=False):
    return sorted(
        topics,
        key=lambda t: getattr(t, attribute),
        reverse=reverse)


def status_to_db_format(status: str) -> int:
    if status == 'open':
            status_val = 0
    else:
            status_val = 1
            
    return status_val
    