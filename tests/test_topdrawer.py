import unittest

from lib import topdrawer


class TestGetIdentifierFromUrl(unittest.TestCase):
    def test_none(self):
        """
        Test that it returns None when given an undefined URL
        """
        result = topdrawer.get_identifier_from_url(None)
        self.assertEqual(result, None)

    def test_empty_url(self):
        """
        Test that it returns None when given an empty URL
        """
        result = topdrawer.get_identifier_from_url("")
        self.assertEqual(result, None)

    def test_spaces_url(self):
        """
        Test that it returns None when given a URL string with only spaces.
        """
        result = topdrawer.get_identifier_from_url("       ")
        self.assertEqual(result, None)

    def test_blue_sky_sunny_day(self):
        """
        Test that it returns the expected identifier when given a proper URL.
        """
        url = "https://www.topdrawersoccer.com/college-soccer/college-soccer-details/women/clemson/clgid-30"
        result = topdrawer.get_identifier_from_url(url)
        self.assertEqual(result, 30)

if __name__ == '__main__':
    unittest.main()
