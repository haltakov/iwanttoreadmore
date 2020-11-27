from datetime import datetime, timedelta
from urllib.parse import parse_qs
from iwanttoreadmore.common import get_cookie_date, sign_cookie, check_cookie_signature
from iwanttoreadmore.models.user import User


def login_user(event, _):
    """
    Login a user
    :param event: event
    :return: 200 and a login cookie if successful, 401 otherwise
    """

    # Parse the paramteres
    params = parse_qs(event["body"])

    # Make sure that the request contains all needed data
    if "identifier" in params and "password" in params:
        # Try to login the user
        user = User()
        username = user.login_user(params["identifier"][0], params["password"][0])

        if username:
            cookie_content = f"user={username}"
            cookie_content_signed = sign_cookie(cookie_content)

            expiration_date = datetime.now() + timedelta(days=30)
            cookie = f"{cookie_content_signed};SameSite=Strict;Expires={get_cookie_date(expiration_date)};HttpOnly"

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST",
                    "Access-Control-Allow-Credentials": "true",
                    "Set-Cookie": cookie,
                },
                "body": "",
            }

    return {
        "statusCode": 401,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": "",
    }


def get_logged_in_user(event):
    """
    Get the logged in user from the provided cookie
    :param event: event
    :return: the username of the logged in user or None if no valid user is logged in
    """

    if not "Cookie" in event["headers"]:
        return None

    return check_cookie_signature(event["headers"]["Cookie"])


def check_user_logged_in(event, _):
    """
    Check if a user is logged in based on the provided cookie
    :param event: event
    :return: 200 if th euser is logged in, 401 otherwise
    """
    return {
        "statusCode": 200 if get_logged_in_user(event) else 401,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": "",
    }


def change_password(event, _):
    """
    Change the password of the user
    :param event: event
    :return: 200 if the change was successful, 400 if there was a problem with the new password
    """

    # Parse the parameters
    params = parse_qs(event["body"])

    # Check if a password is missing or they don't match
    if (
        "newpassword" not in params
        or "newpassword2" not in params
        or params["newpassword"][0] != params["newpassword2"][0]
    ):
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
            },
            "body": "The two passwords don't match",
        }

    # Check if the user is logged in correctly
    username = get_logged_in_user(event)
    if not username:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
            },
            "body": "User not logged in correctly",
        }

    # Try to change the password
    user = User()
    try:
        user.update_user_password(username, params["newpassword"][0])

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
            },
            "body": "",
        }
    except ValueError as error:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
            },
            "body": str(error),
        }
