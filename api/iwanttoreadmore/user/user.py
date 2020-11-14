import os
import time
import boto3
from boto3.dynamodb.conditions import Key


class User:
    """
    This class contains the logic for retrieving and modifying users data
    """

    def __init__(self):
        """
        Initialize a new User object, containing a reference to the votes DynamoDB table
        """
        self.users_table = boto3.resource("dynamodb").Table(os.environ["USERS_TABLE"])

    def create_user(self, username, email, password):
        pass

    def get_user_by_username(self, username):
        pass

    def get_user_by_email(self, email):
        pass

    def login_user(self, identifier, password):
        pass
