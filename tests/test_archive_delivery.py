"""Exercise delivery cleanup, reproducibility and preservation on failures."""

import json
import os
import subprocess
import sys
import unittest
import zipfile
from unittest.mock import patch

from test_helpers import IsolatedCase, init_task, load_script


archiver = load_script("archive_delivery")
installer = load_script("install")


class ArchiveDeliveryTests(IsolatedCase):
    def setUp(self):
        super().setUp()
        self.task = init_task.create_task(self.directory)
        self.state_path = self.task / "task.json"
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        state["stage"] = "delivered"
        self.state_path.write_text(json.dumps(state), encoding="utf-8")
        self.source = self.task / "redraw/render.py"
        self.source.write_text(
            '''from pathlib import Path
task = Path(__file__).resolve().parents[1]
color = (task / "data/color.txt").read_text().strip()
(task / "final/figure.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
    + f'<rect width="100" height="100" fill="{color}"/></svg>'
)
''',
            encoding="utf-8",
        )
        retained = {
            "data/color.txt": b"#356A73",
            "style-study.md": b"Current style decisions",
            "delivery.md": b"Editable SVG, source and data supplied.",
            "user-note.txt": b"User-owned note: retain.",
        }
        process = {
            "references/P01/paper.pdf": b"Reference PDF bytes",
            "references/P01/figure.png": b"Reference image bytes",
            "generation/v01.png": b"Generated draft bytes",
            "generation/prompt-01.md": b"Draft prompt",
            "comparisons/panel.png": b"Comparison bytes",
            "review-01.md": b"Review decisions",
        }
        for name, content in {**retained, **process, ".work/nested/cache.bin": b"Disposable"}.items():
            path = self.task / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.render()
        process["references/papers.csv"] = (self.task / "references/papers.csv").read_bytes()
        self.process = process
        self.retained = {name: (self.task / name).read_bytes() for name in (
            *retained, "requirements.md", ".gitignore", "redraw/render.py", "final/figure.svg"
        )}
        self.manuscript = self.directory / "manuscript.md"
        self.manuscript.write_text("The user's manuscript.", encoding="utf-8")

    def render(self):
        subprocess.run([sys.executable, "-X", "utf8", str(self.source)],
                       cwd=self.directory, capture_output=True, check=True)

    def archive(self):
        return archiver.archive_delivery(self.directory, self.task.name)

    def assert_originals_present(self):
        for name, content in self.process.items():
            self.assertEqual((self.task / name).read_bytes(), content)
        self.assertEqual((self.task / ".work/nested/cache.bin").read_bytes(), b"Disposable")
        self.assertFalse((self.task / ".archive.lock").exists())

    def test_archive_is_complete_and_retained_source_still_reexports(self):
        result = self.archive()
        with zipfile.ZipFile(result["archive"]) as bundle:
            self.assertIsNone(bundle.testzip())
            self.assertEqual(set(bundle.namelist()), set(self.process))
            for name, content in self.process.items():
                self.assertEqual(bundle.read(name), content)
        for name in ("references", "generation", "comparisons", ".work", "review-01.md"):
            self.assertFalse((self.task / name).exists())
        self.render()
        for name, content in self.retained.items():
            self.assertEqual((self.task / name).read_bytes(), content)
        self.assertEqual(self.manuscript.read_text(encoding="utf-8"), "The user's manuscript.")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["process_archives"], ["process.zip"])
        self.assertEqual(state["stage"], "delivered")
        self.assertEqual(result["archived_files"], len(self.process))
        self.assertEqual(result["cleared_cache_files"], 1)
        self.assertFalse((self.task / ".archive.lock").exists())

    def test_repeated_delivery_preserves_archives_and_numbers_new_batches(self):
        self.archive()
        first = (self.task / "process.zip").read_bytes()
        self.assertIsNone(self.archive()["archive"])
        self.assertFalse((self.task / "process-02.zip").exists())
        later = self.task / "generation/v02.png"
        later.parent.mkdir()
        later.write_bytes(b"Later draft")
        self.archive()
        self.assertEqual((self.task / "process.zip").read_bytes(), first)
        with zipfile.ZipFile(self.task / "process-02.zip") as bundle:
            self.assertEqual(bundle.namelist(), ["generation/v02.png"])
            self.assertEqual(bundle.read("generation/v02.png"), b"Later draft")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["process_archives"], ["process.zip", "process-02.zip"])

    def test_incomplete_delivery_and_invalid_figure_ids_preserve_everything(self):
        for figure in ("../img1", "img0", "img1/../../outside"):
            with self.subTest(figure=figure), self.assertRaises(ValueError):
                archiver.archive_delivery(self.directory, figure)
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        for change in ({"stage": "redraw"}, {"figure_id": "img99"}):
            with self.subTest(change=change):
                self.state_path.write_text(json.dumps(dict(state, **change)), encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.archive()
        self.state_path.write_text(json.dumps(state), encoding="utf-8")
        # Nonrecursive deletion of this test's generated output exercises the delivery gate.
        output = self.task / "final/figure.svg"
        self.assertTrue(output.resolve().is_relative_to(self.directory))
        output.unlink()
        with self.assertRaises(ValueError):
            self.archive()
        self.assert_originals_present()
        self.assertEqual(list(self.task.glob("process*.zip")), [])

    def test_failed_verification_keeps_originals_cache_and_previous_archive(self):
        previous = self.task / "process.zip"
        previous.write_bytes(b"An existing user archive")
        with patch.object(archiver, "verify_archive", side_effect=RuntimeError("Invalid archive")):
            with self.assertRaises(RuntimeError):
                self.archive()
        self.assert_originals_present()
        self.assertEqual(previous.read_bytes(), b"An existing user archive")
        self.assertFalse((self.task / "process-02.zip").exists())

    def test_file_changed_during_compression_is_not_deleted(self):
        original_write = zipfile.ZipFile.write
        victim = self.task / "generation/v01.png"

        def write_then_change(bundle, filename, *args, **kwargs):
            original_write(bundle, filename, *args, **kwargs)
            if filename == victim:
                victim.write_bytes(b"Draft updated by another process")

        with patch.object(zipfile.ZipFile, "write", write_then_change):
            with self.assertRaisesRegex(RuntimeError, "differs"):
                self.archive()
        self.process["generation/v01.png"] = b"Draft updated by another process"
        self.assert_originals_present()
        self.assertEqual(list(self.task.glob("process*.zip")), [])

    def test_file_changed_after_verification_is_retained_with_verified_archive(self):
        original_save = archiver.save_state

        def save_then_change(task, state):
            original_save(task, state)
            (task / "references/P01/paper.pdf").write_bytes(b"A later paper version")

        with patch.object(archiver, "save_state", save_then_change):
            with self.assertRaisesRegex(RuntimeError, "changed during cleanup"):
                self.archive()
        self.process["references/P01/paper.pdf"] = b"A later paper version"
        self.assert_originals_present()
        with zipfile.ZipFile(self.task / "process.zip") as bundle:
            self.assertEqual(bundle.read("references/P01/paper.pdf"), b"Reference PDF bytes")

    def test_failed_state_save_keeps_originals_and_removes_its_temporary_file(self):
        before = self.state_path.read_bytes()
        with patch.object(archiver.os, "replace", side_effect=OSError("State write failed")):
            with self.assertRaises(OSError):
                self.archive()
        self.assert_originals_present()
        self.assertEqual(self.state_path.read_bytes(), before)
        self.assertEqual(list(self.task.glob(".state-*.tmp")), [])
        with zipfile.ZipFile(self.task / "process.zip") as bundle:
            self.assertIsNone(bundle.testzip())

    def test_new_cache_files_created_after_the_snapshot_are_preserved(self):
        original_save = archiver.save_state

        def save_then_add(task, state):
            original_save(task, state)
            (task / ".work/new.bin").write_bytes(b"New work from another process")

        with patch.object(archiver, "save_state", save_then_add):
            self.archive()
        self.assertEqual((self.task / ".work/new.bin").read_bytes(), b"New work from another process")
        self.assertFalse((self.task / ".work/nested/cache.bin").exists())
        self.assertTrue((self.task / "process.zip").is_file())

    def test_linked_process_or_cache_directories_are_rejected(self):
        outside = self.directory / "outside-figure"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_bytes(b"Keep outside files")
        for folder in ("references", ".work"):
            with self.subTest(folder=folder):
                link = self.task / folder / "linked"
                try:
                    link.symlink_to(outside, target_is_directory=True)
                except OSError as error:
                    if os.name == "nt" and getattr(error, "winerror", None) == 1314:
                        self.skipTest("Windows symlinks require Developer Mode or privilege.")
                    raise
                try:
                    with self.assertRaisesRegex(ValueError, "Linked paths"):
                        self.archive()
                finally:
                    link.unlink()
                self.assert_originals_present()
                self.assertEqual(sentinel.read_bytes(), b"Keep outside files")

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_windows_junctions_preserve_their_targets(self):
        outside = self.directory / "junction-target"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_bytes(b"Keep junction target")
        for folder in ("references", ".work"):
            with self.subTest(folder=folder):
                link = self.task / folder / "linked"
                subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],
                               capture_output=True, check=True)
                try:
                    self.assertEqual(link.resolve(), outside.resolve())
                    with self.assertRaisesRegex(ValueError, "Linked paths"):
                        self.archive()
                finally:
                    # rmdir removes only the junction; never recursively delete its target.
                    link.rmdir()
                self.assert_originals_present()
                self.assertEqual(sentinel.read_bytes(), b"Keep junction target")

    def test_an_existing_archive_lock_is_preserved(self):
        lock = self.task / ".archive.lock"
        lock.write_text("Existing process", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.archive()
        self.assertEqual(lock.read_text(encoding="utf-8"), "Existing process")
        for name, content in self.process.items():
            self.assertEqual((self.task / name).read_bytes(), content)
        self.assertEqual(list(self.task.glob("process*.zip")), [])

    def test_installed_helper_archives_without_repository_dependencies(self):
        installed, _ = installer.install(self.directory / "client-skills", installer.read_payload())
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(installed / "scripts/archive_delivery.py"),
             "--project", str(self.directory), "--figure", self.task.name],
            cwd=self.directory, capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertEqual(json.loads(result.stdout)["archived_files"], len(self.process))
        self.assertTrue((self.task / "process.zip").is_file())
        self.render()


if __name__ == "__main__":
    unittest.main()
