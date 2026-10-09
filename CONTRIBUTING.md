# Contributing

Keep the author's workflow central: manuscript understanding, reference learning, generated drafts and comparisons, then editable software reconstruction. Paper count and review rounds are selected at intake, with defaults of 20 and 5.

Add only guidance that changes a useful decision. Keep supporting search and drawing hints short. Preserve the six figure expression rules and the host-neutral skill format.

Use English for skill files, templates, code comments and supporting documentation; keep README.md in Chinese. Use Chinese Git commit messages. Share only materials you may publish.

Run the relevant tests after script changes:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```
