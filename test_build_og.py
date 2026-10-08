"""build-og.py stamps every card address with its picture's hash.

X, Telegram and LinkedIn keep a card's image by its URL: a picture redrawn
under the same address kept showing the old one (t27.ai's home card, still the
blog index card on X on 2026-10-08). These hold the stamp to that rule.

    python3 -m unittest test_build_og
"""
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("build_og", Path(__file__).with_name("build-og.py"))
build_og = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_og)

V = {"og-blog-x.png": "aaaaaaaaaaaa", "og-image.png": "bbbbbbbbbbbb"}


class StampTest(unittest.TestCase):
    def test_an_unversioned_card_gets_its_hash(self):
        self.assertEqual(
            build_og.stamp('<meta property="og:image" content="https://t27.ai/og-blog-x.png" />', V),
            '<meta property="og:image" content="https://t27.ai/og-blog-x.png?v=aaaaaaaaaaaa" />',
        )

    def test_a_stale_version_is_replaced(self):
        self.assertEqual(
            build_og.stamp('content="https://t27.ai/og-blog-x.png?v=0123456789ab"', V),
            'content="https://t27.ai/og-blog-x.png?v=aaaaaaaaaaaa"',
        )

    def test_a_site_relative_address_and_json_too(self):
        self.assertEqual(build_og.stamp('<img src="/og-blog-x.png?v=0123456789ab&w=1">', V),
                         '<img src="/og-blog-x.png?v=aaaaaaaaaaaa&w=1">')
        self.assertEqual(build_og.stamp('"image":"https://t27.ai/og-image.png"', V),
                         '"image":"https://t27.ai/og-image.png?v=bbbbbbbbbbbb"')

    def test_a_card_with_no_picture_is_left_alone(self):
        page = '<meta property="og:image" content="https://t27.ai/og-blog-missing.png" />'
        self.assertEqual(build_og.stamp(page, V), page)

    def test_a_longer_name_is_not_a_card(self):
        page = '<a href="https://t27.ai/og-blog-x.pngs">'
        self.assertEqual(build_og.stamp(page, V), page)

    def test_stamping_twice_changes_nothing(self):
        once = build_og.stamp('content="https://t27.ai/og-blog-x.png"', V)
        self.assertEqual(build_og.stamp(once, V), once)


if __name__ == "__main__":
    unittest.main()
