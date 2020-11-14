import unittest
from unittest import mock
from iwanttoreadmore.common import get_current_timestamp


class CommonTestCase(unittest.TestCase):
    @mock.patch("time.time", return_value=9999)
    def test_get_current_timestamp(self, time):
        self.assertEqual("9999", get_current_timestamp())


if __name__ == "__main__":
    unittest.main()
