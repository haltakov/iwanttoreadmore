import unittest
import os
from unittest import mock
import boto3
from moto import mock_dynamodb2
from moto import mock_ssm
from iwanttoreadmore.handlers.user import login_user, check_user_logged_in
from tests.helpers import (
    create_users_table,
    create_test_users_data,
    remove_table,
)


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

        client = boto3.client("ssm")
        client.put_parameter(
            Name="IWANTTOREADMORE_COOKIE_SECRET",
            Description="",
            Value="cookiesecret",
            Type="String",
        )

    def tearDown(self):
        remove_table(os.environ["USERS_TABLE"])

        client = boto3.client("ssm")
        client.delete_parameter(Name="IWANTTOREADMORE_COOKIE_SECRET")

    @mock.patch(
        "iwanttoreadmore.handlers.user.get_cookie_date",
        return_value="Fri, 31 Jan 2020 01:23:34 GMT",
    )
    @mock.patch("bcrypt.gensalt", return_value=b"$2b$12$oGAaQWkNrjCWI0ugg8Go8u")
    def test_login_user(self, _, __):
        # Test successful login
        event_1 = dict(body="identifier=user_1@gmail.com;password=test")
        response_1 = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Credentials": "true",
                "Set-Cookie": "user=user_1&signature=$2b$12$oGAaQWkNrjCWI0ugg8Go8uZ1ld2828dTeTk2cE/WZAO2yOB4aUxQm;SameSite=Strict;Expires=Fri, 31 Jan 2020 01:23:34 GMT",
            },
            "body": "",
        }
        self.assertEqual(response_1, login_user(event_1, None))

        # Test wrong user
        event_2 = dict(body="identifier=invaliduser@gmail.com;password=test")
        response_2 = {
            "statusCode": 401,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
            },
            "body": "",
        }
        self.assertEqual(response_2, login_user(event_2, None))

        # Test wrong password
        event_3 = dict(body="identifier=user_1@gmail.com;password=wrongpassowrd")
        response_3 = {
            "statusCode": 401,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
            },
            "body": "",
        }
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


if __name__ == "__main__":
    unittest.main()
