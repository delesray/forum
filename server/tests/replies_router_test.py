import unittest
from unittest.mock import Mock, patch
from routers import replies as replies_router
from data.models.reply import ReplyCreateUpdate
from routers.replies import HTTPException


TOPIC_ID = 1
REPLY_ID = 1
reply = ReplyCreateUpdate(text='sometext')


def fake_user():
    user = Mock()
    user.user_id = 1

    return user


class RepliesRouter_Should(unittest.TestCase):

    def test_addReply_returnsCorrectMsg_whenUserHasAccessToTopic(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access, \
                patch('routers.replies.replies_services.create_reply') as mock_create_reply:

            mock_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_create_reply.return_value = REPLY_ID

            expected = f'Reply with ID {REPLY_ID} successfully added'

            result = replies_router.add_reply(topic_id=TOPIC_ID, reply=reply,
                                              current_user=fake_user())

            self.assertEqual(expected, result)

    def test_raisesHTTPException_statusCode404_whenTopicNotExists(self):
        with patch('routers.replies.exists') as mock_exists:

            mock_exists.return_value = False

            with self.assertRaises(HTTPException):
                replies_router.add_reply(topic_id=TOPIC_ID, reply=reply,
                                         current_user=fake_user())

    def test_raisesHTTPException_statusCode403_whenUsedNotHasAccessToTopic(self):
        pass
