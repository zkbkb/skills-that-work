#!/usr/bin/env python3
"""Build metadata files for the skills-that-work bundle."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "thinkbench-skills"
SOURCE_REPO_GIT = "https://github.com/zkbkb/thinkbench-skills.git"
SOURCE_REPO_WEB = "https://github.com/zkbkb/thinkbench-skills"
TARGET_REPO_WEB = "https://github.com/zkbkb/skills-that-work"
SOURCE_LOCAL = Path("/home/ubuntu/thinkbench-skills")
IMPORT_DATE = date.today().isoformat()

CATEGORY_TAGS = {
    "context-handoff": {
        "categories": ["conversation", "workflow", "productivity"],
        "tags": ["context", "handoff", "continuation", "session"],
    },
    "transcript": {
        "categories": ["conversation", "export", "documentation"],
        "tags": ["transcript", "archive", "conversation", "markdown"],
    },
    "doc-diff": {
        "categories": ["documents", "comparison", "review"],
        "tags": ["diff", "documents", "comparison", "review"],
    },
    "doc-merge": {
        "categories": ["documents", "merge", "review"],
        "tags": ["merge", "documents", "alignment", "resolution"],
    },
    "qi-gua": {
        "categories": ["divination", "decision-support", "cultural-methods"],
        "tags": ["qi-gua", "meihua-yishu", "liuyao", "divination"],
    },
    "sutong-tutorial": {
        "categories": ["learning", "education", "writing"],
        "tags": ["tutorial", "speed-through", "learning", "first-principles"],
    },
}


def run(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    block = match.group(1).splitlines()
    data: dict[str, str] = {}
    i = 0
    while i < len(block):
        line = block[i]
        if not line.strip() or ":" not in line or line.startswith(" "):
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value in {">", "|"}:
            collected: list[str] = []
            i += 1
            while i < len(block):
                nxt = block[i]
                if nxt and not nxt.startswith(" ") and ":" in nxt:
                    break
                collected.append(nxt.strip())
                i += 1
            data[key] = " ".join(part for part in collected if part).strip()
            continue
        data[key] = value
        i += 1
    return data


def short_description(description: str, limit: int = 220) -> str:
    description = " ".join(description.split())
    if len(description) <= limit:
        return description
    return description[: limit - 1].rstrip() + "…"


def skill_rows(commit: str) -> list[dict]:
    base = ROOT / "skills" / SOURCE_ID
    rows: list[dict] = []
    for skill_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        text = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = fm.get("name", skill_dir.name)
        description = short_description(fm.get("description", ""))
        rel_local = skill_dir.relative_to(ROOT).as_posix()
        upstream_path = f"skills/{skill_dir.name}"
        categories = CATEGORY_TAGS.get(skill_dir.name, {}).get("categories", ["uncategorised"])
        tags = CATEGORY_TAGS.get(skill_dir.name, {}).get("tags", [skill_dir.name])
        rows.append(
            {
                "name": name,
                "directory": skill_dir.name,
                "description": description,
                "upstream_path": upstream_path,
                "local_path": rel_local,
                "skill_file": f"{rel_local}/SKILL.md",
                "pinned_commit": commit,
                "licence": "MIT",
                "local_modifications": False,
                "sync_policy": "manual-review",
                "categories": categories,
                "tags": tags,
            }
        )
    return rows


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_upstream_sources(rows: list[dict], commit: str) -> None:
    payload = {
        "schema_version": "1.0",
        "repository": TARGET_REPO_WEB,
        "description": "A curated, source-tracked bundle of Agent Skills that have proven useful in repeated workflows.",
        "sources": [
            {
                "source_id": SOURCE_ID,
                "repository": SOURCE_REPO_GIT,
                "homepage": SOURCE_REPO_WEB,
                "default_ref": "main",
                "pinned_commit": commit,
                "licence": "MIT",
                "local_root": f"skills/{SOURCE_ID}",
                "skills": [
                    {
                        "name": row["name"],
                        "upstream_path": row["upstream_path"],
                        "local_path": row["local_path"],
                        "ref": "main",
                        "pinned_commit": row["pinned_commit"],
                        "imported_at": IMPORT_DATE,
                        "licence": row["licence"],
                        "local_modifications": row["local_modifications"],
                        "sync_policy": row["sync_policy"],
                        "categories": row["categories"],
                        "tags": row["tags"],
                    }
                    for row in rows
                ],
            }
        ],
    }
    write_json(ROOT / "upstream-sources.json", payload)


def build_skills_json(rows: list[dict]) -> None:
    payload = {
        "schema_version": "1.0",
        "name": "skills-that-work",
        "repository": TARGET_REPO_WEB,
        "description": "A curated, source-tracked bundle of installable Agent Skills.",
        "skills": [
            {
                "name": row["name"],
                "path": row["local_path"],
                "skill_file": row["skill_file"],
                "source_id": SOURCE_ID,
                "description": row["description"],
                "categories": row["categories"],
                "tags": row["tags"],
                "upstream": {
                    "repository": SOURCE_REPO_WEB,
                    "path": row["upstream_path"],
                    "commit": row["pinned_commit"],
                },
                "import_urls": {
                    "github": f"{TARGET_REPO_WEB}/tree/main/{row['local_path']}",
                    "manus": f"https://manus.im/app#settings/skills/import?githubUrl={TARGET_REPO_WEB}/tree/main/{row['local_path']}",
                },
            }
            for row in rows
        ],
    }
    write_json(ROOT / "skills.json", payload)


def build_marketplace(rows: list[dict]) -> None:
    payload = {
        "name": "skills-that-work",
        "owner": {"name": "zkbkb"},
        "metadata": {
            "description": "A curated bundle of time-tested Agent Skills synced from upstream repositories.",
            "version": "0.1.0",
        },
        "plugins": [
            {
                "name": "skills-that-work-core",
                "description": "Useful time-tested skills grouped by upstream repository and reviewed for repeated use.",
                "source": "./",
                "strict": False,
                "skills": [f"./{row['local_path']}" for row in rows],
                "category": "productivity",
                "tags": ["agent-skills", "curated", "workflow", "source-tracked"],
            }
        ],
    }
    path = ROOT / ".claude-plugin" / "marketplace.json"
    path.parent.mkdir(exist_ok=True)
    write_json(path, payload)


def build_readme(rows: list[dict], commit: str) -> None:
    skill_table = [
        "| Skill | Description | Source | Local Path | Import |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        import_url = f"https://manus.im/app#settings/skills/import?githubUrl={TARGET_REPO_WEB}/tree/main/{row['local_path']}"
        skill_link = f"[{row['name']}]({row['skill_file']})"
        source_link = f"[{SOURCE_ID}]({SOURCE_REPO_WEB}/tree/{commit}/{row['upstream_path']})"
        skill_table.append(
            f"| {skill_link} | {row['description']} | {source_link} | `{row['local_path']}` | [Import]({import_url}) |"
        )

    category_map: dict[str, list[str]] = {}
    for row in rows:
        for category in row["categories"]:
            category_map.setdefault(category, []).append(row["name"])
    category_table = ["| Category | Skills |", "|---|---|"]
    for category in sorted(category_map):
        category_table.append(f"| `{category}` | {', '.join(f'`{name}`' for name in sorted(category_map[category]))} |")

    text = f"""# skills-that-work

