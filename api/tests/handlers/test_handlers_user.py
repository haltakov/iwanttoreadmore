import unittest
import os
import json
from unittest import mock
import boto3
from moto import mock_dynamodb2
from moto import mock_ssm
from iwanttoreadmore.models.user import User
from iwanttoreadmore.handlers.handlers_user import (
    login_user,
    check_user_logged_in,
    change_password,
    logout_user,
    get_user_data,
    change_account_public,
    change_voted_message_and_redirect,
    add_single_voting_project,
    remove_single_voting_project,
)
from iwanttoreadmore.handlers.handler_helpers import create_response
from tests.data.data_test_user import (
    create_users_table,
    create_test_users_data,
    get_expected_users_data,
)
from tests.helpers import remove_table, create_cookie_parameter, delete_cookie_parameter


@mock_dynamodb2
@mock_ssm
class UserHandlersTestCase(unittest.TestCase):
    def setUp(self):
        """
        Create a users table and populate it with example data
        """
        os.environ["USERS_TABLE"] = "iwanttoreadmore-users-handlers-test"

        self.users_table = create_users_table(os.environ["USERS_TABLE"])
        create_test_users_data(self.users_table)
        self.expected_user_data = get_expected_users_data()
        create_cookie_parameter()

    def tearDown(self):
        remove_table(os.environ["USERS_TABLE"])
        delete_cookie_parameter()

    def get_user_data(self, user):
        full_user_data = self.expected_user_data[user]
        return {
            key: full_user_data[key]
            for key in ["user", "email", "is_public", "voted_message", "voted_redirect"]
        }

    @mock.patch(
        "iwanttoreadmore.handlers.handlers_user.get_cookie_date",
        return_value="Fri, 31 Jan 2020 01:23:34 GMT",
    )
    @mock.patch("bcrypt.gensalt", return_value=b"$2b$12$oGAaQWkNrjCWI0ugg8Go8u")
    def test_login_user(self, _, __):
        # Test successful login
        event_1 = dict(body="identifier=user_1@gmail.com;password=test")
        response_1 = create_response(
            200,
            "POST",
            body="user_1",
            additional_headers={
                "Access-Control-Allow-Credentials": "true",
                "Set-Cookie": "user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm;SameSite=Strict;Path=/;Expires=Fri, 31 Jan 2020 01:23:34 GMT;HttpOnly",
            },
        )
        self.assertEqual(response_1, login_user(event_1, None))

        # Test wrong user
        event_2 = dict(body="identifier=invaliduser@gmail.com;password=test")
        response_2 = create_response(401, "POST")
        self.assertEqual(response_2, login_user(event_2, None))

        # Test wrong password
        event_3 = dict(body="identifier=user_1@gmail.com;password=wrongpassowrd")
        response_3 = create_response(401, "POST")
        self.assertEqual(response_3, login_user(event_3, None))

    def test_check_user_logged_in(self):
        event_1 = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            )
        )
        self.assertEqual(200, check_user_logged_in(event_1, None)["statusCode"])

        event_2 = dict(
            headers=dict(
                Cookie="user=invaliduser&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            )
        )
        self.assertEqual(401, check_user_logged_in(event_2, None)["statusCode"])

        event_3 = dict(headers=dict(Cookie=""))
        self.assertEqual(401, check_user_logged_in(event_3, None)["statusCode"])

    def test_change_password(self):
        # Positive case
        event_1 = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="newpassword=newpassword;newpassword2=newpassword",
        )
        response_1 = create_response(200, "POST")
        self.assertEqual(response_1, change_password(event_1, None))

        # Invalid password (too short)
        event_2 = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="newpassword=np;newpassword2=np",
        )
        response_2 = create_response(400, "POST", "Invalid password")
        self.assertEqual(response_2, change_password(event_2, None))

        # Password missmatch
        event_3 = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="newpassword=newpassword;newpassword2=otherpassword",
        )
        response_3 = create_response(400, "POST", "The two passwords don't match")
        self.assertEqual(response_3, change_password(event_3, None))

        # Bad password request
        event_4 = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="newpassword=newpassword",
        )
        response_4 = create_response(400, "POST", "The two passwords don't match")
        self.assertEqual(response_4, change_password(event_4, None))

        # Wrong user cookie
        event_5 = dict(
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="newpassword=newpassword;newpassword2=newpassword",
        )
        response_5 = create_response(400, "POST", "User not logged in correctly")
        self.assertEqual(response_5, change_password(event_5, None))

    def test_logout_user(self):
        self.assertEqual(302, logout_user(None, None)["statusCode"])

    def test_get_user_data(self):
        # Positive case
        event_1 = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        response_1 = create_response(200, body=json.dumps(self.get_user_data("user_1")))
        self.assertEqual(response_1, get_user_data(event_1, None))

        # Wrong cookie
        event_2 = dict(
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        response_2 = create_response(200, body=json.dumps(dict()))
        self.assertEqual(response_2, get_user_data(event_2, None))

        # No cookie
        event_3 = dict(headers=dict(),)
        response_3 = create_response(200, body=json.dumps(dict()))
        self.assertEqual(response_3, get_user_data(event_3, None))

    def test_change_account_public(self):
        user = User()
        data = user.get_user_by_username("user_1")
        self.assertTrue(data["is_public"])

        event_change = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(200, change_account_public(event_change, None)["statusCode"])
        data = user.get_user_by_username("user_1")
        self.assertFalse(data["is_public"])

        event_change = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="1",
        )
        self.assertEqual(200, change_account_public(event_change, None)["statusCode"])
        data = user.get_user_by_username("user_1")
        self.assertTrue(data["is_public"])

        # Wrong cookie
        event_2 = dict(
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(400, change_account_public(event_2, None)["statusCode"])

    def test_change_voted_message_and_redirect(self):
        cookie = "user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"

        # Correct empty
        event = dict(
            headers=dict(Cookie=cookie), body="voted_message=&voted_redirect=",
        )
        self.assertEqual(
            200, change_voted_message_and_redirect(event, None)["statusCode"]
        )

        # Correct voted message
        event = dict(
            headers=dict(Cookie=cookie),
            body="voted_message=New voted message&voted_redirect=",
        )
        self.assertEqual(
            200, change_voted_message_and_redirect(event, None)["statusCode"]
        )

        # Correct voted redirect
        event = dict(
            headers=dict(Cookie=cookie),
            body="voted_message=&voted_redirect=http://iwanttoreadmore.com/voted",
        )
        self.assertEqual(
            200, change_voted_message_and_redirect(event, None)["statusCode"]
        )

        # Correct voted message and redirect
        event = dict(
            headers=dict(Cookie=cookie),
            body="voted_message=Some message&voted_redirect=http://iwanttoreadmore.com/voted",
        )
        self.assertEqual(
            200, change_voted_message_and_redirect(event, None)["statusCode"]
        )
        user = User()
        user_data = user.get_user_by_username("user_1")
        self.assertEqual("Some message", user_data["voted_message"])
        self.assertEqual(
            "http://iwanttoreadmore.com/voted", user_data["voted_redirect"]
        )

        # Wrong cookie
        event = dict(
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="voted_message=New voted message&voted_redirect=",
        )
        self.assertEqual(
            400, change_voted_message_and_redirect(event, None)["statusCode"]
        )

        # Invalid message
        event = dict(
            headers=dict(Cookie=cookie),
            body="voted_message=Invalid <message>&voted_redirect=",
        )
        self.assertEqual(
            400, change_voted_message_and_redirect(event, None)["statusCode"]
        )

        # Invalid redirect
        event = dict(
            headers=dict(Cookie=cookie),
            body="voted_message=&voted_redirect=invalidurl",
        )
        self.assertEqual(
            400, change_voted_message_and_redirect(event, None)["statusCode"]
        )

    def test_add_single_voting_project(self):
        cookie = "user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"

        user = User()

        # Positive case
        event = dict(headers=dict(Cookie=cookie), body="project_c",)
        self.assertEqual(200, add_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            ["project_a", "project_b", "project_c"],
            user.get_user_by_username("user_1")["single_voting_projects"],
        )

        # Repeated case
        event = dict(headers=dict(Cookie=cookie), body="project_c",)
        self.assertEqual(200, add_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            ["project_a", "project_b", "project_c"],
            user.get_user_by_username("user_1")["single_voting_projects"],
        )

        # Wrong cookie
        event = dict(
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="project_d",
        )
        self.assertEqual(400, add_single_voting_project(event, None)["statusCode"])
        self.assertNotIn("single_voting_projects", user.get_user_by_username("user_2"))

        # Invalid project name
        event = dict(headers=dict(Cookie=cookie), body="project_invalid_<>",)
        self.assertEqual(400, add_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            ["project_a", "project_b", "project_c"],
            user.get_user_by_username("user_1")["single_voting_projects"],
        )

    def test_remove_single_voting_project(self):
        cookie = "user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"

        user = User()

        # Positive case
        event = dict(headers=dict(Cookie=cookie), body="project_a",)
        self.assertEqual(200, remove_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            ["project_b"],
            user.get_user_by_username("user_1")["single_voting_projects"],
        )

        # Repeated case
        event = dict(headers=dict(Cookie=cookie), body="project_a",)
        self.assertEqual(200, remove_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            ["project_b"],
            user.get_user_by_username("user_1")["single_voting_projects"],
        )

        # Non existing case
        event = dict(headers=dict(Cookie=cookie), body="project_c",)
        self.assertEqual(200, remove_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            ["project_b"],
            user.get_user_by_username("user_1")["single_voting_projects"],
        )

        # Last case
        event = dict(headers=dict(Cookie=cookie), body="project_b",)
        self.assertEqual(200, remove_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            [], user.get_user_by_username("user_1")["single_voting_projects"],
        )

        # Empty case
        event = dict(headers=dict(Cookie=cookie), body="project_b",)
        self.assertEqual(200, remove_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            [], user.get_user_by_username("user_1")["single_voting_projects"],
        )

        # Wrong cookie
        event = dict(
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="project_d",
        )
        self.assertEqual(400, remove_single_voting_project(event, None)["statusCode"])
        self.assertNotIn("single_voting_projects", user.get_user_by_username("user_2"))

        # Invalid project name
        event = dict(headers=dict(Cookie=cookie), body="project_invalid_<>",)
        self.assertEqual(400, remove_single_voting_project(event, None)["statusCode"])
        self.assertEqual(
            [], user.get_user_by_username("user_1")["single_voting_projects"],
        )


if __name__ == "__main__":
    unittest.main()
