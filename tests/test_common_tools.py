import unittest

from common import tools

from bs4 import BeautifulSoup

class TestIsMemberClub(unittest.TestCase):


    def test_undefined_name_and_list(self):
        result = tools.is_member_club(None, None)
        self.assertFalse(result)

    def test_undefined_name(self):
        result = tools.is_member_club(None, [])
        self.assertFalse(result)

    def test_undefined_list(self):
        result = tools.is_member_club("something", None)
        self.assertFalse(result)

    def test_empty_name(self):
        result = tools.is_member_club("", [])
        self.assertFalse(result)

    def test_name_with_only_spaces(self):
        result = tools.is_member_club("     ", [])
        self.assertFalse(result)

    def test_positive(self):
        result = tools.is_member_club("Thing", [ { "name": "Thing" } ])
        self.assertTrue(result)

    def test_negative(self):
        result = tools.is_member_club("OtherThing", [ { "name": "Thing" } ])
        self.assertFalse(result)

class TestGetAnchorText(unittest.TestCase):


    def test_none(self):
        """
        Test that it returns None when given an undefined element.
        """
        result = tools.get_anchor_text(None)
        self.assertEqual(result, None)

    def test_element_with_anchor_text(self):
        html = "<html><body><a href='something'>cool</a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_text(soup)
        self.assertEqual(result, "cool")

    def test_element_with_anchor_text_leading_spaces(self):
        html = "<html><body><a href='something'>  cool</a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_text(soup)
        self.assertEqual(result, "cool")

    def test_element_with_anchor_text_trailing_spaces(self):
        html = "<html><body><a href='something'>cool   </a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_text(soup)
        self.assertEqual(result, "cool")

    def test_element_with_anchor_text_spaces(self):
        html = "<html><body><a href='something'>  cool   </a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_text(soup)
        self.assertEqual(result, "cool")



class TestGetAnchorUrl(unittest.TestCase):


    def test_none(self):
        """
        Test that it returns None when given an undefined element.
        """
        result = tools.get_anchor_url(None)
        self.assertEqual(result, None)

    def test_element_without_anchor(self):
        """
        Test that it returns None when given an element with no anchor tag.
        """
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_url(soup)
        self.assertEqual(result, None)

    def test_element_with_empty_anchor_url(self):
        html = "<html><body><a href=''>cool</a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_url(soup)
        self.assertEqual(result, None)

    def test_element_with_spaces_anchor_url(self):
        html = "<html><body><a href='    '>cool</a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_url(soup)
        self.assertEqual(result, None)

    def test_element_with_nonempty_anchor_url(self):
        html = "<html><body><a href='something'>cool</a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_url(soup)
        self.assertEqual(result, "something")

    def test_element_with_nonempty_anchor_url_prefixed(self):
        html = "<html><body><a href='something'>cool</a></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = tools.get_anchor_url(soup, 'xxx')
        self.assertEqual(result, "xxxsomething")


if __name__ == '__main__':
    unittest.main()
