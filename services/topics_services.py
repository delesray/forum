from data.models import Topic, Reply
from data.database import read_query, update_query, insert_query

def get_all():
    pass

def get_by_id(topic_id: int):
    pass

def get_topic_replies(topic_id: int) -> list[Reply]:
    pass

def create(topic: Topic):
    pass

def update(old: Topic, new: Topic):
    pass

def custom_sort(lst: list[Topic], reverse=False):
    return sorted(
        lst,
        key=lambda t: t.user_id,
        reverse=reverse)