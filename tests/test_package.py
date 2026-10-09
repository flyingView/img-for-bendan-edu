"""Check the skill entry point, metadata, local links and brand assets."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_skill_frontmatter(self):
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", content, re.S)
        self.assertIsNotNone(match)
        data = yaml.safe_load(match.group(1))
        self.assertEqual(data["name"], "img-for-bendan-edu")
        self.assertTrue(0 < len(data["description"]) <= 1024)
        self.assertNotRegex(content, r"\[TODO:")

    def test_ui_metadata_and_icons(self):
        data = yaml.safe_load((ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
        interface = data["interface"]
        self.assertIn("$img-for-bendan-edu", interface["default_prompt"])
        self.assertTrue(25 <= len(interface["short_description"]) <= 64)
        for key in ("icon_small", "icon_large"):
            with Image.open(ROOT / interface[key]) as image:
                image.verify()

    def test_internal_links_resolve(self):
        paths = [path for path in ROOT.rglob("*.md")
                 if not any(part in {".git", "tmp", ".venv", "dist"} for part in path.parts)]
        for path in paths:
            content = path.read_text(encoding="utf-8")
            targets = re.findall(r"\]\(([^)]+)\)", content)
            targets += re.findall(r'(?:src|href)="([^"]+)"', content)
            for target in targets:
                if urlsplit(target).scheme or target.startswith("#"):
                    continue
                filename = unquote(target.split("#", 1)[0])
                with self.subTest(file=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / filename).exists())

    def test_brand_assets_open(self):
        with Image.open(ROOT / "assets/brand/logo.png") as image:
            self.assertIn("A", image.getbands())
            self.assertEqual(image.getchannel("A").getextrema()[0], 0)
        with Image.open(ROOT / "assets/brand/banner.png") as image:
            self.assertGreater(image.width / image.height, 2)
            image.verify()


if __name__ == "__main__":
    unittest.main()
