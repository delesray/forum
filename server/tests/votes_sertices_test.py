import unittest
from unittest.mock import patch
from services import votes_services as votes
from tests.test_utils import REPLY_ID, USER_ID, VOTE_TYPE_INT, VOTE_TYPE_STR


class VotesServices_Should(unittest.TestCase):
    def test_getAll_returnsNumberOfVotes_ifVotes(self):
        with patch('services.votes_services.read_query') as mock_get_all_votes_per_reply:
            total_votes = [(5,)]
            mock_get_all_votes_per_reply.return_value = total_votes

            expected = total_votes[0][0]

            actual = votes.get_all(reply_id=REPLY_ID, type=VOTE_TYPE_STR)

            self.assertEqual(expected, actual)

    def test_getAll_returnsNone_ifNotVotes(self):
        with patch('services.votes_services.read_query') as mock_get_all_votes_per_reply:
            total_votes = []
            mock_get_all_votes_per_reply.return_value = total_votes

            expected = None

            actual = votes.get_all(reply_id=REPLY_ID, type=VOTE_TYPE_STR)

            self.assertEqual(expected, actual)

    def test_getVoteWithType_returnsVoteType_ifVote(self):
        with patch('services.votes_services.read_query') as mock_get_vote_type:

            mock_get_vote_type.return_value = [(VOTE_TYPE_INT,)]

            expected = VOTE_TYPE_STR

            actual = votes.get_vote_with_type(
                reply_id=REPLY_ID, user_id=USER_ID)

            self.assertEqual(expected, actual)

    def test_getVoteWithType_returnsNone_ifNotVote(self):
        with patch('services.votes_services.read_query') as mock_get_vote_type:

            mock_get_vote_type.return_value = []

            expected = None

            actual = votes.get_vote_with_type(
                reply_id=REPLY_ID, user_id=USER_ID)

            self.assertEqual(expected, actual)
