#!/usr/bin/env python3
"""Install the portable skill for one agent, or build a standalone ZIP bundle."""

from __future__ import annotations

import argparse
import io
import os
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "img-for-bendan-edu"
# User and project skills roots, relative to the home and project directories.
PROFILES = {
    "codex": (".agents/skills", ".agents/skills"),
    "claude-code": (".claude/skills", ".claude/skills"),
    "qwen-work": (".qwenworkcn/skills", None),
    "qoder": (".qoder/skills", ".qoder/skills"),
    "qwen-code": (".qwen/skills", ".qwen/skills"),
    "qoder-work": (".qoderwork/skills", None),
}
RUNTIME_FILES = (
    "SKILL.md", "LICENSE", "requirements.txt", "agents/openai.yaml",
    "assets/defaults.json", "assets/brand/logo.png",
    "scripts/init_task.py", "scripts/pdf_figures.py",
)


def read_payload() -> dict[str, bytes]:
    paths = [ROOT / name for name in RUNTIME_FILES]
    for folder in ("references", "assets/templates"):
        supporting = sorted((ROOT / folder).glob("*.md"))
        if not supporting:
            raise FileNotFoundError(f"Missing supporting files in {folder}.")
        paths.extend(supporting)
    return {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in paths}


def resolve_skills_root(
    agent: str, home: Path | None = None, project: Path | None = None,
) -> Path:
    if agent not in PROFILES:
        raise ValueError(f"Unknown agent: {agent}")
    user_path, project_path = PROFILES[agent]
    if project is not None:
        if project_path is None:
            raise ValueError(f"{agent} uses a user installation; omit --project.")
        project = project.expanduser().resolve(strict=True)
        if not project.is_dir():
            raise ValueError("The project must be an existing directory.")
        return project / project_path
    return (Path.home() if home is None else home).expanduser().resolve() / user_path


def install(skills_root: Path, payload: dict[str, bytes]) -> tuple[Path, bool]:
    destination = skills_root.expanduser().resolve() / NAME
    if destination.exists():
        if destination.is_dir() and not destination.is_symlink() and all(
            (destination / name).is_file()
            and (destination / name).read_bytes() == content
            for name, content in payload.items()
        ):
            return destination, False
        raise FileExistsError(f"Existing installation differs and was preserved: {destination}")
    destination.mkdir(parents=True)
    for name, content in payload.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
    return destination, True


def build_package(output: Path, payload: dict[str, bytes]) -> tuple[Path, bool]:
    output = output.expanduser().resolve()
    if output.suffix.lower() != ".zip":
        raise ValueError("The package output must use a .zip extension.")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(payload.items()):
            entry = zipfile.ZipInfo(f"{NAME}/{name}", date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content)
    content = buffer.getvalue()
    if output.is_file() and output.read_bytes() == content:
        return output, False
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent, prefix=f".{output.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output, True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--agent", choices=tuple(PROFILES), help="Install for one host")
    action.add_argument("--dest", type=Path, help="Custom parent skills directory")
    action.add_argument("--package", type=Path, help="Build or refresh an importable .zip file")
    action.add_argument("--list", action="store_true", help="Show supported profiles")
    parser.add_argument("--project", type=Path, help="Existing project for a project-scoped installation")
    args = parser.parse_args()
    if args.project is not None and args.agent is None:
        parser.error("--project requires --agent.")
    if args.list:
        for profile, (user_path, project_path) in PROFILES.items():
            print(f"{profile}: ~/{user_path}; project: {project_path or 'user scope only'}")
        return
    try:
        payload = read_payload()
        if args.package is not None:
            path, changed = build_package(args.package, payload)
        else:
            root = args.dest if args.dest is not None else resolve_skills_root(args.agent, project=args.project)
            path, changed = install(root, payload)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Deployment failed: {error}\n")
    print(f"{'Created' if changed else 'Unchanged'}: {path}")


if __name__ == "__main__":
    main()
