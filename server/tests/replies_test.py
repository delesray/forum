import unittest
from unittest.mock import patch
from routers import replies as replies_router
from routers.replies import HTTPException
from tests.test_utils import TOPIC_ID, REPLY_ID, fake_user, fake_create_update_reply


reply = fake_create_update_reply(text='sometxt')
empty_reply = fake_create_update_reply(text='')


class RepliesRouter_Should(unittest.TestCase):

    def test_addReply_returnsCorrectMsg_whenTopicExists_userHasAccessToTopic(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access, \
                patch('routers.replies.replies_services.create_reply') as mock_create_reply:
            mock_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_create_reply.return_value = REPLY_ID

            expected = f'Reply with ID {REPLY_ID} successfully added'

            actual = replies_router.add_reply(topic_id=TOPIC_ID, reply=reply,
                                              current_user=fake_user())

            self.assertEqual(expected, actual)

    def test_addReply_raises404_whenTopicNotExists(self):
        with patch('routers.replies.exists') as mock_exists:
            mock_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                replies_router.add_reply(topic_id=TOPIC_ID, reply=reply,
                                         current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such topic', ex.exception.detail)

    def test_addReply_raises403_whenUserNotHasAccessToTopic(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access:
            mock_exists.return_value = True
            mock_access.return_value = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')

            with self.assertRaises(HTTPException) as ex:
                replies_router.add_reply(topic_id=TOPIC_ID, reply=reply,
                                         current_user=fake_user())

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual(
                    'You don\'t have permissions to post, modify replies or vote in this topic', ex.exception.detail)
                
    def test_addReply_raises400_whenReplyEmpty(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access:
            mock_exists.return_value = True
            mock_access.return_value = (True, 'OK')

            with self.assertRaises(HTTPException) as ex:
                replies_router.add_reply(topic_id=TOPIC_ID, reply=empty_reply,
                                              current_user=fake_user())

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual('Reply text is required', ex.exception.detail)

    def test_editReply_returnsCorrectMsg_whenTopicExists_userHasAccessToTopic(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access, \
                patch('routers.replies.replies_services.update_reply') as mock_update_reply:
            mock_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_update_reply.return_value = True

            expected = f'Reply with ID {REPLY_ID} successfully updated'

            actual = replies_router.edit_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID, update=reply,
                                               current_user=fake_user())

            self.assertEqual(expected, actual)

    def test_editReply_raises404_whenTopicNotExists(self):
        with patch('routers.replies.exists') as mock_exists:
            mock_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                replies_router.edit_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID, update=reply,
                                          current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such topic', ex.exception.detail)

    def test_editReply_raises404_whenReplyNotExists(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.get_reply_by_id') as mock_get_reply:
            mock_exists.return_value = True
            mock_get_reply.return_value = None

            with self.assertRaises(HTTPException) as ex:
                replies_router.edit_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID, update=reply,
                                          current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)

    def test_editReply_raises403_whenUsedNotHasAccessToTopic(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access, \
                patch('routers.replies.get_reply_by_id') as mock_get_reply:
            mock_exists.return_value = True
            mock_get_reply.return_value = REPLY_ID
            mock_access.return_value = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')

            with self.assertRaises(HTTPException) as ex:
                replies_router.edit_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID, update=reply,
                                          current_user=fake_user())

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual(
                    'You don\'t have permissions to post, modify replies or vote in this topic', ex.exception.detail)
                
    def test_editReply_raises400_whenReplyEmpty(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access:
            mock_exists.return_value = True
            mock_access.return_value = (True, 'OK')

            with self.assertRaises(HTTPException) as ex:
                replies_router.edit_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID, update=empty_reply,
                                               current_user=fake_user())

                self.assertEqual('Reply text is required', ex.exception.detail)
                self.assertEqual(400, ex.exception.status_code)

    def test_deleteReply_returnsCorrectMsg_whenTopicExists_userHasAccessToTopic(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access, \
                patch('routers.replies.replies_services.delete_reply') as mock_delete_reply:
            mock_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_delete_reply.return_value = True

            expected = f'Reply deleted'
            actual = replies_router.delete_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID,
                                                 current_user=fake_user())

            self.assertEqual(expected, actual)

    def test_deleteReply_raises404_whenTopicNotExists(self):
        with patch('routers.replies.exists') as mock_exists:
            mock_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                replies_router.delete_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID,
                                            current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such topic', ex.exception.detail)

    def test_deleteReply_raises404_whenReplyNotExists(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.get_reply_by_id') as mock_get_reply:
            mock_exists.return_value = True
            mock_get_reply.return_value = None

            with self.assertRaises(HTTPException) as ex:
                replies_router.delete_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID,
                                            current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)

    def test_deleteReply_raises403_whenUsedNotHasAccessToTopic(self):
        with patch('routers.replies.exists') as mock_exists, \
                patch('routers.replies.can_user_access_topic_content') as mock_access, \
                patch('routers.replies.get_reply_by_id') as mock_get_reply:
            mock_exists.return_value = True
            mock_get_reply.return_value = REPLY_ID
            mock_access.return_value = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')

            with self.assertRaises(HTTPException) as ex:
                replies_router.delete_reply(topic_id=TOPIC_ID, reply_id=REPLY_ID,
                                            current_user=fake_user())

            self.assertEqual(403, ex.exception.status_code)
            self.assertEqual(
                'You don\'t have permissions to post, modify replies or vote in this topic', ex.exception.detail)
