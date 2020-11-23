import unittest
import os
import json
from unittest import mock
from moto import mock_dynamodb2
from iwanttoreadmore.handlers.vote import (
    add_vote,
    add_vote_and_redirect,
    get_votes_for_user,
    get_votes_for_project,
)
from tests.helpers import (
    create_votes_table,
    create_test_votes_data,
    remove_table,
    get_expected_votes_data,
)


@mock_dynamodb2
class VoteHandlersTestCase(unittest.TestCase):
    def setUp(self):
        """
        Create a votes table and populate it with example data
        """
        os.environ["VOTES_TABLE"] = "iwanttoreadmore-votes-test"

        self.votes_table = create_votes_table(os.environ["VOTES_TABLE"])
        create_test_votes_data(self.votes_table)

    def tearDown(self):
        remove_table(os.environ["VOTES_TABLE"])

    def test_get_votes_for_user(self):
        event_1 = dict(pathParameters=dict(user="user_1"))
        response_1 = get_votes_for_user(event_1, None)

        event_2 = dict(pathParameters=dict(user="user_2"))
        response_2 = get_votes_for_user(event_2, None)

        event_3 = dict(pathParameters=dict(user="user_3"))
        response_3 = get_votes_for_user(event_3, None)

        self.assertEqual(200, response_1["statusCode"])
        self.assertEqual(200, response_2["statusCode"])
        self.assertEqual(200, response_3["statusCode"])

        self.assertEqual(
            json.dumps(get_expected_votes_data("user_1")), response_1["body"]
        )
        self.assertEqual(
            json.dumps(get_expected_votes_data("user_2")), response_2["body"]
        )
        self.assertEqual(json.dumps([]), response_3["body"])

    def test_get_votes_for_project(self):
        event_1 = dict(pathParameters=dict(user="user_1", project="project_a"))
        response_1 = get_votes_for_project(event_1, None)

        event_2 = dict(pathParameters=dict(user="user_1", project="project_b"))
        response_2 = get_votes_for_project(event_2, None)

        event_3 = dict(pathParameters=dict(user="user_2", project="project_c"))
        response_3 = get_votes_for_project(event_3, None)

        event_4 = dict(pathParameters=dict(user="user_2", project="project_y"))
        response_4 = get_votes_for_project(event_4, None)

        event_5 = dict(pathParameters=dict(user="user_3", project="project_z"))
        response_5 = get_votes_for_project(event_5, None)

        self.assertEqual(200, response_1["statusCode"])
        self.assertEqual(200, response_2["statusCode"])
        self.assertEqual(200, response_3["statusCode"])
        self.assertEqual(200, response_4["statusCode"])
        self.assertEqual(200, response_5["statusCode"])

        self.assertEqual(
            json.dumps(get_expected_votes_data("user_1", "project_a")),
            response_1["body"],
        )
        self.assertEqual(
            json.dumps(get_expected_votes_data("user_1", "project_b")),
            response_2["body"],
        )
        self.assertEqual(
            json.dumps(get_expected_votes_data("user_2", "project_c")),
            response_3["body"],
        )
        self.assertEqual(json.dumps([]), response_4["body"])
        self.assertEqual(json.dumps([]), response_5["body"])

    def add_vote_helper(self, vote_handler, expected_return_code):
        expected_data_user_2 = get_expected_votes_data("user_2")
        expected_data_user_2[0]["vote_count"] += 1
        expected_data_user_2[0]["last_vote"] = "9999"

        expected_data_user_3 = [
            dict(
                topic="topic_xxx",
                project_name="project_x",
                vote_count=1,
                last_vote="9999",
            ),
        ]

        # Check existing topic
        event_1 = dict(
            pathParameters=dict(user="user_2", project="project_c", topic="topic_ddd")
        )
        response_1 = vote_handler(event_1, None)
        event_2 = dict(pathParameters=dict(user="user_2"))
        response_2 = get_votes_for_user(event_2, None)

        self.assertEqual(expected_return_code, response_1["statusCode"])
        self.assertEqual(200, response_2["statusCode"])
        self.assertEqual(json.dumps(expected_data_user_2), response_2["body"])

        # Check non-existing topic
        event_3 = dict(
            pathParameters=dict(user="user_3", project="project_x", topic="topic_xxx")
        )
        response_3 = vote_handler(event_3, None)
        event_4 = dict(pathParameters=dict(user="user_3"))
        response_4 = get_votes_for_user(event_4, None)

        self.assertEqual(expected_return_code, response_3["statusCode"])
        self.assertEqual(200, response_4["statusCode"])
        self.assertEqual(json.dumps(expected_data_user_3), response_4["body"])

    @mock.patch("time.time", return_value=9999)
    def test_add_vote(self, time):
        self.add_vote_helper(add_vote, 200)

    @mock.patch("time.time", return_value=9999)
    def test_add_vote_and_redirect(self, time):
        self.add_vote_helper(add_vote_and_redirect, 302)


if __name__ == "__main__":
    unittest.main()
