import re
import time
import urllib.parse
import boto3
import bcrypt


def get_current_timestamp():
    """
    Get the current timestamp as a string
    :return: current timestamp string
    """
    return str(time.time())


def check_password(password):
    """
    Checks if a password is valid
    :param password: password to check
    :return: True if the password is valid, false otherwise
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9!@#$%^&\*\-_\.,+=]{4,100}", password))


def check_email(email):
    """
    Checks if an email is valid
    :param password: password to check
    :return: True if the password is valid, false otherwise
    """
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))


def check_username(username):
    """
    Checks if a username is valid
    :param username: username to check
    :return: True if the username is valid, false otherwise
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9_\.\-]{4,30}", username))


def create_password_hash(password):
    """
    Create a password hash
    :param password: password to be hashed
    :return: password hash
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password_hash(password, password_hash):
    """
    Check if a password corresponds to a password hash
    :param password: password to be checked
    :param password: password hash
    :return: True if the passwords match, False otherwise
    """
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def check_voted_message(message):
    """
    Check if the voted message is valid
    :param message: message to be checked
    :return: True if the message is valid, False otherwise
    """
    return not message or bool(
        re.fullmatch(r"[a-zA-Z0-9\.\-_+\(\)*^%$#@!,/\\\[\]\{\}\? ]{0,500}", message)
    )


def check_url(url):
    """
    Check if a URL is valid
    Source: https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
    :param url: url to be checked
    :return: True if the url is valid, False otherwise
    """
    return not url or bool(
        re.fullmatch(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            url,
            re.IGNORECASE,
        )
    )


def get_cookie_date(date):
    """
    Return a date string in a format suitable for cookies (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Date)
    :param date: datetime object
    :return: date string in cookie format
    """
    return date.strftime("%a, %d %b %Y %H:%M:%S GMT")


def get_cookie_secret():
    """
    Retrieve the cookie secret from the AWS Parameter Store
    :return: cookie secret string
    """
    client = boto3.client("ssm")
    response = client.get_parameter(Name="IWANTTOREADMORE_COOKIE_SECRET")

    return response["Parameter"]["Value"]


def sign_cookie(cookie_content):
    """
    Sign the cookie string with the cookie secret
    :param cookie: cookie string
    :return: signed cookie string
    """
    cookie_content_signed = cookie_content + get_cookie_secret()
    signature = bcrypt.hashpw(cookie_content_signed.encode(), bcrypt.gensalt())
    return f"{cookie_content}&signature={signature.decode()}"


def check_cookie_signature(cookie_string):
    """
    Verify that the content of the cookie wasn't changed by recomputing the signeture
    :param cookie_string: cookie string containing a signature at the end
    :return: The username of the logged in user if the cookie signature is valid, None otherwise
    """

    cookies = cookie_string.split(";")

    for cookie in cookies:
        params = urllib.parse.parse_qs(cookie.strip())

        if "signature" in params and "user" in params:
            cookie_with_secret = f"user={params['user'][0]}" + get_cookie_secret()
            if bcrypt.checkpw(
                cookie_with_secret.encode(), params["signature"][0].encode()
            ):
                return params["user"][0]
            else:
                return None

    return None


def get_logged_in_user(event):
    """
    Get the logged in user from the provided cookie
    :param event: event
    :return: the username of the logged in user or None if no valid user is logged in
    """

    if not "Cookie" in event["headers"]:
        return None

    return check_cookie_signature(event["headers"]["Cookie"])
