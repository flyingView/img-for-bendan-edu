# Selected upstream ideas

Reviewed on 2026-10-09. Stars below are repository-wide GitHub API snapshots, not scores for individual skills. The author's workflow remains the source of the stage order; only a few implementation cues were adapted in original wording. No upstream scripts or extra skills are bundled.

| Repository | Stars observed | Material consulted | Small ideas retained |
| --- | ---: | --- | --- |
| [anthropics/skills](https://github.com/anthropics/skills) | 180,015 | [canvas-design](https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md) | Use hierarchy, spacing and composition to reduce explanatory prose. |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 48,076 | [scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md), [scientific-schematics](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-schematics/SKILL.md), [literature-review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/literature-review/SKILL.md) | Check final physical size, color meaning, scientific relationships and export behavior; use topic-aware search, source verification and version deduplication. |
| [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | 26,444 | [baoyu-infographic](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/SKILL.md) | Separate layout from style; save prompts before rendering; identify reference roles; resolve host-native capabilities. |

Search guidance lives in [reference learning](../references/reference-learning.md); drawing cues live in [reconstruction](../references/reconstruction.md). The source projects' broader workflows, fixed providers, extra approval gates and review-length conventions are not dependencies of this skill.

# Packaging references

The package follows the [Agent Skills specification](https://agentskills.io/specification): a directory with a `SKILL.md` entry point and local supporting files. It uses portable frontmatter and no mandatory host-specific tools or hooks. `agents/openai.yaml` is optional Codex display metadata. Platform paths and deployment instructions are in [INSTALL.md](../INSTALL.md).

# Existing branding

The icon and Chinese README banner were made with built-in imagegen on 2026-10-09. The original prompts are preserved in [brand/prompts.json](../assets/brand/prompts.json). The banner is a README asset and is excluded from the installable skill package.
