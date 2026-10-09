"""Exercise installation and ZIP import bundles in isolated directories."""

import json
import subprocess
import sys
import zipfile
from pathlib import Path

from test_helpers import IsolatedCase, load_script


installer = load_script("install")


class InstallTests(IsolatedCase):
    def setUp(self):
        super().setUp()
        self.payload = installer.read_payload()

    def test_profiles_install_complete_skills_under_the_given_home(self):
        home = self.directory / "home"
        expected = {
            "codex": ".agents", "claude-code": ".claude",
            "qwen-work": ".qwenworkcn", "qoder": ".qoder",
            "qwen-code": ".qwen", "qoder-work": ".qoderwork",
        }
        for agent, folder in expected.items():
            with self.subTest(agent=agent):
                root = installer.resolve_skills_root(agent, home=home)
                destination, changed = installer.install(root, self.payload)
                self.assertEqual(destination, home / folder / "skills" / installer.NAME)
                self.assertTrue(changed)
                for name, content in self.payload.items():
                    self.assertEqual((destination / name).read_bytes(), content)

    def test_project_scope_is_explicit_and_supported(self):
        for agent in ("codex", "claude-code", "qoder", "qwen-code"):
            with self.subTest(agent=agent):
                root = installer.resolve_skills_root(agent, project=self.directory)
                destination, _ = installer.install(root, self.payload)
                self.assertTrue(destination.is_relative_to(self.directory))
        for agent in ("qwen-work", "qoder-work"):
            with self.subTest(agent=agent), self.assertRaises(ValueError):
                installer.resolve_skills_root(agent, project=self.directory)

    def test_identical_install_is_unchanged_and_user_edits_are_preserved(self):
        root = self.directory / "skills"
        destination, _ = installer.install(root, self.payload)
        extra = destination / "user-notes.md"
        extra.write_text("Keep my notes.", encoding="utf-8")
        self.assertFalse(installer.install(root, self.payload)[1])
        edited = destination / "SKILL.md"
        edited.write_text("User modification", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            installer.install(root, self.payload)
        self.assertEqual(edited.read_text(encoding="utf-8"), "User modification")
        self.assertEqual(extra.read_text(encoding="utf-8"), "Keep my notes.")

    def test_installed_helper_runs_with_its_own_resources(self):
        destination, _ = installer.install(self.directory / "skills", self.payload)
        project = self.directory / "\u8bba\u6587-project"
        project.mkdir()
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(destination / "scripts/init_task.py"),
             "--project", str(project), "--papers", "12", "--rounds", "3"],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        task = Path(result.stdout.strip())
        state = json.loads((task / "task.json").read_text(encoding="utf-8"))
        self.assertEqual((state["paper_count"], state["expected_versions"]), (12, 4))
        self.assertEqual((task / "requirements.md").read_text(encoding="utf-8"),
                         self.payload["assets/templates/requirements.md"].decode("utf-8"))

    def test_zip_is_complete_portable_and_repeatable(self):
        output = self.directory / "skill.zip"
        self.assertTrue(installer.build_package(output, self.payload)[1])
        self.assertFalse(installer.build_package(output, self.payload)[1])
        with zipfile.ZipFile(output) as archive:
            prefix = installer.NAME + "/"
            self.assertEqual(set(archive.namelist()), {prefix + name for name in self.payload})
            self.assertIn(prefix + "SKILL.md", archive.namelist())
            self.assertNotIn(prefix + "README.md", archive.namelist())
            self.assertNotIn(prefix + "assets/brand/banner.png", archive.namelist())
            for name, content in self.payload.items():
                self.assertEqual(archive.read(prefix + name), content)
        before = output.read_bytes()
        changed = dict(self.payload, **{"SKILL.md": b"Different skill"})
        with self.assertRaises(FileExistsError):
            installer.build_package(output, changed)
        self.assertEqual(output.read_bytes(), before)
