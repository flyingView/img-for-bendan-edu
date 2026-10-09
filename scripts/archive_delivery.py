#!/usr/bin/env python3
"""Archive a delivered figure's process files, then clear its disposable cache."""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import stat
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_FOLDER = json.loads((ROOT / "assets/defaults.json").read_text(encoding="utf-8"))["task_root"]


def redirected(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) == 0xA0000003


def within(path: Path, task: Path) -> None:
    if path == task or not path.is_relative_to(task):
        raise ValueError(f"Path is outside the figure workspace: {path}")
    for part in (path, *path.parents):
        if redirected(part):
            raise ValueError(f"Linked paths are not archived or cleaned: {part}")
        if part == task:
            break
    if not path.resolve().is_relative_to(task):
        raise ValueError(f"Path resolves outside the figure workspace: {path}")


def collect(path: Path, task: Path) -> tuple[list[Path], list[Path]]:
    within(path, task)
    if not path.exists():
        return [], []
    if path.is_file():
        return [path], []
    if not path.is_dir():
        raise ValueError(f"Unsupported file type: {path}")
    files, directories = [], [path]
    for child in sorted(path.iterdir()):
        child_files, child_dirs = collect(child, task)
        files.extend(child_files)
        directories.extend(child_dirs)
    return files, directories


def fingerprint(path: Path) -> tuple[int, int, int, int]:
    info = path.stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def digest(stream) -> str:
    value = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        value.update(chunk)
    return value.hexdigest()


def verify_archive(archive: Path, task: Path, files: list[Path]) -> dict:
    signatures = {}
    with zipfile.ZipFile(archive) as bundle:
        for path in files:
            within(path, task)
            before = fingerprint(path)
            with path.open("rb") as source, bundle.open(path.relative_to(task).as_posix()) as stored:
                if digest(source) != digest(stored):
                    raise RuntimeError(f"Archive content differs from its source: {path}")
            if fingerprint(path) != before:
                raise RuntimeError(f"Source changed while being archived: {path}")
            signatures[path] = before
    return signatures


def remove_snapshot(files: list[Path], directories: list[Path], task: Path, signatures: dict) -> None:
    for path in files:
        within(path, task)
        if fingerprint(path) != signatures[path]:
            raise RuntimeError(f"File changed during cleanup; retained: {path}")
    for path in files:
        within(path, task)
        if fingerprint(path) != signatures[path]:
            raise RuntimeError(f"File changed during cleanup; retained: {path}")
        path.unlink()
    for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        within(directory, task)
        try:
            directory.rmdir()
        except OSError as error:
            if error.errno not in {errno.ENOTEMPTY, errno.EEXIST}:
                raise


def save_state(task: Path, state: dict) -> None:
    target = task / "task.json"
    within(target, task)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=task,
                                         prefix=".state-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        within(target, task)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            within(temporary, task)
            temporary.unlink(missing_ok=True)


def archive_delivery(project: Path, figure: str) -> dict:
    if not re.fullmatch(r"img[1-9][0-9]*", figure):
        raise ValueError("Use a figure ID such as img1.")
    project = project.expanduser().resolve(strict=True)
    root = project / TASK_FOLDER
    task = root / figure
    if redirected(root) or redirected(task) or task.resolve(strict=True).parent.parent != project:
        raise ValueError("The figure workspace must be an ordinary directory inside the paper project.")
    within(task / "task.json", task)
    state = json.loads((task / "task.json").read_text(encoding="utf-8"))
    if state.get("figure_id") != figure or state.get("stage") != "delivered":
        raise ValueError("Finish and verify delivery, then set task.json stage to delivered.")
    for folder in ("final", "redraw"):
        if not any(path.is_file() for path in (task / folder).rglob("*")):
            raise ValueError(f"Delivery requires files in {folder}/.")
    if not (task / "delivery.md").is_file():
        raise ValueError("Delivery requires delivery.md.")

    lock = task / ".archive.lock"
    within(lock, task)
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    archive = None
    verified = False
    try:
        candidates = [task / name for name in ("references", "generation", "comparisons")]
        candidates += [path for path in sorted(task.glob("review-*.md"))
                       if re.fullmatch(r"review-[0-9]+\.md", path.name)]
        files, directories = [], []
        for candidate in candidates:
            found_files, found_dirs = collect(candidate, task)
            files.extend(found_files)
            directories.extend(found_dirs)
        cache_files, cache_dirs = collect(task / ".work", task)
        cache_signatures = {path: fingerprint(path) for path in cache_files}
        if files:
            number = 1
            while True:
                candidate = task / ("process.zip" if number == 1 else f"process-{number:02d}.zip")
                within(candidate, task)
                try:
                    bundle = zipfile.ZipFile(candidate, "x", compression=zipfile.ZIP_DEFLATED)
                    archive = candidate
                    break
                except FileExistsError:
                    number += 1
            with bundle:
                for path in files:
                    within(path, task)
                    bundle.write(path, path.relative_to(task).as_posix())
            signatures = verify_archive(archive, task, files)
            verified = True
            state.setdefault("process_archives", []).append(archive.name)
            save_state(task, state)
            remove_snapshot(files, directories, task, signatures)
        else:
            remove_snapshot([], directories, task, {})
        remove_snapshot(cache_files, cache_dirs, task, cache_signatures)
        return {"figure": figure, "archive": str(archive) if archive else None,
                "archived_files": len(files), "cleared_cache_files": len(cache_files)}
    finally:
        if archive is not None and not verified:
            within(archive, task)
            archive.unlink(missing_ok=True)
        within(lock, task)
        lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--figure", required=True, help="Figure workspace ID, for example img1")
    args = parser.parse_args()
    try:
        print(json.dumps(archive_delivery(args.project, args.figure), ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Delivery archive failed: {error}\n")


if __name__ == "__main__":
    main()
