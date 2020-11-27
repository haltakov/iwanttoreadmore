import json
from iwanttoreadmore.models.vote import Vote


def add_vote(event, context):
    """
    Handle add vote requests
    :param event: event
    :param context: context
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
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": "",
    }


def add_vote_and_redirect(event, context):
    """
    Handle add vote requests and redirect to a info page
    :param event: event
    :param context: context
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
    return {
        "statusCode": 302,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Location": "https://iwanttoreadmore.com/voted",
        },
        "body": "",
    }


def get_votes_for_user(event, context):
    """
    Handle get votes request for a user
    :param event: event
    :param context: context
    :return: votes data as JSON
    """
    # Get all parameters
    user = event["pathParameters"]["user"]

    # Retrieve votes from the database
    vote = Vote()
    votes_data = vote.get_votes_for_user(user)

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": json.dumps(votes_data),
    }

    return response


def get_votes_for_project(event, context):
    """
    Handle get votes request for a project
    :param event: event
    :param context: context
    :return: votes data as JSON
    """
    # Get all parameters
    user = event["pathParameters"]["user"]
    project = event["pathParameters"]["project"]

    # Retrieve votes from the database
    vote = Vote()
    votes_data = vote.get_votes_for_project(user, project)

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": json.dumps(votes_data),
    }

    return response
