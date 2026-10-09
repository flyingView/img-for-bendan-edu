"""验证编号、已有文件保护及PDF矢量/文字的完整渲染。"""

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pymupdf
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


init_task = load_script("init_task")
pdf_figures = load_script("pdf_figures")


class IsolatedCase(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="check-", dir=scratch)
        self.directory = Path(self.temporary.name).resolve()
        if not self.directory.is_relative_to(scratch.resolve()):
            raise RuntimeError("测试临时目录必须位于本仓库tmp目录内。")
        self.addCleanup(self.temporary.cleanup)


class InitTaskTests(IsolatedCase):
    def test_max_number_and_existing_files_preserved(self):
        first = init_task.create_task(self.directory)
        sentinel = first / "原始需求和内容理解规划.md"
        sentinel.write_text("已有用户内容", encoding="utf-8")
        (first.parent / "img7").mkdir()
        (first.parent / "img100-note").mkdir()
        created = init_task.create_task(self.directory, "manuscript")
        self.assertEqual(created.name, "img8")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "已有用户内容")
        state = json.loads((created / "任务状态.json").read_text(encoding="utf-8"))
        self.assertEqual(state["completed_versions"], [])
        self.assertEqual(state["reference_papers_verified"], 0)

    def test_manuscript_plan_not_overwritten(self):
        first = init_task.create_task(self.directory, "manuscript")
        plan = first.parent / "论文配图总规划.md"
        plan.write_text("已经完成的规划", encoding="utf-8")
        init_task.create_task(self.directory, "manuscript")
        self.assertEqual(plan.read_text(encoding="utf-8"), "已经完成的规划")

    def test_concurrent_initialization_has_unique_ids(self):
        # 分离进程验证真实文件系统竞争，避免仅测试一个Python线程中的编号计算。
        def invoke(_):
            result = subprocess.run(
                [sys.executable, "-X", "utf8", str(ROOT / "scripts/init_task.py"),
                 "--project", str(self.directory)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            return Path(result.stdout.strip()).name
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(invoke, range(3)))
        self.assertEqual(set(results), {"img1", "img2", "img3"})

    def test_invalid_project_fails_without_creating_directory(self):
        missing = self.directory / "不存在"
        with self.assertRaises(FileNotFoundError):
            init_task.create_task(missing)
        self.assertFalse(missing.exists())


class PdfFigureTests(IsolatedCase):
    def setUp(self):
        super().setUp()
        self.pdf = self.directory / "含矢量文字的示例.pdf"
        with pymupdf.open() as document:
            page = document.new_page(width=200, height=100)
            page.draw_rect(pymupdf.Rect(10, 10, 70, 70), color=(1, 0, 0), fill=(1, 0, 0))
            page.insert_text((90, 50), "VECTOR", fontsize=16, color=(0, 0, 0))
            second = document.new_page(width=200, height=100)
            second.draw_rect(pymupdf.Rect(10, 10, 70, 70), color=(1, 0, 0), fill=(1, 0, 0))
            second.set_rotation(90)
            document.save(self.pdf)

    def args(self, **overrides):
        values = dict(command="crop", pdf=self.pdf, out=self.directory / "图例",
                      dpi=72, page=1, box="0,0,1,1", figure_id="P01-Fig1")
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_vector_and_text_survive_rendering(self):
        with pymupdf.open(self.pdf) as document:
            self.assertEqual(document[0].get_images(), [])
        paths = pdf_figures.execute(self.args())
        with Image.open(paths[0]) as image:
            self.assertEqual(image.size, (200, 100))
            self.assertEqual(image.getpixel((30, 30)), (255, 0, 0))
            text_pixels = list(image.crop((85, 25, 190, 55)).getdata())
            self.assertTrue(any(max(pixel) < 80 for pixel in text_pixels))
        record = json.loads(paths[1].read_text(encoding="utf-8"))
        self.assertEqual(record["pdf_sha256"], hashlib.sha256(self.pdf.read_bytes()).hexdigest())
        self.assertEqual(record["page_1_based"], 1)
        self.assertFalse(record["visually_verified"])

    def test_rotated_page_coordinates_match_visible_page(self):
        paths = pdf_figures.execute(self.args(page=2, box="0.25,0.05,0.95,0.4"))
        with Image.open(paths[0]) as image:
            self.assertEqual(image.size, (70, 70))
            self.assertEqual(image.getpixel((25, 20)), (255, 0, 0))

    def test_render_pages_and_no_overwrite(self):
        args = self.args(command="render", pages="1-2,1")
        paths = pdf_figures.execute(args)
        self.assertEqual(len(paths), 2)
        before = paths[0].read_bytes()
        with self.assertRaises(FileExistsError):
            pdf_figures.execute(args)
        self.assertEqual(paths[0].read_bytes(), before)

    def test_crop_no_overwrite(self):
        args = self.args()
        paths = pdf_figures.execute(args)
        before = paths[0].read_bytes()
        with self.assertRaises(FileExistsError):
            pdf_figures.execute(args)
        self.assertEqual(paths[0].read_bytes(), before)

    def test_invalid_coordinates_and_pages(self):
        for box in ("0,0,2,1", "0.8,0,0.1,1", "nan,0,1,1", "0,1,2"):
            with self.subTest(box=box), self.assertRaises(ValueError):
                pdf_figures.execute(self.args(box=box))
        for page in (0, 3):
            with self.subTest(page=page), self.assertRaises(ValueError):
                pdf_figures.execute(self.args(page=page))
        self.assertFalse((self.directory / "图例").exists())

    def test_path_traversal_and_invalid_pdf_rejected(self):
        with self.assertRaises(ValueError):
            pdf_figures.execute(self.args(figure_id="../../escape"))
        invalid = self.directory / "error.pdf"
        invalid.write_text("<html>Not a PDF</html>", encoding="utf-8")
        with self.assertRaises(Exception):
            pdf_figures.execute(self.args(pdf=invalid))
        self.assertFalse((self.directory / "图例").exists())


if __name__ == "__main__":
    unittest.main()
