# Files and resumption

The task-root name is stored in [defaults](../assets/defaults.json). It preserves the author's original workspace convention. Each new figure uses the next available `imgN`; continuing a figure reuses its folder.

```text
<paper-project>/<task-root>/
  manuscript-plan.md                 # manuscript mode only
  img1/
    task.json                        # selected P/R, progress, next action
    requirements.md
    references/
      papers.csv
      search-log.md
      study-notes.md
      reference-index.png
      P01/ ...                       # PDFs, pages, crops, captions
    style-study.md
    style-updates.md
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

`task.json` records selected `paper_count`, `refinement_rounds`, derived `expected_versions`, actual completed drafts/reviews, verified-paper count and the next action. The helper labels parameter sources as `argument` or `default`; update `argument` to `user` or `default` based on the intake. Update state after each stage; files and tool results are the evidence. Apply changed parameters to remaining work, keep earlier artifacts, and record any already-completed work beyond a newly reduced target.

On resume, read state plus the latest requirements and review, then check actual files before continuing. For older Chinese-language task files, read them in place and continue in that same figure folder; retain P/R if recorded, otherwise ask once and use the intake defaults. Do not migrate or rename existing user work automatically.
