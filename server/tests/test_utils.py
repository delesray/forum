from unittest.mock import Mock
from data.models.user import Token, User, UserInfo


# topics
TOPIC_ID = 1
REPLY_ID = 1
USER_ID = 1

# votes
VOTE_TYPE_STR = 'up'
VOTE_TYPE_INT = 1
NEW_VOTE_TYPE = 'down'

# users
USERNAME = 'username'
PASSWORD = 'hashed_password'
EMAIL = 'email@mail.com'
FIRST_NAME = 'FirstName'
LAST_NAME = 'LastName'


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


def create_user_info(username: str ='username'):
    return UserInfo(username=username,
                    email=EMAIL,
                    first_name=FIRST_NAME,
                    last_name=LAST_NAME)


def create_user(is_admin: bool = False):
    return User(user_id=USER_ID,
                username=USERNAME,
                password=PASSWORD,
                email=EMAIL,
                first_name=FIRST_NAME,
                last_name=LAST_NAME,
                is_admin=is_admin)

fake_token = Mock(spec=Token)
