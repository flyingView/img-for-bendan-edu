# Validation

Checked on Windows with Python 3.13.5 on 2026-10-09.

- Skill Creator's `quick_validate.py`: passed.
- `python -X utf8 -m unittest discover -s tests -v`: 23 tests passed.
- Task helpers: default 20/5, custom 12/3, zero refinement rounds, concurrent numbering, existing-file preservation and Unicode paths.
- PDF helpers: vector/text retention, displayed-page rotation, crop coordinates and source records.
- Deployment: six profile destinations in isolated directories, supported project scopes, repeat installation, preservation of user edits and execution from an installed copy.
- Package: complete standalone ZIP, repeatable contents, atomic rebuilds, preservation of the previous ZIP after a failed replacement, local links and Codex display metadata.

Host directory conventions were checked against the official sources linked in [INSTALL.md](../INSTALL.md). Validation covers files and local helper execution; in-app skill discovery was not exercised for each client. GitHub Actions is configured for Windows and Ubuntu with Python 3.10 and 3.13; remote CI results are produced after upload.

## Repeat the local checks

```bash
python -m pip install -r requirements-dev.txt
python -X utf8 -m unittest discover -s tests -v
python scripts/install.py --package dist/img-for-bendan-edu.zip
```
