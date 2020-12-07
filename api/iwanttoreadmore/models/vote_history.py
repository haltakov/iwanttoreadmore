import os
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key
from iwanttoreadmore.common import get_current_timestamp, hash_string
from iwanttoreadmore.models.vote import get_topic_key


class VoteHistory:
    """
    This class contains the logic for retrieving and modifying vote history data
    """

    def __init__(self):
        """
        Initialize a new VoteHistory object, containing a reference to the vote history DynamoDB table
        """
        self.votes_history_table = boto3.resource("dynamodb").Table(
            os.environ["VOTES_HISTORY_TABLE"]
        )

    def add_vote_history(self, user, project, topic, ip_address):
        """
        Add a new vote history entry
        :param user: username
        :param project: topic key
        :param topic: topic key
        :param ip_address: IP address of the user that voted
        """
        topic_key = get_topic_key(project, topic)

        if not self.check_ip_voted(user, topic_key, ip_address):
            self.votes_history_table.put_item(
                Item={
                    "User": user,
                    "TopicKey": topic_key,
                    "VoteTimestamp": get_current_timestamp(),
                    "IPHash": hash_string(user + topic_key + ip_address),
                }
            )

    def get_vote_history(self, user, topic_key):
        """
        Get the vote history for a given user and topic key
        :param user: username
        :param topic_key: topic key
        :return: sorted list of vote timestamps of the specified topic key
        """
        votes = self.votes_history_table.query(
            IndexName="UserTopicKey",
            ProjectionExpression="VoteTimestamp",
            KeyConditionExpression=Key("User").eq(user)
            & Key("Topic_Key").eq(topic_key),
        )

        timestamps = [Decimal(vote["VoteTimestamp"]) for vote in votes["Items"]]
        return sorted(timestamps)

    def check_ip_voted(self, user, topic_key, ip_address):
        """
        Check if an IP address already voted to the specified user and topic key
        :param user: username
        :param topic_key: topic key
        :param ip_address: IP address to check
        :return: False if the IP address hasn't vote for this topic yet, True otherwise
        """
        ip_hash = hash_string(user + topic_key + ip_address)

        vote = self.votes_history_table.query(
            ProjectionExpression="IPHash",
            KeyConditionExpression=Key("IPHash").eq(ip_hash),
        )

        return len(vote["Items"]) > 0

    def check_ip_voted_project(self, user, project, ip_address):
        """
        Check if an IP address already voted to the specified user and topic key
        :param user: username
        :param project: project
        :param ip_address: IP address to check
        :return: False if the IP address hasn't vote for this topic yet, True otherwise
        """
        ip_hash = hash_string(user + project + ip_address)

        vote = self.votes_history_table.query(
            IndexName="IPHashProjectIndex",
            ProjectionExpression="IPHashProject",
            KeyConditionExpression=Key("IPHashProject").eq(ip_hash),
        )

        return len(vote["Items"]) > 0
