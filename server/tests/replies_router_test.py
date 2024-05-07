import unittest
from http.client import HTTPException
from unittest.mock import Mock, patch
from routers import replies as replies_router
from routers import topics as topics_router
from data.models.reply import ReplyCreateUpdate
from fastapi.testclient import TestClient
from main import app

mock_replies_service = Mock(autospec=True)
mock_topics_service = Mock(autospec=True)

replies_router.replies_services = mock_replies_service
replies_router.topics_services = mock_topics_service

TOPIC_ID = 1
REPLY_ID = 1
reply = ReplyCreateUpdate(text='sometext')


def fake_user():
    user = Mock()
    user.user_id = 1

    return user


client = TestClient(app)


def temp():
    from routers.replies import HTTPException
    from unittest import TestCase
    from unittest.mock import patch
    from routers import replies as r

    class RepliesRouter_Should(TestCase):
        @patch('routers.replies.exists')
        def test_m_raisesHTTPException_statusCode404_whenTopicNotExists(self, mock_exists):
            mock_exists.return_value = False

            with self.assertRaises(HTTPException):
                r.add_reply(TOPIC_ID, REPLY, fake_user())


class RepliesRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        mock_replies_service.reset_mock()

    def test_addReply_returnsCorrectMsg_whenUserHasAccessToTopic(self):
        # arrange
        mock_topics_service.exists = True
        mock_replies_service.can_user_access_topic_content = (True, 'OK')
        mock_replies_service.create_reply.return_value = REPLY_ID

        expected = f'Reply with ID {REPLY_ID} successfully added'

        # act
        result = replies_router.add_reply(topic_id=TOPIC_ID, reply=reply,
                                          current_user=fake_user())

        # assert
        self.assertEqual(expected, result)

    def test_raisesHTTPException_statusCode404_whenTopicNotExists(self):
        # arrange
        mock_topics_service.exists = False

        reply_data = reply.model_dump()  # Assuming REPLY.model_dump converts to a serializable format

        with self.assertRaises(HTTPException) as excinfo:
            response = client.post("/topics/{TOPIC_ID}/replies", json={"REPLY": reply_data})

        # Assert status code within the context manager
        self.assertEqual(excinfo.exception.status_code, 404)

        # Assert detail message (optional)
        self.assertEqual(excinfo.exception.detail, "No such topic")

    def test_raisesHTTPException_statusCode403_whenUsedNotHasAccessToTopic(self):
        pass