Useful time-tested skills I have been using over and over again.

`skills-that-work` is a curated, source-tracked Agent Skills bundle. The repository stores local installable copies of selected skills while preserving their upstream source information in `upstream-sources.json`. The first version imports skills from [`zkbkb/thinkbench-skills`]({SOURCE_REPO_WEB}) at commit `{commit}`.

## Install

### Claude Code

```text
/plugin marketplace add zkbkb/skills-that-work
```

### Manus

Use the import links in the table below to import individual skills from this bundled repository.

## Skills

{chr(10).join(skill_table)}

## Skills by Category

{chr(10).join(category_table)}

## Upstream Sources

| Source | Repository | Skills Used | Pinned Commit | Licence | Sync Policy |
|---|---|---|---|---|---|
| `{SOURCE_ID}` | [{SOURCE_REPO_WEB}]({SOURCE_REPO_WEB}) | {', '.join(f'`{row["name"]}`' for row in rows)} | `{commit}` | MIT | `manual-review` |

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
"""
    (ROOT / "README.md").write_text(text, encoding="utf-8")


def build_changelog(rows: list[dict], commit: str) -> None:
    added = "\n".join(
        f"- Added `{row['name']}` from `{SOURCE_ID}`, upstream path `{row['upstream_path']}`, pinned commit `{commit}`."
        for row in rows
    )
    text = f"""# Changelog

All notable changes to `skills-that-work` are documented here.

## {IMPORT_DATE}

### Added

{added}

### Changed

- Initial curated skills bundle structure created with `README.md`, `upstream-sources.json`, `skills.json`, `.claude-plugin/marketplace.json`, and `NOTICE.md`.

### Removed

- None.

### Local Modifications

- No local modifications were made to the imported skill contents in this version.
"""
    (ROOT / "CHANGELOG.md").write_text(text, encoding="utf-8")


def build_notice(commit: str) -> None:
    text = f"""# Notice

This repository contains vendored Agent Skills copied from upstream repositories for stable installation and repeat use.

## Vendored Sources

| Source | Repository | Pinned Commit | Licence | Local Copy |
|---|---|---|---|---|
| `thinkbench-skills` | {SOURCE_REPO_WEB} | `{commit}` | MIT | `skills/thinkbench-skills/` |

The upstream MIT licence for `zkbkb/thinkbench-skills` is preserved at `third_party/thinkbench-skills/LICENSE`.
"""
    (ROOT / "NOTICE.md").write_text(text, encoding="utf-8")


def build_license() -> None:
    path = ROOT / "LICENSE"
    if path.exists():
        return
    text = """MIT License

Copyright (c) 2026 zkbkb

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicence, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    path.write_text(text, encoding="utf-8")


def build_gitignore() -> None:
    path = ROOT / ".gitignore"
    entries = [".external-cache/", "*.tmp", "__pycache__/", ".DS_Store"]
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    merged = existing[:]
    for entry in entries:
        if entry not in merged:
            merged.append(entry)
    path.write_text("\n".join(merged).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    commit = run(["git", "rev-parse", "HEAD"], cwd=SOURCE_LOCAL)
    rows = skill_rows(commit)
    if not rows:
        raise SystemExit("No skills found under skills/thinkbench-skills")
    build_upstream_sources(rows, commit)
    build_skills_json(rows)
    build_marketplace(rows)
    build_readme(rows, commit)
    build_changelog(rows, commit)
    build_notice(commit)
    build_license()
    build_gitignore()
    print(f"Generated metadata for {len(rows)} skills from {SOURCE_ID} at {commit}.")


if __name__ == "__main__":
    main()
