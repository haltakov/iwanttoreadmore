import unittest
import os
import json
from unittest import mock
from unittest.mock import MagicMock
from moto import mock_dynamodb2
from iwanttoreadmore.handlers.handlers_vote import (
    add_vote,
    add_vote_and_redirect,
    get_votes_for_user,
    get_votes_for_project,
    set_vote_hidden,
    delete_vote,
)
from tests.data.data_test_vote import (
    create_votes_table,
    create_test_votes_data,
    get_expected_votes_data,
)
from iwanttoreadmore.models.user import User
from iwanttoreadmore.models.vote import Vote
from iwanttoreadmore.models.vote_history import VoteHistory
from tests.helpers import remove_table, create_cookie_parameter, delete_cookie_parameter
from iwanttoreadmore.handlers.handler_helpers import create_response


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
    @mock.patch.object(User, "get_user_by_username")
    def test_get_votes_for_user(self, get_user_mock):
        # Define helper functions
        event = lambda user: dict(pathParameters=dict(user=user))
        response = lambda user, svp: create_response(
            200,
            body=json.dumps(
                dict(single_voting_projects=svp, votes=get_expected_votes_data(user),)
            ),
        )

        # Good case #1 (with svp)
        get_user_mock.return_value = dict(
            is_public=True, single_voting_projects=["project_a"]
        )
        self.assertEqual(
            response("user_1", ["project_a"]), get_votes_for_user(event("user_1"), None)
        )

        # Good case #2 (without svp)
        get_user_mock.return_value = dict(is_public=True, single_voting_projects=[])
        self.assertEqual(
            response("user_2", []), get_votes_for_user(event("user_2"), None)
        )

        # Invalid user
        get_user_mock.return_value = None
        self.assertEqual(
            create_response(400, "GET", "Invalid user"),
            get_votes_for_user(event("user_X"), None),
        )

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "get_user_by_username")
    def test_get_votes_for_user_private(self, get_user_mock):
        # Define helper functions
        event = lambda user: dict(
            pathParameters=dict(user=user),
            headers=dict(
                Cookie=f"user={user}&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        response = lambda user: create_response(
            200,
            body=json.dumps(
                dict(single_voting_projects=[], votes=get_expected_votes_data(user),)
            ),
        )

        # Logged in user
        get_user_mock.return_value = dict(is_public=False, single_voting_projects=[])
        self.assertEqual(response("user_1"), get_votes_for_user(event("user_1"), None))

        # Not logged in user
        get_user_mock.return_value = dict(is_public=False, single_voting_projects=[])
        self.assertEqual(
            create_response(400, "GET", "Invalid user"),
            get_votes_for_user(event("user_2"), None),
        )

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "get_user_by_username")
    def test_get_votes_for_project(self, get_user_mock):
        # Define helper functions
        event = lambda user, project: dict(
            pathParameters=dict(user=user, project=project),
        )
        response = lambda user, project, svp: create_response(
            200,
            body=json.dumps(
                dict(
                    single_voting_projects=svp,
                    votes=get_expected_votes_data(user, project),
                )
            ),
        )

        # Good case #1 (with svp)
        get_user_mock.return_value = dict(
            is_public=True, single_voting_projects=["project_a"]
        )
        self.assertEqual(
            response("user_1", "project_a", ["project_a"]),
            get_votes_for_project(event("user_1", "project_a"), None),
        )

        # Good case #2 (without svp)
        get_user_mock.return_value = dict(is_public=True, single_voting_projects=[])
        self.assertEqual(
            response("user_1", "project_b", []),
            get_votes_for_project(event("user_1", "project_b"), None),
        )

        # Invalid project
        self.assertEqual(
            response("user_1", "project_X", []),
            get_votes_for_project(event("user_1", "project_X"), None),
        )

        # Invalid user
        get_user_mock.return_value = None
        self.assertEqual(
            create_response(400, "GET", "Invalid user"),
            get_votes_for_project(event("user_X", "project_X"), None),
        )

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
        self.assertEqual(expected_data_user_2, json.loads(response_2["body"])["votes"])

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
        self.assertEqual(expected_data_user_3, json.loads(response_4["body"])["votes"])

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
        self.assertEqual(expected_data_user_4, json.loads(response_6["body"])["votes"])

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(User, "get_user_by_username", lambda _, __: dict(is_public=True))
    @mock.patch.object(VoteHistory, "__init__", lambda _: None)
    @mock.patch.object(VoteHistory, "check_ip_voted", lambda _, __, ___, ____: False)
    @mock.patch.object(
        VoteHistory, "add_vote_history", lambda _, __, ___, ____, _____: None
    )
    @mock.patch("time.time", return_value=9999)
    def test_add_vote(self, _):
        self.add_vote_helper(add_vote, 200)

    @mock.patch.object(User, "__init__", lambda _: None)
    @mock.patch.object(
        User,
        "get_user_by_username",
        lambda _, __: dict(is_public=True, voted_redirect=None, voted_message=None),
    )
    @mock.patch.object(VoteHistory, "__init__", lambda _: None)
    @mock.patch.object(VoteHistory, "check_ip_voted", lambda _, __, ___, ____: False)
    @mock.patch.object(
        VoteHistory, "add_vote_history", lambda _, __, ___, ____, _____: None
    )
    @mock.patch.object(
        User,
        "get_user_by_username",
        lambda _, __: dict(voted_message=None, voted_redirect=None),
    )
    @mock.patch("time.time", return_value=9999)
    def test_add_vote_and_redirect(self, _):
        self.add_vote_helper(add_vote_and_redirect, 302)

    @mock.patch.object(Vote, "set_vote_hidden")
    def test_set_vote_hidden(self, set_vote_hidden_model):
        # Hide
        event = dict(
            pathParameters=dict(user="user_1", project="project_a", topic="topic_bbb"),
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="1",
        )
        self.assertEqual(200, set_vote_hidden(event, None)["statusCode"])
        set_vote_hidden_model.assert_called_with(
            "user_1", "project_a", "topic_bbb", True
        )

        # Show
        event = dict(
            pathParameters=dict(user="user_1", project="project_a", topic="topic_bbb"),
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(200, set_vote_hidden(event, None)["statusCode"])
        set_vote_hidden_model.assert_called_with(
            "user_1", "project_a", "topic_bbb", False
        )

        # Wrong user
        event = dict(
            pathParameters=dict(user="user_1", project="project_a", topic="topic_bbb"),
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(400, set_vote_hidden(event, None)["statusCode"])

        # Wrong topic
        event = dict(
            pathParameters=dict(user="user_1", project="project_a", topic="topic_xxx"),
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(400, set_vote_hidden(event, None)["statusCode"])

    @mock.patch.object(Vote, "delete_vote")
    def test_delete_vote(self, delete_vote_model):
        # Delete
        event = dict(
            pathParameters=dict(user="user_1", project="project_a", topic="topic_bbb"),
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        self.assertEqual(200, delete_vote(event, None)["statusCode"])
        delete_vote_model.assert_called_once_with("user_1", "project_a", "topic_bbb")

        # Wrong user
        event = dict(
            pathParameters=dict(user="user_1", project="project_a", topic="topic_bbb"),
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(400, delete_vote(event, None)["statusCode"])

        # Wrong topic
        event = dict(
            pathParameters=dict(user="user_1", project="project_a", topic="topic_xxx"),
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        self.assertEqual(400, delete_vote(event, None)["statusCode"])


if __name__ == "__main__":
    unittest.main()
