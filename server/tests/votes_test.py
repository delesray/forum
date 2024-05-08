import unittest
from unittest.mock import Mock, patch
from routers import votes as votes_router
from routers.votes import HTTPException
from tests.test_utils import REPLY_ID, TOPIC_ID, fake_user, VOTE_TYPE_STR, NEW_VOTE_TYPE


class VotesRouter_Should(unittest.TestCase):

    def test_getAllVotesForReply_raises404_ifNoSuchTopic(self):
        with patch('routers.votes.topic_exists') as mock_t_exists:
            mock_t_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                votes_router.get_all_votes_for_reply_by_type(
                    reply_id=REPLY_ID, topic_id=TOPIC_ID, type=VOTE_TYPE_STR, current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such topic', ex.exception.detail)

    def test_getAllVotesForReply_raises404_ifTopicExistsAndNoSuchReply(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists:
            mock_t_exists.return_value = False
            mock_r_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                votes_router.get_all_votes_for_reply_by_type(
                    reply_id=REPLY_ID, topic_id=TOPIC_ID, type=VOTE_TYPE_STR, current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such reply in this topic',
                                 ex.exception.detail)

    def test_getAllVotesForReply_raises403_ifTopicExistsReplyExists_userHasNoAccess(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
            patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access:
            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')

            with self.assertRaises(HTTPException) as ex:
                votes_router.get_all_votes_for_reply_by_type(
                    reply_id=REPLY_ID, topic_id=TOPIC_ID, type=VOTE_TYPE_STR, current_user=fake_user())

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('You don\'t have permissions to post, modify replies or vote in this topic',
                                 ex.exception.detail)

    def test_getAllVotesForReply_returnsTotalVotesForType_ifTopicExistsReplyExists_userHasAccess(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access, \
                patch('routers.votes.votes_services.get_all') as mock_get_votes:

            fake_votes_total = 5
            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_get_votes.return_value = fake_votes_total

            expected = {f'Total {VOTE_TYPE_STR}votes': fake_votes_total}

            actual = votes_router.get_all_votes_for_reply_by_type(
                reply_id=REPLY_ID, topic_id=TOPIC_ID, type=VOTE_TYPE_STR, current_user=fake_user())

            self.assertEqual(expected, actual)

    def test_addOrSwitch_raises404_ifNoSuchTopic(self):
        with patch('routers.votes.topic_exists') as mock_exists:
            mock_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                votes_router.add_or_switch(
                    type=VOTE_TYPE_STR, reply_id=REPLY_ID, topic_id=TOPIC_ID, current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such topic', ex.exception.detail)

    def test_addOrSwitch_raises404_ifTopicExistsAndNoSuchReply(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists:
            mock_t_exists.return_value = True
            mock_r_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                votes_router.add_or_switch(
                    type=VOTE_TYPE_STR, reply_id=REPLY_ID, topic_id=TOPIC_ID, current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such reply in this topic',
                                 ex.exception.detail)

    def test_addOrSwitch_raises403_ifTopicExistsReplyExists_userHasNoAccess(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access:

            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')

            with self.assertRaises(HTTPException) as ex:
                votes_router.add_or_switch(
                    type=VOTE_TYPE_STR, reply_id=REPLY_ID, topic_id=TOPIC_ID, current_user=fake_user())

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('You don\'t have permissions to post, modify replies or vote in this topic',
                                 ex.exception.detail)

    def test_addOrSwitch_returnsVoteAdded_ifTopicExistsReplyExists_userHasAccess_voteNotExists(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access, \
                patch('routers.votes.votes_services.get_vote_with_type') as mock_v_exists, \
                patch('routers.votes.votes_services.add_vote') as mock_add_vote:

            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_v_exists.return_value = None
            mock_add_vote.return_value = True

            expected = f'You {VOTE_TYPE_STR}voted REPLY with ID: {REPLY_ID}'

            actual = votes_router.add_or_switch(
                type=VOTE_TYPE_STR, reply_id=REPLY_ID, topic_id=TOPIC_ID, current_user=fake_user())

            self.assertEqual(expected, actual)

    def test_addOrSwitch_returnsVoteSwitched_ifTopicExistsReplyExists_userHasAccess_voteExists_typeNotChanged(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access, \
                patch('routers.votes.votes_services.get_vote_with_type') as mock_v_exists, \
                patch('routers.votes.votes_services.switch_vote') as mock_switch_vote:

            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_v_exists.return_value = VOTE_TYPE_STR
            mock_switch_vote.return_value = True

            expected = f'''Reply already {
                VOTE_TYPE_STR}voted. Choose different type to switch it'''

            actual = votes_router.add_or_switch(
                type=VOTE_TYPE_STR, reply_id=REPLY_ID, topic_id=TOPIC_ID, current_user=fake_user())

            self.assertEqual(expected, actual)

    def test_addOrSwitch_returnsVoteSwitched_ifTopicExistsReplyExists_userHasAccess_voteExists_typeChanged(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access, \
                patch('routers.votes.votes_services.get_vote_with_type') as mock_v_exists, \
                patch('routers.votes.votes_services.switch_vote') as mock_switch_vote:

            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (True, 'OK')
            mock_v_exists.return_value = VOTE_TYPE_STR
            mock_switch_vote.return_value = True

            expected = f'Vote switched to {NEW_VOTE_TYPE}vote'

            actual = votes_router.add_or_switch(
                type=NEW_VOTE_TYPE, reply_id=REPLY_ID, topic_id=TOPIC_ID, current_user=fake_user())

            self.assertEqual(expected, actual)

    def test_removeVote_raises404_ifNoSuchTopic(self):
        with patch('routers.votes.topic_exists') as mock_exists:
            mock_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                votes_router.remove_vote(
                    topic_id=TOPIC_ID, reply_id=REPLY_ID, current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such topic', ex.exception.detail)

    def test_removeVote_raises404_ifTopicExistsAndNoSuchReply(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists:
            mock_t_exists.return_value = True
            mock_r_exists.return_value = False

            with self.assertRaises(HTTPException) as ex:
                votes_router.remove_vote(
                    topic_id=TOPIC_ID, reply_id=REPLY_ID, current_user=fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('No such reply in this topic',
                                 ex.exception.detail)

    def test_removeVote_raises403_ifTopicExistsReplyExists_userHasNoAccess(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access:

            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (
                False, 'You don\'t have permissions to post, modify replies or vote in this topic')

            with self.assertRaises(HTTPException) as ex:
                votes_router.remove_vote(
                    topic_id=TOPIC_ID, reply_id=REPLY_ID, current_user=fake_user())

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('You don\'t have permissions to post, modify replies or vote in this topic',
                                 ex.exception.detail)

    def test_removeVote_returnsNone_whenVoteDeleted(self):
        with patch('routers.votes.topic_exists') as mock_t_exists, \
                patch('routers.votes.reply_exists') as mock_r_exists, \
                patch('routers.votes.can_user_access_topic_content') as mock_access:

            mock_t_exists.return_value = True
            mock_r_exists.return_value = True
            mock_access.return_value = (True, 'OK')

            expected = None

            actual = votes_router.remove_vote(
                topic_id=TOPIC_ID, reply_id=REPLY_ID, current_user=fake_user())

            self.assertEqual(expected, actual)
