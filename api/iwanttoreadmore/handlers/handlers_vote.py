import json
import logging
from iwanttoreadmore.common import get_logged_in_user
from iwanttoreadmore.handlers.handler_helpers import create_response
from iwanttoreadmore.models.vote import Vote

log = logging.getLogger()
log.setLevel(logging.DEBUG)


def add_vote(event, _):
    """
    Handle add vote requests
    :param event: event
    :return: empty 200 response
    """
    # Get all parameters
    user = event["pathParameters"]["user"]
    project = event["pathParameters"]["project"]
    topic = event["pathParameters"]["topic"]

    # Do the voting
    vote = Vote()
    vote.add_vote(user, project, topic)

    # Return response
    return create_response(200, "POST")


def add_vote_and_redirect(event, _):
    """
    Handle add vote requests and redirect to a info page
    :param event: event
    :return: redirect to a page explaining that the vote was added
    """
    # Get all parameters
    user = event["pathParameters"]["user"]
    project = event["pathParameters"]["project"]
    topic = event["pathParameters"]["topic"]

    # Do the voting
    vote = Vote()
    vote.add_vote(user, project, topic)

    # Return response
    return create_response(
        302, additional_headers={"Location": "https://iwanttoreadmore.com/voted"}
    )


def get_votes_for_user(event, _):
    """
    Handle get votes request for a user
    :param event: event
    :return: votes data as JSON
    """
    # Get all parameters
    user = event["pathParameters"]["user"]
    log.debug(f"get_votes_for_user: {user}")

    # If the user not specified, retrieve it from the cookie
    if not user or user == "null":
        user = get_logged_in_user(event)

    # Retrieve votes from the database
    log.debug(f"Retrieving logs for user: {user}")
    votes_data = []

    if user:
        vote = Vote()
        votes_data = vote.get_votes_for_user(user)

    return create_response(200, body=json.dumps(votes_data))


def get_votes_for_project(event, _):
    """
    Handle get votes request for a project
    :param event: event
    :return: votes data as JSON
    """
    # Get all parameters
    user = event["pathParameters"]["user"]
    project = event["pathParameters"]["project"]

    # Retrieve votes from the database
    vote = Vote()
    votes_data = vote.get_votes_for_project(user, project)

    return create_response(200, body=json.dumps(votes_data))
