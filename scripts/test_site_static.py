import re
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = [
    "index.html",
    "timeline.html",
    "members.html",
    "gallery.html",
    "magazine.html",
    "archive.html",
    "guestbook.html",
    "event.html",
    "survey.html",
    "stats.html",
    "day.html",
]


class TestSiteStatic(unittest.TestCase):
    def test_public_pages_have_share_metadata_and_icons(self):
        for name in PUBLIC_PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(page=name):
                self.assertIn('name="description"', html)
                self.assertIn('property="og:title"', html)
                self.assertIn('property="og:description"', html)
                self.assertIn('property="og:image"', html)
                self.assertIn('rel="apple-touch-icon"', html)

    def test_social_and_icon_asset_dimensions(self):
        expected = {
            "assets/og-image.png": (1200, 630),
            "assets/apple-touch-icon.png": (180, 180),
            "assets/favicon.png": (64, 64),
        }
        for path, size in expected.items():
            with self.subTest(asset=path):
                with Image.open(ROOT / path) as image:
                    self.assertEqual(image.size, size)

    def test_gallery_uses_batched_rendering_and_dialog_semantics(self):
        html = (ROOT / "gallery.html").read_text(encoding="utf-8")
        self.assertRegex(html, r"var batchSize\s*=\s*200")
        self.assertIn("IntersectionObserver", html)
        self.assertIn('role="dialog"', html)
        self.assertIn("history.pushState", html)
        self.assertIn('aria-modal="true"', html)

    def test_member_code_uses_numeric_keyboard(self):
        html = (ROOT / "members.html").read_text(encoding="utf-8")
        code_input = re.search(r'<input[^>]+id="code-input"[^>]*>', html, re.S)
        self.assertIsNotNone(code_input)
        self.assertIn('inputmode="numeric"', code_input.group(0))

    def test_new_pages_exist(self):
        for name in ["404.html", "survey.html", "stats.html", "day.html"]:
            with self.subTest(page=name):
                self.assertTrue((ROOT / name).is_file())


if __name__ == "__main__":
    unittest.main()
