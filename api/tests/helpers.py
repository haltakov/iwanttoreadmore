import boto3


def remove_table(table_name):
    """
    Removes a test table
    :param table_name: name of the table
    """
    dynamodb = boto3.client("dynamodb")
    dynamodb.delete_table(TableName=table_name)

