---
name: img-for-bendan-edu
description: Create scientific figures from a figure brief or by reading a manuscript to select useful illustration positions. Learn from reference papers, refine generated drafts, then rebuild an editable final with code or drawing software.
license: MIT
metadata:
  version: "0.2.1"
  language: "en"
---

# Academic Figure Studio

Learn from strong paper figures, refine through comparison, then deliver an editable software reconstruction.

For an existing `imgN` task, read its saved state and resume at the unfinished stage. For local changes to a completed figure, edit its software source directly.

## New tasks: ask for the two parameters

For a new drawing task, ask in the user's language as soon as this skill is invoked. Use values already given; ask only for missing values. Resumed tasks retain their recorded settings.

> How many reference papers and refinement rounds would you like? Recommended and default: **20 papers, 5 rounds**. You can reply with two numbers, such as **12 papers, 3 rounds**.

- `paper_count = P` is a positive integer; `refinement_rounds = R` is a nonnegative integer. Produce **R + 1 generated drafts** and **R review records**. R=0 goes directly from draft 1 to reconstruction.
- Use the host's question tool when available. With asynchronous input, read the manuscript while allowing about a minute for a reply. For skipped or unanswered fields, announce the defaults and continue. In text-only interaction, ask once and state the defaults before continuing manuscript reading.
- Record P/R in `task.json`. Apply later answers to pending work while keeping completed artifacts.

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

Use the host's available search, PDF, vision, image-generation and drawing tools; no particular provider or extra skill is required. If a capability is missing, finish independent work and report the stage reached and what is needed next.

## 2. Understand the manuscript and original request

Locate the intended manuscript version. Read its argument, methods, results, existing figures and captions, then closely read the material relevant to this figure.

Write `requirements.md`: preserve the original prompt; state the figure's main message, insertion anchor, objects and relationships, panel order, scientific sources, manuscript dimensions, language and proposed caption. Separate source facts from design choices. Use the [requirements template](assets/templates/requirements.md).

**Done when:** the content and position are clear, every scientific element has a source, and ambiguities affecting the scientific meaning are resolved.

## 3. Find P papers and extract their figures

Read the short [reference-learning guide](references/reference-learning.md). Keep this priority order:

1. Classic papers in the same field and the same narrow topic.
2. High-quality papers in that topic from the most recent 1-3 months.
3. Classic papers in the same field but other narrow topics.

Download accessible PDFs, verify their identities, and inspect at least one relevant complete figure from each. Keep the source and one useful visual lesson per paper in `references/papers.csv`, with page/figure IDs and captions beside the extracted figures. Build a labeled visual index for comparisons.

**Done when:** P distinct research works have local PDFs, inspected figures and usable notes. Report any shortfall and resolve access or selection before treating this stage as complete.

## 4. Turn observations into a style plan

Write `style-study.md`: **reference evidence → useful feature → application to this figure**. Separate information structure from visual styling and define consistent layout, label, line, legend and color choices. Keep this as the current style plan throughout refinement; distinguish observed conventions from publisher requirements.

**Done when:** the plan can guide actual drawing and its main decisions point to reference figures. Use the [style template](assets/templates/style-study.md).

## 5. Generate draft 1 directly

Save `generation/prompt-01.md` before calling the image tool, then save and inspect `generation/v01.png` (or the tool's actual image format). Combine the requirements, style plan, exact labels and figure expression rules. Identify each reference input as style, palette or structure guidance.

Record the actual tool and available model information. Keep scientific relationships unchanged. For quantitative figures, derive the real chart layer from data; image generation explores layout or conceptual elements, and never becomes the source of numerical results.

## 6. Compare and refine for R rounds

Read [iteration review](references/iteration-review.md). For **n = 1 through R**:

1. Inspect draft n alongside the complete reference index, enlarging the most relevant examples. Check the preceding review's requested changes.
2. Write `review-{n:02d}.md` using the guide's five questions. Connect visible differences to specific edits and preserve what already works.
3. Save the next prompt and generate draft n+1. Pass draft n as the image-edit input when supported, otherwise use it as a visual reference. Inspect the result for intended improvements and scientific drift.
4. Fold useful new lessons into `style-study.md` and update `task.json`; each review retains the reasoning behind its changes.

**Done when:** there are R real reviews and R+1 real generated drafts with prompts. Stop generation at the selected count; carry remaining issues into reconstruction.

## 7. Reconstruct with code or drawing software

Read [reconstruction](references/reconstruction.md). Analyze the latest draft and choose the simplest available tool that can reproduce its layout, objects and typography closely. Write a brief `redraw/plan.md` and rebuild it with actual editable elements and source data.

Aim for near 1:1 visual fidelity while correcting scientific or generated errors. The final must contain **no AI-generated image layers**: embedding, automatic bitmap tracing, upscaling or format-converting the draft is not software reconstruction. Genuine research images may be used with their sources and processing records.

**Done when:** the final passes inspection at manuscript size, follows the expression rules, is scientifically correct, and has editable source verified by re-exporting it.

## 8. Deliver and continue from feedback

Deliver the final preview, manuscript-ready format, editable source/code, reproduction steps, caption and insertion position in `delivery.md`. If insertion was requested and the manuscript is editable, insert the figure and verify caption, references and layout.

Wait for user feedback and save later revisions within the same `imgN/`. Revisit earlier stages when the scientific content or figure purpose changes.
