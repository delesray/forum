import unittest
from unittest.mock import Mock, patch
from data.models.reply import ReplyResponse, ReplyCreateUpdate
from services import replies_services as replies


# REPLY
TEXT = 'sometext'
USERNAME = 'someuser'
TOPIC_ID = 1

USER_ID = 1

# pagination params
PAGE = 1
SIZE = 1


def create_reply(reply_id):
    return ReplyResponse(
        reply_id=reply_id,
        text=TEXT,
        username=USERNAME,
        topic_id=TOPIC_ID)


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


class RepliesServices_Should(unittest.TestCase):

    def test_getAll_returnsListOfReplyResponseObjects_whenRepliesExist(self):
        with patch('services.replies_services.read_query') as get_all_replies:
            reply_id_1, reply_id_2, reply_id_3 = 1, 2, 3
            get_all_replies.return_value = [(reply_id_1, TEXT, USERNAME, TOPIC_ID),
                                            (reply_id_2, TEXT, USERNAME, TOPIC_ID),
                                            (reply_id_3, TEXT, USERNAME, TOPIC_ID)]

            expected = [create_reply(reply_id_1),
                        create_reply(reply_id_2),
                        create_reply(reply_id_3)]

            result = replies.get_all(topic_id=TOPIC_ID, page=PAGE, size=SIZE)

            self.assertEqual(expected, result)

    def test_getAll_returnsEmptyList_whenNoReplies(self):
        with patch('services.replies_services.read_query') as get_all_replies:
            get_all_replies.return_value = []

            expected = []

            result = replies.get_all(topic_id=TOPIC_ID, page=PAGE, size=SIZE)

            self.assertEqual(expected, result)

    def test_getById_returnsReplyResponseObject_whenExists(self):
        with patch('services.replies_services.read_query') as get_reply_by_id:
            reply_id = 1
            get_reply_by_id.return_value = [
                (reply_id, TEXT, USERNAME, TOPIC_ID)]

            expected = create_reply(reply_id)

            result = replies.get_by_id(id=reply_id)

            self.assertEqual(expected, result)

    def test_getById_returnsNone_whenNoSuchReply(self):
        with patch('services.replies_services.read_query') as get_reply_by_id:
            reply_id = 1

            get_reply_by_id.return_value = []

            expected = None
            result = replies.get_by_id(id=reply_id)

            self.assertEqual(expected, result)

    def test_createReply_returnsReplyId(self):
        with patch('services.replies_services.insert_query') as add_reply:
            reply_id = 1

            add_reply.return_value = reply_id

            expected = 1
            result = replies.create_reply(topic_id=TOPIC_ID,
                                          reply=ReplyCreateUpdate(text='text'), user_id=USER_ID)

            self.assertEqual(expected, result)

    # cat is private, no write access
    def test_canUserAccessTopicContent_returnsFalseAndCorrectMsg_whenCategoryPrivateAndNotHasWriteAccess(self):
        with patch('services.replies_services.get_cat_by_id') as mock_get_cat, \
                patch('services.replies_services.has_write_access') as mock_has_write_access:

            mock_category = fake_category(is_private=True)
            mock_get_cat.return_value = mock_category

            mock_has_write_access.return_value = False

            expected = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')
            result = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, result)

    # cat is private, has write access, topic locked
    def test_CanUserAccessTopicContent_returnsFalseAndCorrectMsg_whenTopicLocked(self):
        with patch('services.replies_services.get_cat_by_id') as mock_get_cat, \
                patch('services.replies_services.has_write_access') as mock_has_write_access, \
                patch('services.replies_services.get_topic_by_id') as mock_get_topic:

            mock_category = fake_category(is_private=True)
            mock_get_cat.return_value = mock_category
            mock_has_write_access.return_value = True
            mock_topic = fake_topic(status='locked')
            mock_get_topic.return_value = mock_topic

            expected = (False, 'This topic is read-only')
            result = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, result)

    # cat is private, has_write_access, topic open
    def test_CanUserAccessTopicContent_returnsTrueAndOk_whenCatPrivate_hasWriteAccess(self):
        with patch('services.replies_services.get_cat_by_id') as mock_get_cat, \
                patch('services.replies_services.has_write_access') as mock_has_write_access, \
                patch('services.replies_services.get_topic_by_id') as mock_get_topic:

            mock_category = fake_category(is_private=False)
            mock_get_cat.return_value = mock_category

            mock_has_write_access.return_value = True

            mock_topic = fake_topic(status='open')
            mock_get_topic.return_value = mock_topic

            expected = (True, 'OK')
            result = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, result)

    # cat not private, topic not locked
    def test_CanUserAccessTopicContent_returnsTrueAndOk_whenCatNotPrivate_TopicNotLocked(self):
        with patch('services.replies_services.get_cat_by_id') as mock_get_cat, \
                patch('services.replies_services.has_write_access') as mock_has_write_access, \
                patch('services.replies_services.get_topic_by_id') as mock_get_topic:

            mock_category = fake_category(is_private=False)
            mock_get_cat.return_value = mock_category

            mock_topic = fake_topic(status='open')
            mock_get_topic.return_value = mock_topic

            mock_has_write_access.return_value = False

            expected = (True, 'OK')
            result = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, result)

    # cat not private, topic locked
    def test_CanUserAccessTopicContent_returnsFalseAndCorrectMsg_whenCatNotPrivate_TopicLocked(self):
        with patch('services.replies_services.get_cat_by_id') as mock_get_cat, \
                patch('services.replies_services.has_write_access') as mock_has_write_access, \
                patch('services.replies_services.get_topic_by_id') as mock_get_topic:

            mock_category = fake_category(is_private=False)
            mock_get_cat.return_value = mock_category

            mock_topic = fake_topic(status='locked')
            mock_get_topic.return_value = mock_topic

            mock_has_write_access.return_value = False

            expected = (False, 'This topic is read-only')
            result = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, result)
