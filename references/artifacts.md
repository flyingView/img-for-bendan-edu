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
    data/
    redraw/plan.md                    # plus editable source/code
    final/                           # outputs, caption, reproduction steps
    delivery.md
```

Use at least two digits for draft/review numbers and the actual image extension. R=0 creates no review files. Create templates when their stage starts, not an empty set that appears completed.

`task.json` records selected `paper_count`, `refinement_rounds`, derived `expected_versions`, actual completed drafts/reviews, verified-paper count and the next action. Update state after each stage and confirm it against actual files. When settings change, recalculate `expected_versions`, preserve completed work and record any work already beyond a reduced target.

On resume, read state, requirements, the current style plan and latest review. Continue older layouts in place, including Chinese filenames or separate learning logs. Retain recorded P/R; ask once if missing. Keep existing user files and names.
