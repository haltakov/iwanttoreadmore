import unittest
import os
import json
from unittest import mock
import boto3
from moto import mock_dynamodb2
from moto import mock_ssm
from iwanttoreadmore.handlers.handlers_user import (
    login_user,
    check_user_logged_in,
    change_password,
    logout_user,
    get_user_data,
    change_account_public,
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
        return {key: full_user_data[key] for key in ["user", "email", "is_public"]}

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
        event_get = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        data = get_user_data(event_get, None)
        self.assertTrue(data["is_public"])

        event_change = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(200, change_account_public(event_change, None)["statusCode"])
        event_get = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        data = get_user_data(event, None)
        self.assertFlase(data["is_public"])

        event_change = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="1",
        )
        self.assertEqual(200, change_account_public(event_change, None)["statusCode"])
        event_get = dict(
            headers=dict(
                Cookie="user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
        )
        data = get_user_data(event, None)
        self.assertTrue(data["is_public"])

        # Wrong cookie
        event_2 = dict(
            headers=dict(
                Cookie="user=user_2&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm"
            ),
            body="0",
        )
        self.assertEqual(400, change_account_public(event_2, None)["statusCode"])


if __name__ == "__main__":
    unittest.main()
