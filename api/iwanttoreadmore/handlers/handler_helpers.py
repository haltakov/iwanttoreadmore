def create_response(code, method="GET", body="", additional_headers=None):
    """
    Create a HTTP repsonse dictionary
    :param code: HTTP response code
    :param method: HTTP method
    :param body: HTTP response body
    :param additional_headers: additional headers to add to the default list
    :return: HTTP response dictionary
    """

    headers = {
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": method,
    }

    if additional_headers:
        headers.update(additional_headers)

    return {
        "statusCode": code,
        "headers": headers,
        "body": body,
    }
