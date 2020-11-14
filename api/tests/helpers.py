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


def remove_table(table_name):
    """
    Removes a test table
    :param table_name: name of the table
    """
    dynamodb = boto3.client("dynamodb")
    dynamodb.delete_table(TableName=table_name)


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

    if not project:
        result = data[user]
    else:
        result = [x for x in data[user] if x["project_name"] == project]

    return sorted(result, key=lambda x: x["vote_count"], reverse=True)


def create_users_table(table_name):
    """
    Create test users table
    :param table_name: name of the table
    :return: the table object
    """
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "User", "KeyType": "HASH"},],
        AttributeDefinitions=[{"AttributeName": "User", "AttributeType": "S"},],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )


def create_test_users_data(users_table):
    """
    Populates a users table with test data
    :param votes_table: table object
    """
    users_table.put_item(
        Item={
            "User": "user_1",
            "EMail": "user_1@gmail.com",
            "PasswordHash": "$2b$12$O71GJeJ/8dbwS6q3sXab7.sdnczecXyQeWiLGxEeA9oClAvjeEcti",  # test
            "Registered": "1111",
            "LastActive": "1111",
        }
    )
    users_table.put_item(
        Item={
            "User": "user_2",
            "EMail": "user_2@gmail.com",
            "PasswordHash": "$2b$12$G/Kb.r3YAJbenM7Ul9gQXO6bIjMZtVAt1uY.nKZMQL.1i6L50LLTW",  # test2
            "Registered": "1111",
            "LastActive": "1111",
        }
    )


def get_expected_users_data():
    data = dict(
        user_1=dict(
            user="user_1",
            email="user_1@gmail.com",
            password_hash="$2b$12$O71GJeJ/8dbwS6q3sXab7.sdnczecXyQeWiLGxEeA9oClAvjeEcti",  # test
            registered="1111",
            last_active="1111",
        ),
        user_2=dict(
            user="user_2",
            email="user_2@gmail.com",
            password_hash="$2b$12$G/Kb.r3YAJbenM7Ul9gQXO6bIjMZtVAt1uY.nKZMQL.1i6L50LLTW",  # test2
            registered="1111",
            last_active="1111",
        ),
        user_3=dict(
            user="user_3",
            email="user_3@gmail.com",
            password_hash="$2b$12$nChdB1EJj1DZbtJgNSOFz.fTxPXu565.ic3xtXJvjLf64F4ELnuXG",  # test3, salt: $2b$12$nChdB1EJj1DZbtJgNSOFz.
            registered="9999",
            last_active="9999",
        ),
    )

    return data
