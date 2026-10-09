# Compare, learn, refine

Use the P and R recorded in `task.json`. Each review turns draft n into draft n+1; stop after R reviews. Look across all P reference papers, then enlarge a few directly relevant figures (up to three when P is small).

Answer the author's five questions with visible evidence:

- What makes this draft visually weaker than the examples?
- What makes it unlike a paper figure in this field?
- Which observable details create an AI-generated look?
- What did the previous style study miss?
- What exactly should change next?

Use **location → reference figure → difference → action → acceptance condition**. Check scientific content first, then hierarchy, readability and visual consistency. Describe concrete artifacts, such as malformed labels or meaningless arrows.

Check all six [figure expression rules](../SKILL.md#figure-expression-rules) each round. Revisit the previous review's changes, preserve what works, and write the next prompt with those invariants. New lessons go into `style-updates.md`.

Spread attention over the available R rounds: structure, domain conventions, typography/color/legend, manuscript-size readability, and final reconstruction readiness. These are review topics, not five mandatory extra rounds. R=1 covers them together; R=0 proceeds from draft 1 to reconstruction.

If no defect is found, state that and its evidence; use a controlled visual alternative to test the design rather than fabricating criticism. Preserve regressions and failed attempts. A failed call or a renamed copy does not count as a new generated draft.

After draft R+1, do a final inspection and move unresolved issues into `redraw/plan.md`. This inspection does not start another generation round. Resume from actual artifacts, retaining selected settings and completed work.
