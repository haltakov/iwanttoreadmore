import unittest
import os
import json
from unittest import mock
from moto import mock_dynamodb2
from iwanttoreadmore.handlers.handlers_vote import (
    add_vote,
    add_vote_and_redirect,
    get_votes_for_user,
    get_votes_for_project,
)
from tests.data.data_test_vote import (
    create_votes_table,
    create_test_votes_data,
    get_expected_votes_data,
)
from iwanttoreadmore.models.user import User
from iwanttoreadmore.models.vote_history import VoteHistory
from tests.helpers import remove_table, create_cookie_parameter, delete_cookie_parameter


def add_ip_address(event):
    if "headers" not in event:
        event["headers"] = dict()
    event["headers"]["Client-Ip"] = "192.168.0.1"
    return event


@mock_dynamodb2
class VoteHandlersTestCase(unittest.TestCase):
    def setUp(self):
        """
        Create a votes table and populate it with example data
        """
        os.environ["VOTES_TABLE"] = "iwanttoreadmore-votes-test"

        self.votes_table = create_votes_table(os.environ["VOTES_TABLE"])
        create_test_votes_data(self.votes_table)
        create_cookie_parameter()

    def tearDown(self):
        remove_table(os.environ["VOTES_TABLE"])
        delete_cookie_parameter()

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "is_account_public", lambda _, __: True)
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

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "is_account_public", lambda _, __: False)
    def test_get_votes_for_user_private(self):
        event_1 = dict(
            pathParameters=dict(user="user_1"),
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        response_1 = get_votes_for_user(event_1, None)

        event_2 = dict(
            pathParameters=dict(user="user_2"),
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        response_2 = get_votes_for_user(event_2, None)

        self.assertEqual(
            json.dumps(get_expected_votes_data("user_1")), response_1["body"]
        )
        self.assertEqual(json.dumps([]), response_2["body"])

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "is_account_public", lambda _, __: True)
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

        expected_data_user_4 = [
            dict(
                topic="topic_xxx",
                project_name="project_x",
                vote_count=2,
                last_vote="9999",
            ),
        ]

        # Check existing topic
        event_1 = add_ip_address(
            dict(
                pathParameters=dict(
                    user="user_2", project="project_c", topic="topic_ddd"
                )
            )
        )
        response_1 = vote_handler(event_1, None)
        event_2 = add_ip_address(dict(pathParameters=dict(user="user_2")))
        response_2 = get_votes_for_user(event_2, None)

        self.assertEqual(expected_return_code, response_1["statusCode"])
        self.assertEqual(200, response_2["statusCode"])
        self.assertEqual(json.dumps(expected_data_user_2), response_2["body"])

        # Check non-existing topic
        event_3 = add_ip_address(
            dict(
                pathParameters=dict(
                    user="user_3", project="project_x", topic="topic_xxx"
                )
            )
        )
        response_3 = vote_handler(event_3, None)
        event_4 = add_ip_address(dict(pathParameters=dict(user="user_3")))
        response_4 = get_votes_for_user(event_4, None)

        self.assertEqual(expected_return_code, response_3["statusCode"])
        self.assertEqual(200, response_4["statusCode"])
        self.assertEqual(json.dumps(expected_data_user_3), response_4["body"])

        # Check uppercase letters
        event_5 = add_ip_address(
            dict(
                pathParameters=dict(
                    user="UseR_3", project="ProJect_X", topic="ToPiC_xXX"
                )
            )
        )
        response_5 = vote_handler(event_5, None)
        event_6 = add_ip_address(dict(pathParameters=dict(user="user_3")))
        response_6 = get_votes_for_user(event_6, None)

        self.assertEqual(expected_return_code, response_5["statusCode"])
        self.assertEqual(200, response_6["statusCode"])
        self.assertEqual(json.dumps(expected_data_user_4), response_6["body"])

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "is_account_public", lambda _, __: True)
    @mock.patch.object(VoteHistory, "__init__", lambda _: None)
    @mock.patch.object(VoteHistory, "check_ip_voted", lambda _, __, ___, ____: False)
    @mock.patch.object(VoteHistory, "add_vote_history", lambda _, __, ___, ____: None)
    @mock.patch("time.time", return_value=9999)
    def test_add_vote(self, _):
        self.add_vote_helper(add_vote, 200)

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "is_account_public", lambda _, __: True)
    @mock.patch.object(VoteHistory, "__init__", lambda _: None)
    @mock.patch.object(VoteHistory, "check_ip_voted", lambda _, __, ___, ____: False)
    @mock.patch.object(VoteHistory, "add_vote_history", lambda _, __, ___, ____: None)
    @mock.patch.object(
        User,
        "get_user_by_username",
        lambda _, __: dict(voted_message=None, voted_redirect=None),
    )
    @mock.patch("time.time", return_value=9999)
    def test_add_vote_and_redirect(self, _):
        self.add_vote_helper(add_vote_and_redirect, 302)


if __name__ == "__main__":
    unittest.main()
