#!/usr/bin/env python3
"""为一张新图创建独立任务目录。仅使用 Python 标准库。"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TASK_FOLDER = "重型绘图任务"
REFERENCE_FIELDS = [
    "paper_id", "title", "authors", "year", "published_date", "version_date",
    "priority", "selection_evidence", "doi_or_id", "landing_url", "pdf_url",
    "downloaded_at", "pdf_path", "pdf_sha256", "figure_ids", "figure_paths",
    "visually_checked", "notes",
]


def create_task(project: Path, mode: str = "single") -> Path:
    project = project.expanduser().resolve(strict=True)
    if not project.is_dir():
        raise ValueError("论文项目路径必须是已经存在的目录。")
    if mode not in {"single", "manuscript"}:
        raise ValueError("mode 必须是 single 或 manuscript。")
    template = (SKILL_ROOT / "assets/templates/原始需求和内容理解规划.md").read_text(
        encoding="utf-8"
    )
    root = project / TASK_FOLDER
    root.mkdir(exist_ok=True)
    if root.resolve().parent != project:
        raise ValueError("重型绘图任务目录不能通过链接指向项目外。")

    # mkdir 的独占创建使两个同时开始的新任务不会占用同一个编号。
    while True:
        indices = [
            int(match.group(1))
            for child in root.iterdir()
            if (match := re.fullmatch(r"img([1-9][0-9]*)", child.name))
        ]
        target = root / f"img{max(indices, default=0) + 1}"
        try:
            target.mkdir()
            break
        except FileExistsError:
            continue

    for directory in ("参考文献", "生图", "对照", "数据", "重绘", "最终交付"):
        (target / directory).mkdir()

    state = {
        "schema_version": 1,
        "figure_id": target.name,
        "manuscript_figure_number": None,
        "mode": mode,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "requirements",
        "reference_papers_verified": 0,
        "completed_versions": [],
        "completed_reviews": [],
        "next_action": "阅读论文与用户要求，填写原始需求和内容理解规划.md。",
        "blockers": [],
    }
    (target / "任务状态.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (target / "原始需求和内容理解规划.md").write_text(template, encoding="utf-8")
    with (target / "参考文献/文献清单.csv").open(
        "x", encoding="utf-8-sig", newline=""
    ) as stream:
        csv.writer(stream).writerow(REFERENCE_FIELDS)

    if mode == "manuscript":
        try:
            with (root / "论文配图总规划.md").open("x", encoding="utf-8") as stream:
                stream.write(
                    "# 论文配图总规划\n\n"
                    "状态：待通读论文并填写。\n\n"
                    "| 任务编号 | 位置/源码锚点 | 核心信息 | 现有缺口 | 图类型与数据来源 | 新增/替换 | 优先级 |\n"
                    "| --- | --- | --- | --- | --- | --- | --- |\n"
                )
        except FileExistsError:
            pass
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="已存在的论文项目目录")
    parser.add_argument("--mode", choices=("single", "manuscript"), default="single")
    args = parser.parse_args()
    try:
        target = create_task(args.project, args.mode)
    except (OSError, ValueError) as error:
        parser.exit(1, f"初始化失败：{error}\n")
    print(target)


if __name__ == "__main__":
    main()
