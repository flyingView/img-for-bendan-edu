---
name: img-for-bendan-edu
description: Create scientific paper figures from a specific figure brief or by reading a manuscript and selecting useful illustration positions. Learn from reference-paper figures, compare and refine generated drafts, then rebuild the final figure with editable code or drawing software. Ask for paper count and refinement rounds at intake; recommend 20 papers and 5 rounds.
license: MIT
metadata:
  version: "0.2.0"
  language: "en"
---

# Academic Figure Studio

Learn from strong examples, make each comparison improve the next draft, and deliver an editable software reconstruction. Follow the author's workflow below; use the host agent's judgment and available tools for implementation.

## First action: ask for the two parameters

In the user's language, ask one short question as soon as this skill is invoked:

> How many reference papers and refinement rounds would you like? Recommended and default: **20 papers, 5 rounds**. You can reply with two numbers, such as **12 papers, 3 rounds**.

- `paper_count = P`: positive integer; default **20**.
- `refinement_rounds = R`: nonnegative integer; default **5**.
- Produce **R + 1 generated drafts** and **R review records**, then reconstruct the final draft with software. If R is 0, reconstruct after draft 1.
- Use values already specified in the request; ask only for missing values. On a resumed task, retain its recorded values unless the user changes them.
- Prefer the host's question tool. If it supports a nonblocking question, continue locating and reading the manuscript while the user considers it. Allow a reasonable reply window (about one minute) before applying defaults to unanswered fields. A skipped or empty answer uses defaults. With text-only interaction, ask once, state the defaults, and proceed with manuscript reading before settling unanswered fields. Do not repeatedly ask or wait indefinitely.
- Record the selected values and whether they came from the user or defaults. A later answer updates pending work without discarding completed artifacts.

## Figure expression rules

Apply these rules to every generation prompt, every review, and the software final:

1. **No small explanatory text.** Keep necessary labels, variables, panel letters and legends readable at manuscript size. Put explanations in the caption or body.
2. **No scope-boundary descriptions or defensive prose.** Express the main content directly; leave caveats, disclaimers and self-justification off the figure.
3. **Be concise and clear.** Use one main message, a visible hierarchy and an obvious reading order.
4. **No piles of AI-generated mini-icons.** Prefer consistent geometric elements and necessary domain symbols with clear meanings.
5. **Make legends clear.** Map colors, symbols and line types to meanings consistently; place the legend where readers can find it.
6. **Use a harmonious palette.** Learn a restrained set of colors from the references, emphasize the main path, and keep each meaning the same color.

## 1. Select the mode and create the figure workspace

Read [scenarios](references/scenarios.md). A **specific-figure** request starts from the user's brief. A **manuscript-illustration** request first identifies useful figure positions and produces a short whole-paper plan, then works figure by figure.

Create the task root named in [defaults](assets/defaults.json) inside the paper project, then `img1/`, `img2/`, and so on. Use the largest existing number plus one; resume the same figure in its existing folder. Keep all its materials and code there. The directory index is separate from its manuscript Figure number.

Optional helper, run from this skill's actual directory, replacing the example counts with the selected P and R:

```bash
python scripts/init_task.py --project "/path/to/paper" --mode single --papers 20 --rounds 5
```

Use `--mode manuscript` for whole-paper work. If Python is unavailable, create the same files directly. See [artifacts](references/artifacts.md) for names and resumption.

Use the host's search, PDF, vision, image-generation and drawing tools. No particular model, API provider, MCP server or extra skill is required by name. If a required capability is absent, finish independent work and identify the exact missing capability rather than claiming the stage completed.

## 2. Understand the manuscript and original request

Locate the intended manuscript version. Read its argument, methods, results, existing figures and captions, then closely read the material relevant to this figure.

Write `requirements.md`: preserve the original prompt; state the figure's main message, insertion anchor, objects and relationships, panel order, scientific sources, manuscript dimensions, language and proposed caption. Separate source facts from design choices. Use the [requirements template](assets/templates/requirements.md).

**Done when:** the content and position are clear, every scientific element has a source, and ambiguities affecting the scientific meaning are resolved.

## 3. Find P papers and extract their figures

Read the short [reference-learning guide](references/reference-learning.md). Keep this priority order:

1. Classic papers in the same field and the same narrow topic.
2. High-quality papers in that topic from the most recent 1-3 months.
3. Classic papers in the same field but other narrow topics.

Download accessible PDFs, verify their identities, and select at least one relevant complete figure from each. Keep page numbers, figure IDs, captions and source links. Inspect the figures themselves and record one useful observation per paper in `references/study-notes.md`; keep a labeled visual index for comparisons.

**Done when:** P distinct research works have local PDFs, inspected figures and usable notes. Report any shortfall and resolve access or selection before treating this stage as complete.

## 4. Turn observations into a style plan

Write `style-study.md`: **reference evidence → useful feature → application to this figure**. Separate information structure from visual styling. Define a small consistent set of layout, label, line, arrow, legend and color choices. Distinguish observed conventions from verified publisher requirements.

**Done when:** the plan can guide actual drawing and its main decisions point to reference figures. Use the [style template](assets/templates/style-study.md).

## 5. Generate draft 1 directly

Save `generation/prompt-01.md` before calling the image tool, then save and inspect `generation/v01.png` (or the tool's actual image format). Combine the requirements, style plan, exact labels and figure expression rules. Identify each reference input as style, palette or structure guidance.

Record the actual tool and available model information. Keep scientific relationships unchanged. For quantitative figures, derive the real chart layer from data; image generation explores layout or conceptual elements, and never becomes the source of numerical results.

## 6. Compare and refine for R rounds

Read [iteration review](references/iteration-review.md). For **n = 1 through R**:

1. Inspect draft n alongside the complete reference index, enlarging the most relevant examples. Check the preceding review's requested changes.
2. Write `review-{n:02d}.md`: what looks weaker than the examples, what feels unlike a paper figure in this field, observable AI-looking artifacts, missed lessons, and specific improvements. Anchor each issue to a location and reference; do not invent faults.
3. Save the next prompt and generate draft n+1. Inspect it for both the intended improvement and any scientific drift.
4. Save the result, add new lessons to `style-updates.md`, and update `task.json`.

**Done when:** there are R real reviews and R+1 real generated drafts with prompts. Stop generation at the selected count; carry remaining issues into reconstruction. Defaults give reviews 1-5 and drafts 1-6.

## 7. Reconstruct with code or drawing software

Read [reconstruction](references/reconstruction.md). Analyze the latest draft and choose the simplest available tool that can reproduce its layout, objects and typography closely. Write a brief `redraw/plan.md` and rebuild it with actual editable elements and source data.

Aim for near 1:1 visual fidelity while correcting scientific or generated errors. The final must contain **no AI-generated image layers**: embedding, automatic bitmap tracing, upscaling or format-converting the draft is not software reconstruction. Genuine research images may be used with their sources and processing records.

Open the exported final at manuscript size, check the figure and legend, and export once again from the saved source to verify reproducibility.

**Done when:** the final is scientifically correct, follows the expression rules, has editable source, and can be exported from that source.

## 8. Deliver and continue from feedback

Deliver the final preview, manuscript-ready format, editable source/code, reproduction steps, caption and insertion position in `delivery.md`. If insertion was requested and the manuscript is editable, insert the figure and verify caption, references and layout.

Wait for user feedback. Save later revisions within the same `imgN/`; edit the reconstructed source for local changes. Return to an earlier stage only when the scientific content or figure purpose changes.
