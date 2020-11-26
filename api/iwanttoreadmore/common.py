import re
import time
import boto3
import bcrypt
import urllib.parse


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

