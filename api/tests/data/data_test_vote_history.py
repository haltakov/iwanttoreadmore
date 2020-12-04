import boto3
from decimal import Decimal
from iwanttoreadmore.common import hash_string


def create_vote_history_table(table_name):
    """
    Create test vote history table
    :param table_name: name of the table
    :return: the table object
    """
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "IPHash", "KeyType": "HASH"},],
        AttributeDefinitions=[{"AttributeName": "User", "AttributeType": "S"},],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "UserTopicKey",
                "KeySchema": [
                    {"AttributeName": "User", "KeyType": "HASH"},
                    {"AttributeName": "TopicKey", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "INCLUDE",
                    "NonKeyAttributes": ["VoteTimestamp",],
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 2, "WriteCapacityUnits": 2},
    )


def create_test_vote_history_data(votes_table):
    """
    Populates the vote history table with test data
    :param votes_table: table object
    """
    votes_table.put_item(
        Item={
            "User": "user_1",
            "TopicKey": "project_a/topic_aaa",
            "ProjectName": "project_a",
            "Topic": "topic_aaa",
            "VoteTimestamp": Decimal(1111),
            "IPHash": hash_string("user_1" + "project_a/topic_aaa" + "192.168.0.1"),
        }
    )
    votes_table.put_item(
        Item={
            "User": "user_1",
            "TopicKey": "project_a/topic_aaa",
            "ProjectName": "project_a",
            "Topic": "topic_aaa",
            "VoteTimestamp": Decimal(2222),
            "IPHash": hash_string("user_1" + "project_a/topic_aaa" + "192.168.0.2"),
        }
    )
    votes_table.put_item(
        Item={
            "User": "user_1",
            "TopicKey": "project_a/topic_bbb",
            "ProjectName": "project_a",
            "Topic": "topic_bbb",
            "VoteTimestamp": Decimal(3333),
            "IPHash": hash_string("user_1" + "project_a/topic_bbb" + "192.168.0.2"),
        }
    )

