import unittest
import os
from decimal import Decimal
from unittest import mock
from moto import mock_dynamodb2
from iwanttoreadmore.models.vote_history import VoteHistory
from tests.data.data_test_vote_history import (
    create_vote_history_table,
    create_test_vote_history_data,
)
from tests.helpers import remove_table


@mock_dynamodb2
class VoteHistoryTestCase(unittest.TestCase):
    def setUp(self):
        """
        Create a vote history table and populate it with example data
        """
        os.environ["VOTES_HISTORY_TABLE"] = "iwanttoreadmore-votes-history-test"

        self.vote_history_table = create_vote_history_table(
            os.environ["VOTES_HISTORY_TABLE"]
        )
        create_test_vote_history_data(self.vote_history_table)

    def tearDown(self):
        remove_table(os.environ["VOTES_HISTORY_TABLE"])

    def test_get_vote_history(self):
        vote_history = VoteHistory()

        # Positive cases
        self.assertEqual(
            [1111, 2222], vote_history.get_vote_history("user_1", "project_a/topic_aaa")
        )
        self.assertEqual(
            [3333], vote_history.get_vote_history("user_1", "project_a/topic_bbb")
        )

        # Negative cases
        self.assertEqual(
            [], vote_history.get_vote_history("user_2", "project_a/topic_aaa")
        )
        self.assertEqual(
            [], vote_history.get_vote_history("user_1", "project_a/topic_ccc")
        )

    @mock.patch("time.time", return_value=9999)
    def test_add_vote_history(self, _):
        vote_history = VoteHistory()

        # Invalid vote
        vote_history.add_vote_history("user_1", "project_a/topic_aaa", "192.168.0.1")
        self.assertEqual(
            [Decimal(1111), Decimal(2222)],
            vote_history.get_vote_history("user_1", "project_a/topic_aaa"),
        )

        # Valid vote
        vote_history.add_vote_history("user_1", "project_a/topic_aaa", "192.168.0.3")
        self.assertEqual(
            [Decimal(1111), Decimal(2222), Decimal(9999)],
            vote_history.get_vote_history("user_1", "project_a/topic_aaa"),
        )

        # New vote
        vote_history.add_vote_history("user_1", "project_a/topic_ccc", "192.168.0.3")
        self.assertEqual(
            [Decimal(9999)],
            vote_history.get_vote_history("user_1", "project_a/topic_ccc"),
        )

    def test_check_ip_voted(self):
        vote_history = VoteHistory()

        # Valid vote
        self.assertFalse(
            vote_history.check_ip_voted("user_1", "project_a/topic_aaa", "192.168.0.3")
        )

        # Invalid vote
        self.assertTrue(
            vote_history.check_ip_voted("user_1", "project_a/topic_aaa", "192.168.0.1")
        )

        # New vote
        self.assertFalse(
            vote_history.check_ip_voted("user_1", "project_a/topic_ccc", "192.168.0.1")
        )


if __name__ == "__main__":
    unittest.main()
