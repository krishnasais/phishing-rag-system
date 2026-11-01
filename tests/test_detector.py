import unittest

from app.detector import inspect_url


class DetectorTests(unittest.TestCase):

    def test_empty_input(self):

        result = inspect_url("")

        self.assertEqual(
            result["findings"],
            ["No URL entered."]
        )

    def test_ip_and_http(self):

        result = inspect_url(
            "http://192.0.2.10/account"
        )

        self.assertTrue(
            any(
                "IP address" in item
                for item in result["findings"]
            )
        )

        self.assertTrue(
            any(
                "Uses HTTP" in item
                for item in result["findings"]
            )
        )

    def test_at_symbol(self):

        result = inspect_url(
            "http://example.com@sample.invalid/login"
        )

        self.assertTrue(
            any(
                "@ symbol" in item
                for item in result["findings"]
            )
        )

    def test_many_hostname_segments(self):

        result = inspect_url(
            "https://a.b.c.d.e.example.invalid/path"
        )

        self.assertTrue(
            any(
                "many hostname" in item
                for item in result["findings"]
            )
        )

    def test_punycode(self):

        result = inspect_url(
            "https://xn--example.invalid/"
        )

        self.assertTrue(
            any(
                "punycode" in item
                for item in result["findings"]
            )
        )

    def test_malformed_url(self):

        result = inspect_url(
            "http://[bad"
        )

        self.assertFalse(
            result["is_valid_format"]
        )


if __name__ == "__main__":

    unittest.main()