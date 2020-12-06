import os
import boto3
from boto3.dynamodb.conditions import Key
from iwanttoreadmore.common import get_current_timestamp


def get_topic_key(project_name, topic):
    """
    Get the topic key for a project name and a topic
    :param project_name: project name
    :param topic: topic
    :return: topic key
    """
    return f"{project_name}/{topic}"


def get_vote_dict_from_table(vote_from_query):
    """
    Returns a dict representation of a vote given a result from the table query
    :param vote_from_query: a signle result from a query to the votes table
    :return: dict representation of the vote
    """
    result = dict(
        topic=vote_from_query["Topic"],
        project_name=vote_from_query["ProjectName"],
        vote_count=int(vote_from_query["VoteCount"]),
        last_vote=vote_from_query["LastVote"],
    )

    if "VoteHidden" in vote_from_query:
        result["hidden"] = vote_from_query["VoteHidden"]

    return result


class Vote:
    """
    This class contains the logic for retrieving and modifying votes data
    """

    def __init__(self):
        """
        Initialize a new Vote object, containing a reference to the votes DynamoDB table
        """
        self.votes_table = boto3.resource("dynamodb").Table(os.environ["VOTES_TABLE"])

    def get_votes_for_user(self, user):
        """
        Retrieves all votes (topic, project, votes) for the specified user.
        :param user: user for which the votes should be retrieved
        :return: List of dictionaries describing the votes
        """
        votes = self.votes_table.query(
            ProjectionExpression="Topic, ProjectName, VoteCount, LastVote, VoteHidden",
            KeyConditionExpression=Key("User").eq(user),
        )

        votes_data = [get_vote_dict_from_table(vote) for vote in votes["Items"]]

        return sorted(votes_data, key=lambda x: x["vote_count"], reverse=True)

    def get_votes_for_project(self, user, project_name):
        """
        Retrieves all votes (topic, project, votes) for the specified user and project.
        :param user: user for which the votes should be retrieved
        :param project_name: project for which the votes should be retrieved
        :return: List of dictionaries describing the votes
        """
        votes = self.votes_table.query(
            ProjectionExpression="Topic, ProjectName, VoteCount, LastVote, VoteHidden",
            KeyConditionExpression=Key("User").eq(user),
        )

        votes_data = [
            get_vote_dict_from_table(vote)
            for vote in votes["Items"]
            if vote["ProjectName"] == project_name
        ]

        return sorted(votes_data, key=lambda x: x["vote_count"], reverse=True)

    def get_vote_count(self, user, topic_key):
        """
        Get the vote count of a topic key
        :param user: user to which the topic key belongs
        :param topic_key: topic key for which the vote count should be retrieved
        :return: vote count
        """
        vote = self.votes_table.query(
            ProjectionExpression="VoteCount",
            KeyConditionExpression=Key("User").eq(user) & Key("TopicKey").eq(topic_key),
        )

        return int(vote["Items"][0]["VoteCount"]) if vote["Count"] else 0

    def set_vote_count(self, user, topic_key, vote_count):
        """
        Set the vote count for a topic key
        :param user: user to which the topic key belongs
        :param topic_key: topic key for which the vote count should be set
        :param vote_count: new vote count
        """
        self.votes_table.update_item(
            Key={"User": user, "TopicKey": topic_key},
            ExpressionAttributeNames={
                "#VoteCount": "VoteCount",
                "#LastVote": "LastVote",
            },
            ExpressionAttributeValues={
                ":VoteCount": vote_count,
                ":LastVote": get_current_timestamp(),
            },
            UpdateExpression="SET #VoteCount = :VoteCount, #LastVote = :LastVote",
        )

    def create_topic(self, user, topic, project_name):
        """
        Create a new topic
        :param user: user for which a new topic should be created
        :param topic: name of the topic
        :param project_name: project name for which the topic should be created
        :return:
        """
        self.votes_table.put_item(
            Item={
                "User": user,
                "TopicKey": get_topic_key(project_name, topic),
                "ProjectName": project_name,
                "Topic": topic,
                "LastVote": get_current_timestamp(),
                "VoteCount": 1,
            }
        )

    def add_vote(self, user, project_name, topic):
        """
        Increase the vote count by 1 for a specified topic
        :param user: user which the topic belongs to
        :param project_name: project name
        :param topic: topic
        """
        topic_key = get_topic_key(project_name, topic)

        vote_count = self.get_vote_count(user, topic_key)

        if vote_count > 0:
            self.set_vote_count(user, topic_key, vote_count + 1)
        else:
            self.create_topic(user, topic, project_name)

    def set_vote_hidden(self, user, project_name, topic, hidden):
        """
        Hide the specified topic
        :param user: user which the topic belongs to
        :param project_name: project name
        :param topic: topic
        :param hidden: if the topic should be hidden or not
        """
        self.votes_table.update_item(
            Key={"User": user, "TopicKey": get_topic_key(project_name, topic)},
            ExpressionAttributeNames={"#VoteHidden": "VoteHidden",},
            ExpressionAttributeValues={":VoteHidden": hidden,},
            UpdateExpression="SET #VoteHidden = :VoteHidden",
        )

    def delete_vote(self, user, project_name, topic):
        """
        Delete the specified topic
        :param user: user which the topic belongs to
        :param project_name: project name
        :param topic: topic
        """
        self.votes_table.delete_item(
            Key={"User": user, "TopicKey": get_topic_key(project_name, topic)},
        )
