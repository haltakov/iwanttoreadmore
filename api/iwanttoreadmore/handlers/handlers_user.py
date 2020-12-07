import re
import json
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
            cookie = f"{cookie_content_signed};SameSite=Strict;Path=/;Expires={get_cookie_date(expiration_date)};HttpOnly"

            return create_response(
                200,
                "POST",
                username,
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


def get_user_data(event, _):
    """
    Get the data for the logged in user.
    :param event: event
    :return: dict with the main data attributes for the logged in user
    """
    # Check if the user is logged in correctly and return empty dict if not
    username = get_logged_in_user(event)
    if not username:
        return create_response(200, body=json.dumps(dict()))

    # Get the user data
    user = User()
    data = user.get_user_by_username(username)

    # Choose fileds to provide
    return create_response(
        200,
        body=json.dumps(
            {
                key: data[key]
                for key in [
                    "user",
                    "email",
                    "is_public",
                    "voted_message",
                    "voted_redirect",
                ]
            }
        ),
    )


def change_account_public(event, _):
    """
    Change the public visibility of an account
    :param event: event
    :return: 200 if the change was successful, 400 otherwise
    """
    # Check if the user is logged in correctly
    username = get_logged_in_user(event)
    if not username:
        return create_response(400, "POST", "User not logged in correctly")

    # Get the new value of the public option
    new_is_public = event["body"] == "1"

    # Change the user public setting
    user = User()
    user.set_account_public(username, new_is_public)

    return create_response(200, "POST")


def logout_user(event, _):
    """
    Logout a user by expiring the login cookie
    """
    cookie = f"user=;SameSite=Strict;Path=/;Expires={get_cookie_date(datetime.now() - timedelta(days=1))};HttpOnly"
    return create_response(
        302,
        "GET",
        "",
        {
            "Access-Control-Allow-Credentials": "true",
            "Set-Cookie": cookie,
            "Location": "/",
        },
    )


def change_voted_message_and_redirect(event, _):
    """
    Change the user's voted message and redirect.
    """
    # Parse the parameters
    params = parse_qs(event["body"])

    # Check if the user is logged in correctly
    username = get_logged_in_user(event)
    if not username:
        return create_response(400, "POST", "User not logged in correctly")

    # Set the voted message and redirect
    voted_params = dict(user=username, voted_message=None, voted_redirect=None)
    if "voted_redirect" in params and params["voted_redirect"]:
        voted_params["voted_redirect"] = params["voted_redirect"][0]
    if "voted_message" in params and params["voted_message"]:
        voted_params["voted_message"] = params["voted_message"][0]

    user = User()
    try:
        user.set_voted_message_and_redirect(**voted_params)
    except ValueError as error:
        return create_response(400, "POST", str(error))

    return create_response(200, "POST")


def add_single_voting_project(event, _):
    """
    Add a project to the user's single voting projects list
    """
    project = event["body"]

    # Check if the project name is valid
    if not re.fullmatch(r"[a-z0-9_\.\-]{1,100}", project):
        return create_response(400, "POST", "Invalid project name")

    # Get the logged in user data
    user = User()
    username = get_logged_in_user(event)
    user_data = user.get_user_by_username(username)
    if not user_data:
        return create_response(400, "POST", "User not logged in correctly")

    # Update the list of single voting projects
    if "single_voting_projects" not in user_data:
        user_data["single_voting_projects"] = [project]
    else:
        if not project in user_data["single_voting_projects"]:
            user.change_single_voting_projects(
                username, user_data["single_voting_projects"] + [project]
            )

    return create_response(200, "POST")


def remove_single_voting_project(event, _):
    """
    Remove a project from the user's single voting projects list
    """
    project = event["body"]

    # Check if the project name is valid
    if not re.fullmatch(r"[a-z0-9_\.\-]{1,100}", project):
        return create_response(400, "POST", "Invalid project name")

    # Get the logged in user data
    user = User()
    username = get_logged_in_user(event)
    user_data = user.get_user_by_username(username)
    if not user_data:
        return create_response(400, "POST", "User not logged in correctly")

    # Update the list of single voting projects
    if "single_voting_projects" in user_data:
        if project in user_data["single_voting_projects"]:
            user_data["single_voting_projects"].remove(project)

            user.change_single_voting_projects(
                username, user_data["single_voting_projects"]
            )

    return create_response(200, "POST")
