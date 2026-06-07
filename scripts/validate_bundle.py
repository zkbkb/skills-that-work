#!/usr/bin/env python3
"""Validate the skills-that-work bundle structure."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Invalid JSON: {path}: {exc}") from exc


def require_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"Missing file: {path.relative_to(ROOT)}")


def require_dir(path: Path) -> None:
    if not path.is_dir():
        raise SystemExit(f"Missing directory: {path.relative_to(ROOT)}")


def main() -> None:
    required_files = [
        "README.md",
        "CHANGELOG.md",
        "NOTICE.md",
        "LICENSE",
        "upstream-sources.json",
        "skills.json",
        ".claude-plugin/marketplace.json",
    ]
    for rel in required_files:
        require_file(ROOT / rel)

    upstream = load_json(ROOT / "upstream-sources.json")
    skills_index = load_json(ROOT / "skills.json")
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")

    indexed_paths = set()
    for skill in skills_index.get("skills", []):
        path = ROOT / skill["path"]
        require_dir(path)
        require_file(path / "SKILL.md")
        indexed_paths.add(skill["path"])

    upstream_paths = {
        skill["local_path"]
        for source in upstream.get("sources", [])
        for skill in source.get("skills", [])
    }
    if indexed_paths != upstream_paths:
        missing_from_index = upstream_paths - indexed_paths
        missing_from_upstream = indexed_paths - upstream_paths
        raise SystemExit(
            "Mismatch between skills.json and upstream-sources.json: "
            f"missing_from_index={sorted(missing_from_index)}, "
            f"missing_from_upstream={sorted(missing_from_upstream)}"
        )

    marketplace_paths = set()
    for plugin in marketplace.get("plugins", []):
        for rel in plugin.get("skills", []):
            normalised = rel[2:] if rel.startswith("./") else rel
            require_dir(ROOT / normalised)
            require_file(ROOT / normalised / "SKILL.md")
            marketplace_paths.add(normalised)

    if marketplace_paths != indexed_paths:
        raise SystemExit(
            "Mismatch between marketplace.json and skills.json: "
            f"marketplace_only={sorted(marketplace_paths - indexed_paths)}, "
            f"index_only={sorted(indexed_paths - marketplace_paths)}"
        )

    print(f"Validated {len(indexed_paths)} skills successfully.")


if __name__ == "__main__":
    main()
