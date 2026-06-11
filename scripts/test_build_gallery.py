import unittest, tempfile, json
from pathlib import Path
from PIL import Image
from build_gallery import process_image, guess_year, write_gallery_data

class TestBuildGallery(unittest.TestCase):
    def test_guess_year_from_path(self):
        self.assertEqual(guess_year(Path("cd files/2005 MR/photo.jpg")), 2005)
        self.assertEqual(guess_year(Path("cd files/1998 활동사진/a.jpg")), 1998)
        self.assertIsNone(guess_year(Path("misc/photo.jpg")))

    def test_process_image_creates_thumb_and_meta(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "2003 MR" / "img.jpg"; src.parent.mkdir()
            Image.new("RGB", (2000, 1500), "red").save(src, quality=95)
            out = Path(td) / "thumbs"
            meta = process_image(src, out, base=Path(td))
            self.assertTrue((out / meta["thumb"]).exists())
            self.assertEqual(meta["year"], 2003)
            self.assertLess((out / meta["thumb"]).stat().st_size, 80_000)

    def test_write_gallery_data_creates_year_index_and_files(self):
        items = [
            {"thumb": "a.webp", "year": 2003, "src": "photos/2003/a.jpg"},
            {"thumb": "b.webp", "year": 2003, "src": "photos/2003/b.jpg"},
            {"thumb": "c.webp", "year": None, "src": "photos/misc/c.jpg"},
        ]
        with tempfile.TemporaryDirectory() as td:
            data_dir = Path(td)
            write_gallery_data(items, data_dir)
            index = json.loads(
                (data_dir / "gallery-years" / "index.json").read_text())
            self.assertEqual(index[0]["year"], None)
            self.assertEqual(index[1]["year"], 2003)
            self.assertEqual(index[1]["count"], 2)
            year_items = json.loads(
                (data_dir / "gallery-years" / "2003.json").read_text())
            self.assertEqual(len(year_items), 2)

if __name__ == "__main__":
    unittest.main()
