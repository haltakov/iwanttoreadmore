import unittest
import os
from unittest import mock
from moto import mock_dynamodb2
from iwanttoreadmore.models.vote import Vote, get_topic_key
from tests.data.data_test_vote import (
    create_votes_table,
    create_test_votes_data,
    get_expected_votes_data,
)
from tests.helpers import remove_table


@mock_dynamodb2
class VoteTestCase(unittest.TestCase):
    def setUp(self):
        """
        Create a votes table and populate it with example data
        """
        os.environ["VOTES_TABLE"] = "iwanttoreadmore-votes-test"

        self.votes_table = create_votes_table(os.environ["VOTES_TABLE"])
        create_test_votes_data(self.votes_table)

    def tearDown(self):
        remove_table(os.environ["VOTES_TABLE"])

    def test_get_topic_key(self):
        self.assertEqual("project_a/topic_aaa", get_topic_key("project_a", "topic_aaa"))

    def test_get_votes_for_user(self):
        vote = Vote()
        self.assertEqual(
            get_expected_votes_data("user_1"), vote.get_votes_for_user("user_1")
        )
        self.assertEqual(
            get_expected_votes_data("user_2"), vote.get_votes_for_user("user_2")
        )
        self.assertEqual([], vote.get_votes_for_user("user_3"))

    def test_get_votes_for_project(self):
        vote = Vote()
        self.assertEqual(
            get_expected_votes_data("user_1", "project_a"),
            vote.get_votes_for_project("user_1", "project_a"),
        )
        self.assertEqual(
            get_expected_votes_data("user_1", "project_b"),
            vote.get_votes_for_project("user_1", "project_b"),
        )
        self.assertEqual(
            get_expected_votes_data("user_2", "project_c"),
            vote.get_votes_for_project("user_2", "project_c"),
        )
        self.assertEqual([], vote.get_votes_for_project("user_2", "project_y"))
        self.assertEqual([], vote.get_votes_for_project("user_3", "project_z"))

    def test_get_vote_count(self):
        vote = Vote()

        # Test existing topics
        self.assertEqual(10, vote.get_vote_count("user_1", "project_a/topic_aaa"))
        self.assertEqual(20, vote.get_vote_count("user_1", "project_a/topic_bbb"))
        self.assertEqual(30, vote.get_vote_count("user_1", "project_b/topic_ccc"))
        self.assertEqual(40, vote.get_vote_count("user_2", "project_c/topic_ddd"))

        # Test non-existing topics
        self.assertEqual(0, vote.get_vote_count("user_1", "project_a/topic_xxx"))
        self.assertEqual(0, vote.get_vote_count("user_1", "project_x/topic_xxx"))
        self.assertEqual(0, vote.get_vote_count("user_x", "project_x/topic_xxx"))
        self.assertEqual(0, vote.get_vote_count("user_2", "project_a/topic_aaa"))
        self.assertEqual(0, vote.get_vote_count("user_2", "project_c/topic_aaa"))

    @mock.patch("time.time", return_value=9999)
    def test_set_vote_count(self, _):
        vote = Vote()

        # Check votes count set correctly
        self.assertEqual(10, vote.get_vote_count("user_1", "project_a/topic_aaa"))
        vote.set_vote_count("user_1", "project_a/topic_aaa", 100)
        self.assertEqual(100, vote.get_vote_count("user_1", "project_a/topic_aaa"))

        # Check timestamp set correctly
        votes_user_1 = vote.get_votes_for_user("user_1")
        self.assertEqual("9999", votes_user_1[0]["last_vote"])

    @mock.patch("time.time", return_value=9999)
    def test_create_topic(self, _):
        expected_votes_user_2 = get_expected_votes_data("user_2") + [
            dict(
                topic="topic_eee",
                project_name="project_d",
                vote_count=1,
                last_vote="9999",
            ),
        ]

        expected_votes_user_3 = [
            dict(
                topic="topic_fff",
                project_name="project_e",
                vote_count=1,
                last_vote="9999",
            ),
        ]

        vote = Vote()
        vote.create_topic("user_2", "topic_eee", "project_d")
        vote.create_topic("user_3", "topic_fff", "project_e")

        self.assertEqual(expected_votes_user_2, vote.get_votes_for_user("user_2"))
        self.assertEqual(expected_votes_user_3, vote.get_votes_for_user("user_3"))

    def test_add_vote(self):
        vote = Vote()

        # Test existing topic
        vote.add_vote("user_1", "project_a", "topic_aaa")
        self.assertEqual(11, vote.get_vote_count("user_1", "project_a/topic_aaa"))
        vote.add_vote("user_1", "project_a", "topic_aaa")
        self.assertEqual(12, vote.get_vote_count("user_1", "project_a/topic_aaa"))

        # Test new topic
        vote.add_vote("user_1", "project_a", "topic_xxx")
        self.assertEqual(1, vote.get_vote_count("user_1", "project_a/topic_xxx"))
        vote.add_vote("user_1", "project_a", "topic_xxx")
        self.assertEqual(2, vote.get_vote_count("user_1", "project_a/topic_xxx"))

    def test_set_vote_hidden(self):
        vote = Vote()

        vote.set_vote_hidden("user_1", "project_a", "topic_bbb", True)
        self.assertTrue(vote.get_votes_for_project("user_1", "project_a")[0]["hidden"])

        vote.set_vote_hidden("user_1", "project_b", "topic_ccc", False)
        self.assertFalse(vote.get_votes_for_project("user_1", "project_b")[0]["hidden"])

    def test_delete_vote(self):
        vote = Vote()

        vote.delete_vote("user_1", "project_b", "topic_ccc")
        self.assertEqual([], vote.get_votes_for_project("user_1", "project_b"))


if __name__ == "__main__":
    unittest.main()
