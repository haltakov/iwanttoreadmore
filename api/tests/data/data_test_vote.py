import boto3


def create_votes_table(table_name):
    """
    Create test votes table
    :param table_name: name of the table
    :return: the table object
    """
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "User", "KeyType": "HASH"},
            {"AttributeName": "TopicKey", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "User", "AttributeType": "S"},
            {"AttributeName": "TopicKey", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )


def create_test_votes_data(votes_table):
    """
    Populates a votes table with test data
    :param votes_table: table object
    """
    votes_table.put_item(
        Item={
            "User": "user_1",
            "TopicKey": "project_a/topic_aaa",
            "ProjectName": "project_a",
            "Topic": "topic_aaa",
            "LastVote": "1111",
            "VoteCount": 10,
        }
    )
    votes_table.put_item(
        Item={
            "User": "user_1",
            "TopicKey": "project_a/topic_bbb",
            "ProjectName": "project_a",
            "Topic": "topic_bbb",
            "LastVote": "2222",
            "VoteCount": 20,
        }
    )
    votes_table.put_item(
        Item={
            "User": "user_1",
            "TopicKey": "project_b/topic_ccc",
            "ProjectName": "project_b",
            "Topic": "topic_ccc",
            "LastVote": "3333",
            "VoteCount": 30,
            "VoteHidden": True,
        }
    )
    votes_table.put_item(
        Item={
            "User": "user_2",
            "TopicKey": "project_c/topic_ddd",
            "ProjectName": "project_c",
            "Topic": "topic_ddd",
            "LastVote": "4444",
            "VoteCount": 40,
        }
    )


def get_expected_votes_data(user, project=None):
    """
    Return the expect data for the votes tests
    :param user: user
    :param project: project
    :retuen: expected data dicts for the specified user and/or project
    """
    data = dict(
        user_1=[
            dict(
                topic="topic_aaa",
                project_name="project_a",
                vote_count=10,
                last_vote="1111",
            ),
            dict(
                topic="topic_bbb",
                project_name="project_a",
                vote_count=20,
                last_vote="2222",
            ),
            dict(
                topic="topic_ccc",
                project_name="project_b",
                vote_count=30,
                last_vote="3333",
                hidden=True,
            ),
        ],
        user_2=[
            dict(
                topic="topic_ddd",
                project_name="project_c",
                vote_count=40,
                last_vote="4444",
            ),
        ],
    )

    if user in data:
        if not project:
            result = data[user]
        else:
            result = [x for x in data[user] if x["project_name"] == project]
    else:
        return []

    return sorted(result, key=lambda x: x["vote_count"], reverse=True)
