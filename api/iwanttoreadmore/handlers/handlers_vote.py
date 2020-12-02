import re
import json
import logging
from urllib.parse import quote_plus
from iwanttoreadmore.common import get_logged_in_user
from iwanttoreadmore.handlers.handler_helpers import create_response
from iwanttoreadmore.models.vote import Vote
from iwanttoreadmore.models.user import User

log = logging.getLogger()
log.setLevel(logging.DEBUG)


def do_vote(event, _):
    """
    Post a vote to the database
    :param event: event
    """
    # Get all parameters
    user = event["pathParameters"]["user"].lower()
    project = event["pathParameters"]["project"].lower()
    topic = event["pathParameters"]["topic"].lower()

    # Check all parameters for validity and return if some of them is not valid
    if not re.fullmatch(r"[a-z0-9_\.\-]{4,30}", user):
        return

    if not re.fullmatch(r"[a-z0-9_\.\-]{1,100}", project):
        return

    if not re.fullmatch(r"[a-z0-9_\.\-]{1,100}", topic):
        return

    # Do the voting
    vote = Vote()
    vote.add_vote(user, project, topic)


def add_vote(event, _):
    """
    Handle add vote requests
    :param event: event
    :return: empty 200 response
    """
    # Save the vote
    do_vote(event, None)

    # Return response
    return create_response(200, "POST")


def add_vote_and_redirect(event, _):
    """
    Handle add vote requests and redirect to a info page
    :param event: event
    :return: redirect to a page explaining that the vote was added
    """
    # Save the vote
    do_vote(event, None)

    redirect_url = "/voted"

    # Find the user and determine the redirect page
    username = event["pathParameters"]["user"].lower()
    user = User()
    user_data = user.get_user_by_username(username)

    if user_data:
        # If the user has a redirect page configured
        if user_data["voted_redirect"]:
            redirect_url = user_data["voted_redirect"]
        elif user_data["voted_message"]:
            redirect_url = f"/voted?message={quote_plus(user_data['voted_message'])}"

    # Return response
    return create_response(302, additional_headers={"Location": redirect_url})


def get_votes_for_user(event, _):
    """
    Handle get votes request for a user
    :param event: event
    :return: votes data as JSON
    """
    # Get all parameters
    username = event["pathParameters"]["user"]
    log.debug(f"User param: {username}")

    # Retrieve votes from the database
    log.debug(f"Retrieving logs for user: {username}")

    votes_data = []

    # Check if the user stats are public or the user is logged in
    user = User()
    if user.is_account_public(username) or username == get_logged_in_user(event):
        vote = Vote()
        votes_data = vote.get_votes_for_user(username)

    return create_response(200, body=json.dumps(votes_data))


def get_votes_for_project(event, _):
    """
    Handle get votes request for a project
    :param event: event
    :return: votes data as JSON
    """
    # Get all parameters
    username = event["pathParameters"]["user"]
    project = event["pathParameters"]["project"]

    votes_data = []

    # Check if the user stats are public or the user is logged in
    user = User()
    if user.is_account_public(username) or username == get_logged_in_user(event):
        vote = Vote()
        votes_data = vote.get_votes_for_project(username, project)

    return create_response(200, body=json.dumps(votes_data))
