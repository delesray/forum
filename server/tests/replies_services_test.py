import unittest
from unittest.mock import Mock, patch
from data.models.reply import ReplyResponse, ReplyCreateUpdate
from common.utils import PaginationInfo
from services import replies_services as replies
from tests.test_utils import TOPIC_ID, REPLY_ID, USER_ID, fake_category, fake_topic


# REPLY
TEXT = 'sometext'
USERNAME = 'someuser'

# pagination params
PAGE = 1
SIZE = 1


def create_reply(reply_id):
    return ReplyResponse(
        reply_id=reply_id,
        text=TEXT,
        username=USERNAME,
        topic_id=TOPIC_ID)


class RepliesServices_Should(unittest.TestCase):

    def test_getAll_returnsListOfReplyResponseObjectsPaginationInfoAndLinks_whenRepliesExist(self):
        with patch('services.replies_services.read_query') as mock_get_all_replies, \
                patch('services.replies_services.get_pagination_info') as mock_pagination_info, \
                patch('services.replies_services.create_links') as mock_create_links:
            reply_id_1, reply_id_2, reply_id_3 = 1, 2, 3
            mock_get_all_replies.return_value = [(reply_id_1, TEXT, USERNAME, TOPIC_ID),
                                                 (reply_id_2, TEXT,
                                                  USERNAME, TOPIC_ID),
                                                 (reply_id_3, TEXT, USERNAME, TOPIC_ID)]

            mock_pagination_info.return_value = PaginationInfo(total_elements=len(mock_get_all_replies.return_value),
                                                               page=PAGE,
                                                               size=SIZE,
                                                               pages=1)
            request = Mock()
            links = Mock()
            mock_create_links.return_value = links

            expected = [create_reply(reply_id_1), create_reply(reply_id_2), create_reply(reply_id_3)], PaginationInfo(
                total_elements=len(mock_get_all_replies.return_value), page=PAGE, size=SIZE, pages=1), links

            actual = replies.get_all(
                topic_id=TOPIC_ID, request=request, page=PAGE, size=SIZE)

            self.assertEqual(expected, actual)

    def test_getAll_returnsEmptyListPaginationInfoAndLinks_whenNoReplies(self):
        with patch('services.replies_services.read_query') as mock_get_all_replies, \
                patch('services.replies_services.get_pagination_info') as mock_pagination_info, \
                patch('services.replies_services.create_links') as mock_create_links:

            mock_get_all_replies.return_value = []
            mock_pagination_info.return_value = PaginationInfo(total_elements=len(mock_get_all_replies.return_value),
                                                               page=PAGE,
                                                               size=SIZE,
                                                               pages=0)
            request = Mock()
            links = Mock()
            mock_create_links.return_value = links

            expected = [], PaginationInfo(total_elements=0,
                                          page=PAGE,
                                          size=SIZE,
                                          pages=0), links

            actual = replies.get_all(
                topic_id=TOPIC_ID, request=request, page=PAGE, size=SIZE)

            self.assertEqual(expected, actual)

    def test_getById_returnsReplyResponseObject_whenExists(self):
        with patch('services.replies_services.read_query') as mock_get_reply_by_id:
            reply_id = 1
            mock_get_reply_by_id.return_value = [
                (reply_id, TEXT, USERNAME, TOPIC_ID)]

            expected = create_reply(reply_id)

            actual = replies.get_by_id(id=reply_id)

            self.assertEqual(expected, actual)

    def test_getById_returnsNone_whenNoSuchReply(self):
        with patch('services.replies_services.read_query') as mock_get_reply_by_id:
            reply_id = 1

            mock_get_reply_by_id.return_value = []

            expected = None
            actual = replies.get_by_id(id=reply_id)

            self.assertEqual(expected, actual)

    def test_createReply_returnsReplyId(self):
        with patch('services.replies_services.insert_query') as mock_add_reply:
            reply_id = 1

            mock_add_reply.return_value = reply_id

            expected = 1
            actual = replies.create_reply(topic_id=TOPIC_ID,
                                          reply=ReplyCreateUpdate(text='text'), user_id=USER_ID)

            self.assertEqual(expected, actual)

    # cat is private, no write access
    def test_canUserAccessTopicContent_returnsFalseAndCorrectMsg_whenCategoryPrivateAndNotHasWriteAccess(self):
        with patch('services.replies_services.get_cat_by_id') as mock_get_cat, \
                patch('services.replies_services.has_write_access') as mock_has_write_access:

            mock_category = fake_category(is_private=True)
            mock_get_cat.return_value = mock_category

            mock_has_write_access.return_value = False

            expected = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')
            actual = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, actual)

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
            actual = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, actual)

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
            actual = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, actual)

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
            actual = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, actual)

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
            actual = replies.can_user_access_topic_content(TOPIC_ID, USER_ID)

            self.assertEqual(expected, actual)

    def test_replyExists_returnsTrue_ifReply(self):
        with patch('services.replies_services.read_query') as mock_exists:

            mock_exists.return_value = [(1,)]

            expected = True

            actual = replies.exists(reply_id=REPLY_ID, topic_id=TOPIC_ID)

            self.assertEqual(expected, actual)

    def test_replyExists_returnsFalse_ifNotReply(self):
        with patch('services.votes_services.read_query') as mock_get_vote_type:

            mock_get_vote_type.return_value = []

            expected = False

            actual = replies.exists(reply_id=REPLY_ID, topic_id=TOPIC_ID)

            self.assertEqual(expected, actual)
