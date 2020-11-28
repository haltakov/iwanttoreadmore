import boto3


def remove_table(table_name):
    """
    Removes a test table
    :param table_name: name of the table
    """
    dynamodb = boto3.client("dynamodb")
    dynamodb.delete_table(TableName=table_name)


def create_cookie_parameter():
    """
    Creates a SSM parameter for the cookie secret
    """
    client = boto3.client("ssm")
    client.put_parameter(
        Name="IWANTTOREADMORE_COOKIE_SECRET",
        Description="",
        Value="cookiesecret",
        Type="String",
    )


def delete_cookie_parameter():
    """
    Deletes the SSM parameter for the cookie secret
    """
    client = boto3.client("ssm")
    client.delete_parameter(Name="IWANTTOREADMORE_COOKIE_SECRET")
