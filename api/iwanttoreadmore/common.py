import re
import time
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

