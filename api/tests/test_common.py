import unittest
from unittest import mock
from datetime import datetime
import boto3
from moto import mock_ssm
from iwanttoreadmore.common import (
    get_current_timestamp,
    check_email,
    check_password,
    check_username,
    create_password_hash,
    check_password_hash,
    get_cookie_date,
    get_cookie_secret,
    sign_cookie,
    check_cookie_signature,
)


@mock_ssm
class CommonTestCase(unittest.TestCase):
    def setUp(self):
        client = boto3.client("ssm")
        client.put_parameter(
            Name="IWANTTOREADMORE_COOKIE_SECRET",
            Description="",
            Value="cookiesecret",
            Type="String",
        )

    def tearDown(self):
        client = boto3.client("ssm")
        client.delete_parameter(Name="IWANTTOREADMORE_COOKIE_SECRET")

    @mock.patch("time.time", return_value=9999)
    def test_get_current_timestamp(self, _):
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

    @mock.patch("bcrypt.gensalt", return_value=b"$2b$12$nChdB1EJj1DZbtJgNSOFz.")
    def test_create_password_hash(self, _):
        self.assertEqual(
            "$2b$12$nChdB1EJj1DZbtJgNSOFz.fTxPXu565.ic3xtXJvjLf64F4ELnuXG",
            create_password_hash("test3"),
        )

    def test_check_password_hash(self):
        self.assertTrue(
            check_password_hash(
                "test3", "$2b$12$nChdB1EJj1DZbtJgNSOFz.fTxPXu565.ic3xtXJvjLf64F4ELnuXG"
            )
        )

        self.assertFalse(
            check_password_hash(
                "test_wrong",
                "$2b$12$nChdB1EJj1DZbtJgNSOFz.fTxPXu565.ic3xtXJvjLf64F4ELnuXG",
            )
        )

    def test_get_cookie_date(self):
        self.assertEqual(
            "Mon, 09 Mar 2020 08:13:24 GMT",
            get_cookie_date(datetime(2020, 3, 9, 8, 13, 24)),
        )
        self.assertEqual(
            "Wed, 21 Oct 2015 07:28:00 GMT",
            get_cookie_date(datetime(2015, 10, 21, 7, 28, 0)),
        )

    def test_get_cookie_secret(self):
        self.assertEqual("cookiesecret", get_cookie_secret())

    @mock.patch("bcrypt.gensalt", return_value=b"$2b$12$FTU0sMh7DANHArQW1CBGiu")
    def test_sign_cookie(self, _):
        cookie = "user=haltakov"
        self.assertEqual(
            "user=haltakov&signature=$2b$12$FTU0sMh7DANHArQW1CBGiuKdkfpeViomU/Smp2TFBwv0wmBhMEizC",
            sign_cookie(cookie),
        )

    def test_check_cookie_signature(self):
        self.assertEqual(
            "haltakov",
            check_cookie_signature(
                "user=haltakov&signature=$2b$12$FTU0sMh7DANHArQW1CBGiuKdkfpeViomU/Smp2TFBwv0wmBhMEizC"
            ),
        )
        self.assertEqual(
            "haltakov",
            check_cookie_signature(
                "user=haltakov&signature=$2b$12$FTU0sMh7DANHArQW1CBGiuKdkfpeViomU/Smp2TFBwv0wmBhMEizC; loggedinuser=haltakov"
            ),
        )
        self.assertEqual(
            "haltakov",
            check_cookie_signature(
                "loggedinuser=haltakov; user=haltakov&signature=$2b$12$FTU0sMh7DANHArQW1CBGiuKdkfpeViomU/Smp2TFBwv0wmBhMEizC"
            ),
        )
        self.assertEqual(
            None,
            check_cookie_signature(
                "user=otheruser&signature=$2b$12$FTU0sMh7DANHArQW1CBGiuKdkfpeViomU/Smp2TFBwv0wmBhMEizC"
            ),
        )
        self.assertEqual(None, check_cookie_signature("user=haltakov"))


if __name__ == "__main__":
    unittest.main()
