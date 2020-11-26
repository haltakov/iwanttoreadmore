from datetime import datetime, timedelta
from urllib.parse import parse_qs
from iwanttoreadmore.common import get_cookie_date, sign_cookie, check_cookie_signature
from iwanttoreadmore.user.user import User


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


def check_user_logged_in(event, _):
    """
    Check if a user is logged in based on the provided cookie
    :param event: event
    :return: 200 if th euser is logged in, 401 otherwise
    """
    status_code = 401

    if "Cookie" in event["headers"]:
        cookie = event["headers"]["Cookie"]

        if check_cookie_signature(cookie):
            status_code = 200

    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": "",
    }

