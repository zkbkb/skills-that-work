# skills-that-work

Useful time-tested skills I have been using over and over again.

`skills-that-work` is a curated, source-tracked Agent Skills bundle. The repository stores local installable copies of selected skills while preserving their upstream source information in `upstream-sources.json`. The first version imports skills from [`zkbkb/thinkbench-skills`](https://github.com/zkbkb/thinkbench-skills) at commit `7c85489e7b60d1abdecfdc0ae920d05a27896447`.

## Install

### Claude Code

```text
/plugin marketplace add zkbkb/skills-that-work
```

### Manus

Use the import links in the table below to import individual skills from this bundled repository.

## Skills

| Skill | Description | Source | Local Path | Import |
|---|---|---|---|---|
| [context-handoff](skills/thinkbench-skills/context-handoff/SKILL.md) | Generate structured context handoff documents that capture the essential state of a conversation for seamless continuation in a new session. Use this skill when the user wants to carry over context from the current conv… | [thinkbench-skills](https://github.com/zkbkb/thinkbench-skills/tree/7c85489e7b60d1abdecfdc0ae920d05a27896447/skills/context-handoff) | `skills/thinkbench-skills/context-handoff` | [Import](https://manus.im/app#settings/skills/import?githubUrl=https://github.com/zkbkb/skills-that-work/tree/main/skills/thinkbench-skills/context-handoff) |
| [doc-diff](skills/thinkbench-skills/doc-diff/SKILL.md) | Generate Obsidian-compatible Markdown tracked-changes documents that show the differences between two versions of the same document. Use this skill whenever the user provides two versions of a file and asks to compare,… | [thinkbench-skills](https://github.com/zkbkb/thinkbench-skills/tree/7c85489e7b60d1abdecfdc0ae920d05a27896447/skills/doc-diff) | `skills/thinkbench-skills/doc-diff` | [Import](https://manus.im/app#settings/skills/import?githubUrl=https://github.com/zkbkb/skills-that-work/tree/main/skills/thinkbench-skills/doc-diff) |
| [doc-merge](skills/thinkbench-skills/doc-merge/SKILL.md) | Multi-document semantic comparison, difference diagnosis, and interactive merge resolution. Use when the user uploads or references multiple documents on the same topic and wants to compare, contrast, reconcile, or merg… | [thinkbench-skills](https://github.com/zkbkb/thinkbench-skills/tree/7c85489e7b60d1abdecfdc0ae920d05a27896447/skills/doc-merge) | `skills/thinkbench-skills/doc-merge` | [Import](https://manus.im/app#settings/skills/import?githubUrl=https://github.com/zkbkb/skills-that-work/tree/main/skills/thinkbench-skills/doc-merge) |
| [qi-gua](skills/thinkbench-skills/qi-gua/SKILL.md) | 基于梅花易数与六爻纳甲的通用起卦占卜技能。当用户希望通过易学方法进行占卜分析时 触发此技能。触发短语包括但不限于："帮我起一卦"、"帮我算一卦"、"我想占卜一下"、 "起卦看看"、"帮我卜一卦"、"梅花易数占卜"、"六爻占卜"、"qi gua"、"divination"。 适用于任何占问主题——事业、感情、决策、出行、健康、财运、人际、时机判断等， 不限于特定场景。当用户的意图是通过易学卦象获取分析和指引时，均应触发此技能。 | [thinkbench-skills](https://github.com/zkbkb/thinkbench-skills/tree/7c85489e7b60d1abdecfdc0ae920d05a27896447/skills/qi-gua) | `skills/thinkbench-skills/qi-gua` | [Import](https://manus.im/app#settings/skills/import?githubUrl=https://github.com/zkbkb/skills-that-work/tree/main/skills/thinkbench-skills/qi-gua) |
| [sutong-tutorial](skills/thinkbench-skills/sutong-tutorial/SKILL.md) | Generate high-density knowledge speed-through tutorials (高密度知识速通教程) that help readers achieve deep understanding with minimal cognitive load. Use this skill when the user requests to "speed through" (速通) a topic or asks… | [thinkbench-skills](https://github.com/zkbkb/thinkbench-skills/tree/7c85489e7b60d1abdecfdc0ae920d05a27896447/skills/sutong-tutorial) | `skills/thinkbench-skills/sutong-tutorial` | [Import](https://manus.im/app#settings/skills/import?githubUrl=https://github.com/zkbkb/skills-that-work/tree/main/skills/thinkbench-skills/sutong-tutorial) |
| [transcript](skills/thinkbench-skills/transcript/SKILL.md) | Export the current conversation as a structured transcript file preserving all user inputs and AI responses in chronological order. Use this skill when the user wants to save, export, or download the current conversatio… | [thinkbench-skills](https://github.com/zkbkb/thinkbench-skills/tree/7c85489e7b60d1abdecfdc0ae920d05a27896447/skills/transcript) | `skills/thinkbench-skills/transcript` | [Import](https://manus.im/app#settings/skills/import?githubUrl=https://github.com/zkbkb/skills-that-work/tree/main/skills/thinkbench-skills/transcript) |

## Skills by Category

| Category | Skills |
|---|---|
| `comparison` | `doc-diff` |
| `conversation` | `context-handoff`, `transcript` |
| `cultural-methods` | `qi-gua` |
| `decision-support` | `qi-gua` |
| `divination` | `qi-gua` |
| `documentation` | `transcript` |
| `documents` | `doc-diff`, `doc-merge` |
| `education` | `sutong-tutorial` |
| `export` | `transcript` |
| `learning` | `sutong-tutorial` |
| `merge` | `doc-merge` |
| `productivity` | `context-handoff` |
| `review` | `doc-diff`, `doc-merge` |
| `workflow` | `context-handoff` |
| `writing` | `sutong-tutorial` |

## Upstream Sources

| Source | Repository | Skills Used | Pinned Commit | Licence | Sync Policy |
|---|---|---|---|---|---|
| `thinkbench-skills` | [https://github.com/zkbkb/thinkbench-skills](https://github.com/zkbkb/thinkbench-skills) | `context-handoff`, `doc-diff`, `doc-merge`, `qi-gua`, `sutong-tutorial`, `transcript` | `7c85489e7b60d1abdecfdc0ae920d05a27896447` | MIT | `manual-review` |

## Repository Structure

```text
skills-that-work/
├── README.md
├── CHANGELOG.md
├── NOTICE.md
├── upstream-sources.json
├── skills.json
├── .claude-plugin/
│   └── marketplace.json
├── skills/
│   └── thinkbench-skills/
│       ├── context-handoff/
│       ├── doc-diff/
│       ├── doc-merge/
│       ├── qi-gua/
│       ├── sutong-tutorial/
│       └── transcript/
└── third_party/
    └── thinkbench-skills/
        └── LICENSE
```

## Source Tracking

All skills in this repository are local vendored copies grouped by upstream repository. `upstream-sources.json` is the machine-readable source registry, `skills.json` is the installable skill index, and `CHANGELOG.md` records import and update history. The copied upstream licence is preserved under `third_party/thinkbench-skills/LICENSE`.

## Licence

This bundle is released under the MIT Licence. Vendored content from `zkbkb/thinkbench-skills` is MIT-licensed; see `NOTICE.md` and `third_party/thinkbench-skills/LICENSE` for attribution details.
