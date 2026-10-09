# Install for an agent

This repository contains one standalone Agent Skill. Use the same skill files on every supported host. Installation needs only Python 3.10+; no API key, Node.js, plugin manifest or extra skill is needed.

## Agent deployment

1. Read `SKILL.md`. Identify the host the user wants to install into.
2. Run the matching command below from the repository root. Use `--project /path/to/project` only for an explicitly requested project installation; otherwise use the user scope.
3. Confirm that the returned directory contains `SKILL.md` and its supporting files. Reload the host's skills or start a new session, then check that `img-for-bendan-edu` appears in its available skills. Report file installation separately from host discovery if the host cannot be inspected here.

```bash
python scripts/install.py --agent codex
python scripts/install.py --agent claude-code
python scripts/install.py --agent qwen-work
python scripts/install.py --agent qoder
```

Run **one command for the intended host**, not the entire list. The installer makes no network requests, copies only runtime files, and leaves an identical installation unchanged. A different existing installation is preserved; inspect it before choosing a new destination or replacing it.

All bundled scripts, references and assets stay inside that single skill directory. Fetch the repository outside the paper project when preparing installation. To uninstall, use the host's skill manager or remove that exact `img-for-bendan-edu/` directory; paper figures remain in their own project workspace.

## Verified directory conventions

Paths checked against official documentation on 2026-10-09. Each destination below receives an `img-for-bendan-edu/` subfolder.

| Profile | User skills root | Project skills root | Source |
| --- | --- | --- | --- |
| `codex` | `~/.agents/skills/` | `.agents/skills/` | [Codex](https://learn.chatgpt.com/docs/build-skills) |
| `claude-code` | `~/.claude/skills/` | `.claude/skills/` | [Claude Code](https://code.claude.com/docs/en/skills) |
| `qwen-work` | `~/.qwenworkcn/skills/` | User scope | [Qwen Work CN](https://docs.qwenwork.cn/features/skills) |
| `qoder` | `~/.qoder/skills/` | `.qoder/skills/` | [Qoder IDE](https://docs.qoder.com/extensions/skills), [CLI](https://docs.qoder.com/cli/Skills) |
| `qwen-code` | `~/.qwen/skills/` | `.qwen/skills/` | [Qwen Code](https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/) |
| `qoder-work` | `~/.qoderwork/skills/` | User scope | [QoderWork](https://docs.qoder.com/qoderwork/skills) |

For another Agent Skills host or a customized local configuration, choose its actual skills root explicitly:

```bash
python scripts/install.py --dest "/path/to/skills"
```

This also supports an existing Codex setup that uses `~/.codex/skills`; choose its configured path instead of creating duplicate discoveries. `--dest` is the parent skills directory, not the skill directory itself. On Windows, `~` is the user's profile directory.

## ZIP or manual import

```bash
python scripts/install.py --package "dist/img-for-bendan-edu.zip"
```

Re-running the command refreshes that ZIP after source changes; identical contents leave it unchanged. The new build replaces the previous ZIP only after it has been written successfully.

The ZIP contains one `img-for-bendan-edu/` folder with `SKILL.md` at its root. Import the complete bundle in hosts with a local skill importer, or extract that folder into the documented skills root. Qoder desktop provides a [ZIP import](https://docs.qoder.com/qoder/skills); Qwen Work accepts the skill and its supporting files through its Skills UI. Preserve the whole directory, not only `SKILL.md`.

## Runtime capabilities

The workflow uses the host's literature search, PDF reading, vision, image generation and local code/drawing capabilities. Discover their actual names at runtime. Python helpers are optional; PDF helpers need the packages in `requirements.txt`. Use an existing suitable environment or create a `.venv/` inside the installed skill directory. The installer itself installs no Python packages.

Verify installation by checking host discovery. Invoke the skill by its name in natural language; host-specific slash or dollar syntax is optional.
