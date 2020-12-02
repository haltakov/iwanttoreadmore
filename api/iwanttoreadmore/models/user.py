import os
import boto3
from boto3.dynamodb.conditions import Key
from iwanttoreadmore.common import (
    get_current_timestamp,
    check_password,
    check_email,
    check_username,
    create_password_hash,
    check_password_hash,
    check_voted_message,
    check_url,
)


def get_user_dict_from_table(user_from_query):
    """
    Returns a dict representation of a user given a result from the table query
    :param user_from_query: a signle result from a query to the users table
    :return: dict representation of the user
    """
    return dict(
        user=user_from_query["User"],
        email=user_from_query["EMail"],
        password_hash=user_from_query["PasswordHash"],
        registered=user_from_query["Registered"],
        last_active=user_from_query["LastActive"],
        is_public=user_from_query["IsPublic"],
        voted_message=user_from_query["VotedMessage"],
        voted_redirect=user_from_query["VotedRedirect"],
    )


class User:
    """
    This class contains the logic for retrieving and modifying users data
    """

    def __init__(self):
        """
        Initialize a new User object, containing a reference to the votes DynamoDB table
        """
        self.users_table = boto3.resource("dynamodb").Table(os.environ["USERS_TABLE"])

    def create_user(self, user, email, password):
        """
        Create a new user. The function will raise an exception if the user already exists or if the password, username or e-mail are invalid.
        :param user: username
        :param email: e-mail of the user
        :param password: password of the user
        """
        if not check_username(user):
            raise ValueError(f"Invalid username")

        if not check_email(email):
            raise ValueError(f"Invalid e-mail")

        if not check_password(password):
            raise ValueError(f"Invalid password")

        if self.get_user_by_username(user):
            raise ValueError(f"Username already registered")

        if self.get_user_by_email(email):
            raise ValueError(f"E-mail already registered")

        self.users_table.put_item(
            Item={
                "User": user,
                "EMail": email,
                "PasswordHash": create_password_hash(password),
                "Registered": get_current_timestamp(),
                "LastActive": get_current_timestamp(),
                "IsPublic": False,
                "VotedMessage": None,
                "VotedRedirect": None,
            }
        )

    def update_user_email(self, user, email):
        """
        Update a user's email. The function will raise an exception if the user doesn't exist or if the e-mail is invalid.
        :param user: existing username
        :param email: new e-mail of the user
        """
        if not check_email(email):
            raise ValueError(f"Invalid e-mail")

        if not self.get_user_by_username(user):
            raise ValueError(f"Cannot find user {user}")

        self.users_table.update_item(
            Key={"User": user},
            ExpressionAttributeNames={"#EMail": "EMail",},
            ExpressionAttributeValues={":EMail": email},
            UpdateExpression="SET #EMail = :EMail",
        )

    def update_user_password(self, user, password):
        """
        Update a user's password. The function will raise an exception if the user doesn't exist or if the password is invalid.
        :param user: existing username
        :param email: new password of the user
        """
        if not check_password(password):
            raise ValueError(f"Invalid password")

        if not self.get_user_by_username(user):
            raise ValueError(f"Cannot find user {user}")

        self.users_table.update_item(
            Key={"User": user},
            ExpressionAttributeNames={"#PasswordHash": "PasswordHash",},
            ExpressionAttributeValues={":PasswordHash": create_password_hash(password)},
            UpdateExpression="SET #PasswordHash = :PasswordHash",
        )

    def update_user_last_active(self, user):
        """
        Update a user's last active time with the current time. The function will raise an exception if the user doesn't exist.
        :param user: existing username
        """
        if not self.get_user_by_username(user):
            raise ValueError(f"Cannot find user {user}")

        self.users_table.update_item(
            Key={"User": user},
            ExpressionAttributeNames={"#LastActive": "LastActive",},
            ExpressionAttributeValues={":LastActive": get_current_timestamp()},
            UpdateExpression="SET #LastActive = :LastActive",
        )

    def get_user_by_username(self, username):
        """
        Retrieves a user from the database by its username. If the user is not found, None will be returned.
        :param user: username
        :return: dict containing the user's data
        """
        user = self.users_table.query(
            ProjectionExpression="#User, EMail, PasswordHash, Registered, LastActive, IsPublic, VotedMessage, VotedRedirect",
            ExpressionAttributeNames={"#User": "User"},
            KeyConditionExpression=Key("User").eq(username),
        )

        if user["Items"]:
            return get_user_dict_from_table(user["Items"][0])
        else:
            return None

    def get_user_by_email(self, email):
        """
        Retrieves a user from the database by its e-mail. If the user is not found, None will be returned.
        :param email: e-mail of the user
        :return: dict containing the user's data
        """
        user = self.users_table.scan(
            ProjectionExpression="#User, EMail, PasswordHash, Registered, LastActive, IsPublic, VotedMessage, VotedRedirect",
            ExpressionAttributeNames={"#EMail": "EMail", "#User": "User"},
            ExpressionAttributeValues={":EMail": email,},
            FilterExpression="#EMail = :EMail",
        )

        if user["Items"]:
            return get_user_dict_from_table(user["Items"][0])
        else:
            return None

    def login_user(self, identifier, password):
        """
        Checks if the provided login information corresponds to an existing user.
        :param identifier: username or e-mail of the user
        :param password: password of the user
        :return: the username if the login is successful or None otherwise
        """
        user = (
            self.get_user_by_email(identifier)
            if "@" in identifier
            else self.get_user_by_username(identifier)
        )

        if not user:
            return None

        if check_password_hash(password, user["password_hash"]):
            self.update_user_last_active(user["user"])
            return user["user"]
        else:
            return None

    def is_account_public(self, user):
        """
        Check if the user account is public
        :param user: user to check
        :return: True if account is public, False otherwise
        """
        user = self.get_user_by_username(user)
        if user:
            return user["is_public"]
        else:
            return None

    def set_account_public(self, user, is_publuc):
        """
        Change if the user account is public or not
        :param user: user to check
        :param is_publuc: new value
        """
        if not self.get_user_by_username(user):
            raise ValueError(f"Cannot find user {user}")

        self.users_table.update_item(
            Key={"User": user},
            ExpressionAttributeNames={"#IsPublic": "IsPublic",},
            ExpressionAttributeValues={":IsPublic": is_publuc},
            UpdateExpression="SET #IsPublic = :IsPublic",
        )

    def set_voted_message_and_redirect(self, user, voted_message, voted_redirect):
        """
        Set the custom voted message and redirect
        :param user: username
        :param voted_message: new voted message
        :param voted_redirect: new voted redirect
        """
        if not self.get_user_by_username(user):
            raise ValueError(f"Cannot find user {user}")

        if not check_voted_message(voted_message):
            raise ValueError(f"Invalid voted massage (don't use HTML tags)")

        if not check_url(voted_redirect):
            raise ValueError(f"Invalid URL")

        self.users_table.update_item(
            Key={"User": user},
            ExpressionAttributeNames={
                "#VotedMessage": "VotedMessage",
                "#VotedRedirect": "VotedRedirect",
            },
            ExpressionAttributeValues={
                ":VotedMessage": voted_message,
                ":VotedRedirect": voted_redirect,
            },
            UpdateExpression="SET #VotedMessage = :VotedMessage, #VotedRedirect = :VotedRedirect",
        )
