import unittest
import os
from unittest import mock
from moto import mock_dynamodb2
from iwanttoreadmore.user.user import User
from tests.helpers import (
    create_users_table,
    create_test_users_data,
    remove_table,
    get_expected_users_data,
)


@mock_dynamodb2
class UserTestCase(unittest.TestCase):
    def setUp(self):
        """
        Create a users table and populate it with example data
        """
        os.environ["USERS_TABLE"] = "iwanttoreadmore-users-test"

        self.users_table = create_users_table(os.environ["USERS_TABLE"])
        create_test_users_data(self.users_table)
        self.expected_users_data = get_expected_users_data()

    def tearDown(self):
        remove_table(os.environ["USERS_TABLE"])

    def test_get_user_by_username(self):
        expected_user_data = get_expected_users_data()
        user = User()
        self.assertEqual(
            self.expected_users_data["user_1"], user.get_user_by_username("user_1")
        )
        self.assertEqual(
            self.expected_users_data["user_2"], user.get_user_by_username("user_2")
        )
        self.assertEqual([], user.get_user_by_username("user_3"))

    def test_get_user_by_email(self):
        expected_user_data = get_expected_users_data()
        user = User()
        self.assertEqual(
            self.expected_users_data["user_1"],
            user.get_user_by_email("user_1@gmail.com"),
        )
        self.assertEqual(
            self.expected_users_data["user_2"],
            user.get_user_by_email("user_2@gmail.com"),
        )
        self.assertEqual([], user.get_user_by_username("user_3@gmail.com"))

    @mock.patch("time.time", return_value=9999)
    @mock.patch("bcrypt.gensalt", return_value=b"$2b$12$nChdB1EJj1DZbtJgNSOFz.")
    def test_create_user(self, bcrypt, time):
        user = User()
        # Test creation of a valid user
        user.create_user("user_3", "user_3@gmail.com", "test3")
        self.assertEqual(
            self.expected_users_data["user_3"], user.get_user_by_username("user_3")
        )

        # Test invalid values
        self.assertRaises(
            ValueError, user.create_user, "user_4", "user_4@gmail.com", "a"
        )
        self.assertRaises(
            ValueError, user.create_user, "u", "user_4@gmail.com", "test4"
        )
        self.assertRaises(
            ValueError, user.create_user, "user_4", "user_4@gmail", "test4"
        )

        # Test creation of duplicate username or e-mail
        self.assertRaises(
            ValueError, user.create_user, "user_2", "user_4@gmail.com", "test4"
        )
        self.assertRaises(
            ValueError, user.create_user, "user_4", "user_2@gmail.com", "test4"
        )

    @mock.patch("time.time", return_value=9999)
    def test_login_user(self, time):
        user = User()
        # Test correct identifier and password
        self.assertEqual("user_1", user.login_user("user_1", "test"))
        self.assertEqual("user_1", user.login_user("user_1@gmail.com", "test"))

        # Test wrong identifier or password
        self.assertFalse(user.login_user("user_1", "wrong_password"))
        self.assertFalse(user.login_user("user_1", "test2"))
        self.assertFalse(user.login_user("user_3", "test3"))
        self.assertFalse(user.login_user("user_3@gmail.com", "test3"))

        # Test last active password
        self.assertEqual("1111", user.get_user_by_username("user_2")["last_active"])
        user.login_user("user_2", "test2")
        self.assertEqual("9999", user.get_user_by_username("user_2")["last_active"])

    def test_update_user_email(self):
        user = User()

        # Test valid email
        user_1 = user.get_user_by_username("user_1")
        user_1["email"] = "updated@gmail.com"

        user.update_user_email("user_1", user_1["email"])
        self.assertEqual(user_1, user.get_user_by_username("user_1"))

        # Test invalid email
        self.assertRaises(ValueError, user.update_user_email, "user_1", "")
        self.assertRaises(ValueError, user.update_user_email, "user_1", "aaaaaa")
        self.assertRaises(ValueError, user.update_user_email, "user_1", "bbbb@cccc")

        # Test invalid user
        self.assertRaises(
            ValueError, user.update_user_email, "user_x", "updated@gmail.com"
        )

    @mock.patch("bcrypt.gensalt", return_value=b"$2b$12$nChdB1EJj1DZbtJgNSOFz.")
    def test_update_user_password(self, bcrypt):
        user = User()

        # Test valid password hash
        user_1 = user.get_user_by_username("user_1")
        user_1[
            "password_hash"
        ] = "$2b$12$nChdB1EJj1DZbtJgNSOFz.fTxPXu565.ic3xtXJvjLf64F4ELnuXG"

        user.update_user_password("user_1", "test3")
        self.assertEqual(user_1, user.get_user_by_username("user_1"))

        # Test invalid password hash
        self.assertRaises(ValueError, user.update_user_password, "user_1", "")
        self.assertRaises(ValueError, user.update_user_password, "user_1", "a")
        self.assertRaises(ValueError, user.update_user_password, "user_1", "aa")
        self.assertRaises(ValueError, user.update_user_password, "user_1", "aaa")

        # Test invalid user
        self.assertRaises(
            ValueError,
            user.update_user_password,
            "user_x",
            "$2b$12$G/Kb.r3YAJbenM7Ul9gQXO6bIjMZtVAt1uY.nKZMQL.1i6L50LLTW",
        )

    @mock.patch("time.time", return_value=9999)
    def test_update_user_last_active(self, time):
        user = User()

        # Test valid password hash
        user.update_user_last_active("user_1")
        self.assertEqual("9999", user.get_user_by_username("user_1")["last_active"])

        # Test invalid user
        self.assertRaises(ValueError, user.update_user_last_active, "user_x")


if __name__ == "__main__":
    unittest.main()
