from datetime import datetime, timedelta
from urllib.parse import parse_qs
from iwanttoreadmore.handlers.handler_helpers import create_response
from iwanttoreadmore.common import get_cookie_date, sign_cookie, get_logged_in_user
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

            return create_response(
                200,
                "POST",
                "",
                {"Access-Control-Allow-Credentials": "true", "Set-Cookie": cookie},
            )

    return create_response(401, "POST")


def check_user_logged_in(event, _):
    """
    Check if a user is logged in based on the provided cookie
    :param event: event
    :return: 200 if th euser is logged in, 401 otherwise
    """
    return create_response(200 if get_logged_in_user(event) else 401)


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
        return create_response(400, "POST", "The two passwords don't match")

    # Check if the user is logged in correctly
    username = get_logged_in_user(event)
    if not username:
        return create_response(400, "POST", "User not logged in correctly")

    # Try to change the password
    user = User()
    try:
        user.update_user_password(username, params["newpassword"][0])

        return create_response(200, "POST")

    except ValueError as error:
        return create_response(400, "POST", str(error))


def logout_user(event, _):
    """
    Logout a user by expiring the login cookie
    """
    cookie = f"user=;SameSite=Strict;Expires={get_cookie_date(datetime.now() - timedelta(days=1))};HttpOnly"
    return create_response(
        302,
        "GET",
        "",
        {
            "Access-Control-Allow-Credentials": "true",
            "Set-Cookie": cookie,
            "Location": "https://iwanttoreadmore.com/",
        },
    )

