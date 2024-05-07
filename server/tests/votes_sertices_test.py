import unittest
from unittest.mock import patch
from services import votes_services as votes
from tests.test_utils import REPLY_ID, USER_ID, VOTE_TYPE_INT, VOTE_TYPE_STR


class VotesServices_Should(unittest.TestCase):
    def test_getAll_returnsNumberOfVotes_ifVotes(self):
        with patch('services.votes_services.read_query') as get_all_votes_per_reply:
            total_votes = [(5,)]
            get_all_votes_per_reply.return_value = total_votes

            expected = total_votes[0][0]

            result = votes.get_all(reply_id=REPLY_ID, type=VOTE_TYPE_STR)

            self.assertEqual(expected, result)

    def test_getAll_returnsNone_ifNotVotes(self):
        with patch('services.votes_services.read_query') as get_all_votes_per_reply:
            total_votes = []
            get_all_votes_per_reply.return_value = total_votes

            expected = None

            result = votes.get_all(reply_id=REPLY_ID, type=VOTE_TYPE_STR)

            self.assertEqual(expected, result)

    def test_voteExists_returnsTrue_ifVote(self):
        with patch('services.votes_services.read_query') as get_vote_type:

            get_vote_type.return_value = [(1,)]

            expected = True

            result = votes.vote_exists(reply_id=REPLY_ID, user_id=USER_ID)

            self.assertEqual(expected, result)

    def test_voteExists_returnsFalse_ifNotVote(self):
        with patch('services.votes_services.read_query') as get_vote_type:

            get_vote_type.return_value = []

            expected = False

            result = votes.vote_exists(reply_id=REPLY_ID, user_id=USER_ID)

            self.assertEqual(expected, result)
