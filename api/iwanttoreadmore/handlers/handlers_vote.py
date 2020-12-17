import re
import json
import logging
from urllib.parse import quote_plus
from iwanttoreadmore.common import get_logged_in_user, get_ip_address
from iwanttoreadmore.handlers.handler_helpers import create_response
from iwanttoreadmore.models.vote import Vote, get_topic_key
from iwanttoreadmore.models.vote_history import VoteHistory
from iwanttoreadmore.models.user import User

log = logging.getLogger()
log.setLevel(logging.DEBUG)


def do_vote(event, _):
    """
    Post a vote to the database
    :param event: event
    """
    # Get all parameters
    username = event["pathParameters"]["user"].lower()
    project = event["pathParameters"]["project"].lower()
    topic = event["pathParameters"]["topic"].lower()

    # Check all parameters for validity and return if some of them is not valid
    if not re.fullmatch(r"[a-z0-9_\.\-]{3,30}", username):
        return

    if not re.fullmatch(r"[a-z0-9_\.\-]{1,100}", project):
        return

    if not re.fullmatch(r"[a-z0-9_\.\-]{1,100}", topic):
        return

    # Check if this IP address already voted for this topic
    log.debug(f"Event: {event}")
    ip_address = get_ip_address(event)

    vote_history = VoteHistory()
    if vote_history.check_ip_voted(username, get_topic_key(project, topic), ip_address):
        return

    # Check if the user has multiple voting for a project disabled
    user = User()
    user_data = user.get_user_by_username(username)

    # Stop if the user is not registered
    if not user_data:
        return

    # Stop ff the project is a single voting and the user already voted
    if (
        "single_voting_projects" in user_data
        and project in user_data["single_voting_projects"]
        and vote_history.check_ip_voted_project(username, project, ip_address)
    ):
        return

    # Do the voting
    vote = Vote()
    vote.add_vote(username, project, topic)
    vote_history.add_vote_history(username, project, topic, ip_address)


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

    # Check if the user stats are public or the user is logged in
    user = User()
    user_data = user.get_user_by_username(username)

    if user_data and (user_data["is_public"] or username == get_logged_in_user(event)):
        vote = Vote()
        votes_data = vote.get_votes_for_user(username)
        result = dict(
            single_voting_projects=user_data.get("single_voting_projects"),
            votes=votes_data,
        )
        return create_response(200, body=json.dumps(result))
    else:
        return create_response(400, "GET", "Invalid user")


def get_votes_for_project(event, _):
    """
    Handle get votes request for a project
    :param event: event
    :return: votes data as JSON
    """
    # Get all parameters
    username = event["pathParameters"]["user"]
    project = event["pathParameters"]["project"]

    # Check if the user stats are public or the user is logged in
    user = User()
    user_data = user.get_user_by_username(username)

    if user_data and (user_data["is_public"] or username == get_logged_in_user(event)):
        vote = Vote()
        votes_data = vote.get_votes_for_project(username, project)
        result = dict(
            single_voting_projects=user_data.get("single_voting_projects"),
            votes=votes_data,
        )
        return create_response(200, body=json.dumps(result))
    else:
        return create_response(400, "GET", "Invalid user")


def set_vote_hidden(event, _):
    """
    Handle changing the hidden state of a vote
    :param event: event
    :return: votes data as JSON
    """
    user = event["pathParameters"]["user"].lower()
    project = event["pathParameters"]["project"].lower()
    topic = event["pathParameters"]["topic"].lower()
    hidden = event["body"] == "1"

    # Check if we are changing the currently logged in user
    loggedin_user = get_logged_in_user(event)
    if user != loggedin_user:
        return create_response(400, "POST", "User not logged in correctly")

    vote = Vote()

    # Check if the topic exists
    if vote.get_vote_count(user, get_topic_key(project, topic)) > 0:
        vote.set_vote_hidden(user, project, topic, hidden)
        return create_response(200, "POST")
    else:
        return create_response(400, "POST", "Topic doesn't exist")


def delete_vote(event, _):
    """
    Delete a vote
    :param event: event
    :return: votes data as JSON
    """
    user = event["pathParameters"]["user"].lower()
    project = event["pathParameters"]["project"].lower()
    topic = event["pathParameters"]["topic"].lower()

    # Check if we are changing the currently logged in user
    loggedin_user = get_logged_in_user(event)
    if user != loggedin_user:
        return create_response(400, "POST", "User not logged in correctly")

    vote = Vote()

    # Check if the topic exists
    if vote.get_vote_count(user, get_topic_key(project, topic)) > 0:
        vote.delete_vote(user, project, topic)
        return create_response(200, "POST")
    else:
        return create_response(400, "POST", "Topic doesn't exist")
