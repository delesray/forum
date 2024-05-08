from unittest.mock import Mock

TOPIC_ID = 1
REPLY_ID = 1
USER_ID = 1

VOTE_TYPE_STR = 'up'
VOTE_TYPE_INT = 1
NEW_VOTE_TYPE = 'down'


def fake_category(is_private: bool):
    category = Mock()
    category.category_id = 1
    category.is_private = is_private

    return category


def fake_topic(status: str):
    topic = Mock()
    topic.category_id = 1
    topic.status = status

    return topic


def fake_user():
    user = Mock()
    user.user_id = 1

    return user


def fake_create_update_reply(text: str):
    reply = Mock()
    reply.text = text

    return reply
