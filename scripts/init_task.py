#!/usr/bin/env python3
"""Create a numbered figure workspace using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = json.loads((SKILL_ROOT / "assets/defaults.json").read_text(encoding="utf-8"))
TASK_FOLDER = DEFAULTS["task_root"]
REFERENCE_FIELDS = [
    "paper_id", "title", "authors", "year", "published_date", "version_date",
    "priority", "selection_evidence", "doi_or_id", "landing_url", "pdf_url",
    "downloaded_at", "pdf_path", "pdf_sha256", "figure_ids", "figure_paths",
    "visually_checked", "notes",
]


def create_task(
    project: Path,
    mode: str = "single",
    paper_count: int | None = None,
    refinement_rounds: int | None = None,
) -> Path:
    papers = DEFAULTS["paper_count"] if paper_count is None else paper_count
    rounds = DEFAULTS["refinement_rounds"] if refinement_rounds is None else refinement_rounds
    for name, value, minimum in (("paper_count", papers, 1), ("refinement_rounds", rounds, 0)):
        if type(value) is not int or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}.")
    project = project.expanduser().resolve(strict=True)
    if not project.is_dir():
        raise ValueError("The paper project must be an existing directory.")
    if mode not in {"single", "manuscript"}:
        raise ValueError("mode must be single or manuscript.")
    template = (SKILL_ROOT / "assets/templates/requirements.md").read_text(
        encoding="utf-8"
    )
    root = project / TASK_FOLDER
    root.mkdir(exist_ok=True)
    if root.resolve().parent != project:
        raise ValueError("The task root must resolve inside the paper project.")

    # Exclusive creation keeps concurrent tasks from claiming the same number.
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

    for directory in ("references", "generation", "comparisons", "data", "redraw", "final"):
        (target / directory).mkdir()

    state = {
        "schema_version": 2,
        "figure_id": target.name,
        "manuscript_figure_number": None,
        "mode": mode,
        "paper_count": papers,
        "refinement_rounds": rounds,
        "expected_versions": rounds + 1,
        "parameter_sources": {
            "paper_count": "default" if paper_count is None else "argument",
            "refinement_rounds": "default" if refinement_rounds is None else "argument",
        },
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "requirements",
        "reference_papers_verified": 0,
        "completed_versions": [],
        "completed_reviews": [],
        "next_action": "Read the manuscript and user request; complete requirements.md.",
        "blockers": [],
    }
    (target / "task.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (target / "requirements.md").write_text(template, encoding="utf-8")
    with (target / "references/papers.csv").open(
        "x", encoding="utf-8-sig", newline=""
    ) as stream:
        csv.writer(stream).writerow(REFERENCE_FIELDS)

    if mode == "manuscript":
        try:
            with (root / "manuscript-plan.md").open("x", encoding="utf-8") as stream:
                stream.write(
                    "# Manuscript figure plan\n\n"
                    "Status: read the manuscript and complete this plan.\n\n"
                    "| Task ID | Insertion anchor | Main message | Visual need | Type and data source | Add/replace | Priority |\n"
                    "| --- | --- | --- | --- | --- | --- | --- |\n"
                )
        except FileExistsError:
            pass
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="Existing paper project directory")
    parser.add_argument("--mode", choices=("single", "manuscript"), default="single")
    parser.add_argument("--papers", type=int, help="Reference paper count (default: 20)")
    parser.add_argument("--rounds", type=int, help="Refinement rounds (default: 5)")
    args = parser.parse_args()
    try:
        target = create_task(args.project, args.mode, args.papers, args.rounds)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Initialization failed: {error}\n")
    print(target)


if __name__ == "__main__":
    main()
