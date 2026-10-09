# Reference learning

The goal is a useful visual reference set of P papers. Keep the priority order in the main workflow; use these lightweight search cues:

1. Combine the narrow research topic, its main synonyms and the intended figure type. Start with representative citations already in the manuscript; use a field-appropriate scholarly source and follow relevant references or citing papers.
2. Screen relevance from title/abstract, then assess the actual paper and figure. Keep the search date, useful queries and selection reason in a short `references/search-log.md`.
3. Check title, authors, publication date and DOI/arXiv identity against the source page and PDF. Merge duplicate hits and preprint/published versions of the same work. A registered DOI alone does not verify content.
4. Interpret recent as the rolling last three calendar months, including the latest month. Explain why a paper is classic or high quality; use topic fit and figure usefulness rather than citation count alone.
5. Prefer publisher, proceedings, institutional or author-hosted PDFs. If access fails, seek an accessible version or a suitable replacement at the same priority before broadening the topic.

Save each paper under `references/P01/`, `P02/`, and onward. Record identity, selection reason, source URL, local PDF, page/figure IDs and inspected figure paths in `references/papers.csv`. Keep at least one meaningful visual lesson per paper in `references/study-notes.md`.

## Extract complete figures

Render the full PDF page first, then crop the complete figure region. Embedded bitmap extraction can lose independently drawn labels, legends and vector lines. Preserve the full page and caption so the crop can be checked.

Optional helper:

```bash
python scripts/pdf_figures.py render --pdf "paper.pdf" --pages 3,5-6 --out "pages"
python scripts/pdf_figures.py crop --pdf "paper.pdf" --page 5 --box 0.08,0.12,0.92,0.58 --figure-id P01-Fig2 --out "figures"
```

Pages start at 1. Crop coordinates are normalized left/top/right/bottom coordinates of the displayed page. Inspect the result; the helper does not identify figure boundaries or judge quality.

## Learn useful rules

Build a labeled reference index covering all P papers. Compare at similar display sizes and zoom in for details. Record layout and visual style separately, then connect each useful observation to an action in `style-study.md`.

Use spacing, alignment and hierarchy to reduce explanatory text. Choose colors by meaning: categories, magnitude, or deviation need different mappings. Record a single consistent mapping for labels, symbols and arrows. Keep exceptions that help explain when a visual convention does not fit this figure.

Reference figures teach visual methods; scientific content comes from the user's paper and data.
