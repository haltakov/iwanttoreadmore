import boto3


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
            "IsPublic": True,
            "VotedMessage": "Test Message",
            "VotedRedirect": None,
            "SingleVotingProjects": ["project_a", "project_b"],
        }
    )
    users_table.put_item(
        Item={
            "User": "user_2",
            "EMail": "user_2@gmail.com",
            "PasswordHash": "$2b$12$G/Kb.r3YAJbenM7Ul9gQXO6bIjMZtVAt1uY.nKZMQL.1i6L50LLTW",  # test2
            "Registered": "1111",
            "LastActive": "1111",
            "IsPublic": False,
            "VotedMessage": None,
            "VotedRedirect": "https://iwanttoreadmore.com/404",
        }
    )


def get_expected_users_data():
    """
    Return the expect data for the users tests
    :retuen: expected data dicts
    """
    data = dict(
        user_1=dict(
            user="user_1",
            email="user_1@gmail.com",
            password_hash="$2b$12$O71GJeJ/8dbwS6q3sXab7.sdnczecXyQeWiLGxEeA9oClAvjeEcti",  # test
            registered="1111",
            last_active="1111",
            is_public=True,
            voted_message="Test Message",
            voted_redirect=None,
            single_voting_projects=["project_a", "project_b"],
        ),
        user_2=dict(
            user="user_2",
            email="user_2@gmail.com",
            password_hash="$2b$12$G/Kb.r3YAJbenM7Ul9gQXO6bIjMZtVAt1uY.nKZMQL.1i6L50LLTW",  # test2
            registered="1111",
            last_active="1111",
            is_public=False,
            voted_message=None,
            voted_redirect="https://iwanttoreadmore.com/404",
        ),
        user_3=dict(
            user="user_3",
            email="user_3@gmail.com",
            password_hash="$2b$12$nChdB1EJj1DZbtJgNSOFz.fTxPXu565.ic3xtXJvjLf64F4ELnuXG",  # test3, salt: $2b$12$nChdB1EJj1DZbtJgNSOFz.
            registered="9999",
            last_active="9999",
            is_public=False,
            voted_message=None,
            voted_redirect=None,
        ),
    )

    return data
