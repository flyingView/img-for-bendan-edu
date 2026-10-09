# Files and resumption

The task-root name is stored in [defaults](../assets/defaults.json). It preserves the author's original workspace convention. Each new figure uses the next available `imgN`; continuing a figure reuses its folder.

```text
<paper-project>/<task-root>/
  manuscript-plan.md                 # manuscript mode only
  img1/
    task.json                        # selected P/R, progress, next action
    requirements.md
    references/
      papers.csv                     # sources, selection reasons, visual lessons
      reference-index.png
      P01/ ...                       # PDFs, pages, crops, captions
    style-study.md                   # search note and current style decisions
    generation/
      prompt-01.md ... prompt-{R+1}.md
      v01.png ... v{R+1}.png
    review-01.md ... review-{R}.md
    comparisons/
    .work/                           # disposable files and task-local caches
    data/
    redraw/plan.md                    # plus editable source/code
    final/                           # outputs, caption, reproduction steps
    delivery.md
```

Use at least two digits for draft/review numbers and the actual image extension. R=0 creates no review files. Create templates when their stage starts, not an empty set that appears completed.

`task.json` records selected `paper_count`, `refinement_rounds`, derived `expected_versions`, actual completed drafts/reviews, verified-paper count and the next action. Update state after each stage and confirm it against actual files. When settings change, recalculate `expected_versions`, preserve completed work and record any work already beyond a reduced target.

On resume, read state, requirements, the current style plan and latest review. Continue older layouts in place, including Chinese filenames or separate learning logs. Retain recorded P/R; ask once if missing. Keep existing user files and names.

## Delivery housekeeping

Once tools have finished and the delivered source has been re-exported successfully, set `task.json` stage to `delivered`. Ensure every file needed for future edits is in `data/`, `redraw/` or `final/`; `.work/` is disposable.

Run this helper from the installed skill directory:

```bash
python scripts/archive_delivery.py --project "/path/to/paper" --figure img1
```

The helper compresses `references/`, `generation/`, `comparisons/` and numbered `review-*.md` files into `imgN/process.zip`. It checks every archived file against its original with SHA-256 before removing those originals, then clears `.work/`. It preserves `final/`, `redraw/`, `data/`, requirements, the current style plan, delivery notes and task state. Later process batches use `process-02.zip`, and so on.

Record the archive path and cleanup result in `delivery.md`, then verify re-export from the retained source. Use archive paths when referring to earlier drafts or reviews. Restore selected process files inside this same `imgN/` when further reference study is needed; archived files are completed work, not missing work.

If Python is unavailable, use the host's archive tools with the same scope and verify the archive before removing originals. Keep anything whose role is unclear. The helper leaves older nonstandard filenames in place and rejects linked paths.
