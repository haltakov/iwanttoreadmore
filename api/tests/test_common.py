import unittest
from unittest import mock
from iwanttoreadmore.common import (
    get_current_timestamp,
    check_email,
    check_password,
    check_username,
)


class CommonTestCase(unittest.TestCase):
    @mock.patch("time.time", return_value=9999)
    def test_get_current_timestamp(self, time):
        self.assertEqual("9999", get_current_timestamp())

    def test_check_email(self):
        self.assertTrue(check_email("test@gmail.com"))
        self.assertTrue(check_email("test.test@gmail.com"))
        self.assertTrue(check_email("test.test+test@gmail.com"))
        self.assertTrue(check_email("haltakov@aaa.bbb.com"))

        self.assertFalse(check_email("test"))
        self.assertFalse(check_email("test.test"))
        self.assertFalse(check_email("test@test"))

    def test_check_password(self):
        self.assertTrue(check_password("test"))
        self.assertTrue(check_password("1234"))
        self.assertTrue(check_password("TEST"))
        self.assertTrue(check_password("@#$%^&*-_.,"))
        self.assertTrue(check_password("a" * 100))

        self.assertFalse(check_password(""))
        self.assertFalse(check_password("a"))
        self.assertFalse(check_password("aa"))
        self.assertFalse(check_password("aaa"))
        self.assertFalse(check_password("a" * 101))
        self.assertFalse(check_password("test()"))

    def test_check_username(self):
        self.assertTrue(check_username("aaaa"))
        self.assertTrue(check_username("BBBB"))
        self.assertTrue(check_username("1234"))
        self.assertTrue(check_username("aaa-_."))
        self.assertTrue(check_username("a" * 30))

        self.assertFalse(check_username(""))
        self.assertFalse(check_username("a"))
        self.assertFalse(check_username("aa"))
        self.assertFalse(check_username("aaa"))
        self.assertFalse(check_username("a" * 31))


if __name__ == "__main__":
    unittest.main()
