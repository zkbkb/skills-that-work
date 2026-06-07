#!/usr/bin/env python3
"""
transcript_converter.py — Convert transcript files between Markdown and JSON formats.

Usage:
    python transcript_converter.py input.md              # MD → JSON (output: input.json)
    python transcript_converter.py input.json            # JSON → MD (output: input.md)
    python transcript_converter.py input.md -o out.json   # explicit output path
    python transcript_converter.py input.json -o out.md

Designed for use with the /transcript skill's output format.
"""

import json
import re
import sys
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Markdown → JSON
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML front-matter and return (metadata_dict, remaining_body)."""
    match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not match:
        return {}, text

    raw = match.group(1)
    body = text[match.end():]
    meta = {}

    current_key = None
    current_list = None

    for line in raw.split('\n'):
        # List item under a key
        if re.match(r'^\s+-\s+', line) and current_key:
            val = re.sub(r'^\s+-\s+', '', line).strip().strip('"').strip("'")
            if current_list is None:
                current_list = []
            current_list.append(val)
            meta[current_key] = current_list
            continue

        # New key-value pair
        kv = re.match(r'^(\w[\w_]*):\s*(.*)', line)
        if kv:
            # Save previous list if any
            if current_key and current_list is not None:
                meta[current_key] = current_list

            current_key = kv.group(1)
            val = kv.group(2).strip().strip('"').strip("'")
            current_list = None

            if val:
                # Try to parse as int
                try:
                    meta[current_key] = int(val)
                except ValueError:
                    meta[current_key] = val
            # If no value, it might be a list starting on next line

    return meta, body


def parse_md_to_json(text: str) -> dict:
    """Parse a transcript Markdown file into the JSON schema."""
    meta, body = parse_frontmatter(text)

    # Build metadata block
    metadata = {
        "export_date": meta.get("export_date", "N/A"),
        "model": meta.get("model", "N/A"),
        "total_turns": meta.get("total_turns", 0),
        "estimated_length": meta.get("estimated_length", "N/A"),
        "topic_summary": meta.get("topic_summary", "N/A"),
        "tags": meta.get("tags", ["conversation"]),
        "keywords": meta.get("keywords", []),
        "user_files": meta.get("user_files", []),
        "generated_files": meta.get("generated_files", []),
        "tools_used": meta.get("tools_used", []),
    }

    # Split body into turns by --- separator
    # Extract and remove the H1 heading
    body = body.strip()
    title_match = re.match(r'^#\s+Transcript:\s*(.+)', body)
    doc_title = title_match.group(1).strip() if title_match else "Conversation"
    body = re.sub(r'^#\s+Transcript:.*?\n', '', body).strip()

    # Store title in metadata
    metadata["title"] = doc_title

    # Split on horizontal rules
    raw_turns = re.split(r'\n---\n', body)
    # Filter out empty segments
    raw_turns = [t.strip() for t in raw_turns if t.strip()]

    turns = []
    for raw_turn in raw_turns:
        raw_turn = raw_turn.strip()
        if not raw_turn:
            continue

        # Split into user and assistant parts
        parts = re.split(r'\n\*\*Assistant:\*\*\n', raw_turn, maxsplit=1)

        user_part = parts[0]
        assistant_part = parts[1] if len(parts) > 1 else None

        # Clean user part
        user_part = re.sub(r'^\*\*User:\*\*\n', '', user_part).strip()

        # Extract files from user part (callouts)
        user_files = []
        file_pattern = r'>\s*\[!file\]\s*\n>\s*`([^`]+)`\s*\(([^)]+)\)'
        for fm in re.finditer(file_pattern, user_part):
            user_files.append(fm.group(1))
        # Remove file callouts from message
        user_msg = re.sub(file_pattern, '', user_part).strip()

        turn = {
            "user": {
                "message": user_msg,
                "files": user_files,
            }
        }

        if assistant_part is None:
            # Final turn (export trigger)
            turn["assistant"] = None
            # Check for termination marker
            if "[对话导出于此处终止]" in user_msg:
                turn["_note"] = "对话导出于此处终止"
                turn["user"]["message"] = user_msg.replace(
                    "\n[对话导出于此处终止]", ""
                ).replace("[对话导出于此处终止]", "").strip()
        else:
            assistant_part = assistant_part.strip()

            # Extract tools
            tools = []
            tool_pattern = r'\[tools?:\s*([^\]]+?)(?:\s*—\s*|\s*-\s*)([^\]]+)\]'
            for tm in re.finditer(tool_pattern, assistant_part):
                tools.append({
                    "tool": tm.group(1).strip(),
                    "purpose": tm.group(2).strip(),
                })

            # Extract choices
            choices = []
            choice_pattern = r'\[choice\]\s*Q:\s*(.+?)\s*→\s*(.+)'
            for cm in re.finditer(choice_pattern, assistant_part):
                choices.append({
                    "question": cm.group(1).strip(),
                    "selected": cm.group(2).strip(),
                })

            # Extract files (artifacts)
            asst_files = []
            for fm in re.finditer(file_pattern, assistant_part):
                name = fm.group(1)
                desc = fm.group(2)
                file_entry = {"name": name}
                if "artifact" in desc.lower():
                    file_entry["type"] = "artifact"
                    note = re.sub(r'artifact,?\s*', '', desc, flags=re.IGNORECASE).strip()
                    if note:
                        file_entry["note"] = note
                else:
                    file_entry["type"] = "upload"
                    file_entry["note"] = desc
                asst_files.append(file_entry)

            # Clean assistant message: remove tool markers, choice markers, file callouts
            asst_msg = assistant_part
            asst_msg = re.sub(tool_pattern, '', asst_msg)
            asst_msg = re.sub(choice_pattern, '', asst_msg)
            asst_msg = re.sub(file_pattern, '', asst_msg)
            # Clean up extra whitespace
            asst_msg = re.sub(r'\n{3,}', '\n\n', asst_msg).strip()

            turn["assistant"] = {
                "message": asst_msg,
                "tools": tools,
                "choices": choices,
                "files": asst_files,
            }

        turns.append(turn)

    return {"metadata": metadata, "turns": turns}


# ---------------------------------------------------------------------------
# JSON → Markdown
# ---------------------------------------------------------------------------

def json_to_md(data: dict) -> str:
    """Convert a transcript JSON object to Markdown format."""
    meta = data["metadata"]
    lines = []

    # Front-matter
    lines.append("---")
    lines.append(f'export_date: "{meta["export_date"]}"')
    lines.append(f'model: "{meta["model"]}"')
    lines.append(f'total_turns: {meta["total_turns"]}')
    lines.append(f'estimated_length: "{meta["estimated_length"]}"')
    lines.append(f'topic_summary: "{meta["topic_summary"]}"')

    for list_key in ["tags", "keywords", "user_files", "generated_files", "tools_used"]:
        val = meta.get(list_key, [])
        if not val:
            lines.append(f'{list_key}: []')
        else:
            lines.append(f'{list_key}:')
            for item in val:
                # Only quote if item contains special YAML chars
                if any(c in str(item) for c in ':#{}[],"\'&*?|->!%@`'):
                    lines.append(f'  - "{item}"')
                else:
                    lines.append(f'  - {item}')

    lines.append("---")
    lines.append("")

    # Heading — use stored title, or derive from summary
    heading = meta.get("title")
    if not heading:
        summary = meta.get("topic_summary", "Conversation")
        if summary and summary != "N/A":
            heading = summary.split("，")[0].split(",")[0].split("。")[0].split(".")[0]
            if len(heading) > 50:
                heading = heading[:50].rsplit(" ", 1)[0]
        else:
            heading = "Conversation"
    lines.append(f"# Transcript: {heading}")
    lines.append("")

    # Turns
    for i, turn in enumerate(data["turns"]):
        user = turn["user"]

        # User message
        lines.append("**User:**")
        lines.append(user["message"])

        # User files
        for f in user.get("files", []):
            lines.append("> [!file]")
            lines.append(f"> `{f}` (user upload)")

        assistant = turn.get("assistant")
        if assistant is None:
            # Final turn
            note = turn.get("_note", "对话导出于此处终止")
            lines.append(f"[{note}]")
        else:
            lines.append("")
            lines.append("**Assistant:**")

            msg = assistant["message"]

            # Insert tool markers at the beginning of the message
            for t in assistant.get("tools", []):
                lines.append(f'[tool: {t["tool"]} — {t["purpose"]}]')

            lines.append(msg)

            # Insert choice markers
            for c in assistant.get("choices", []):
                lines.append(f'[choice] Q: {c["question"]} → {c["selected"]}')

            # Artifact files
            for f in assistant.get("files", []):
                note_parts = [f.get("type", "")]
                if f.get("note"):
                    note_parts.append(f["note"])
                desc = ", ".join(p for p in note_parts if p)
                lines.append("> [!file]")
                lines.append(f"> `{f['name']}` ({desc})")

        # Turn separator (except after last turn)
        if i < len(data["turns"]) - 1:
            lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert transcript files between Markdown and JSON."
    )
    parser.add_argument("input", help="Input file (.md or .json)")
    parser.add_argument("-o", "--output", help="Output file path (auto-detected if omitted)")
    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: {input_path} not found.", file=sys.stderr)
        sys.exit(1)

    suffix = input_path.suffix.lower()

    if suffix == ".md":
        # MD → JSON
        text = input_path.read_text(encoding="utf-8")
        result = parse_md_to_json(text)
        out_path = Path(args.output) if args.output else input_path.with_suffix(".json")
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Converted: {input_path} → {out_path}")

    elif suffix == ".json":
        # JSON → MD
        text = input_path.read_text(encoding="utf-8")
        data = json.loads(text)
        result = json_to_md(data)
        out_path = Path(args.output) if args.output else input_path.with_suffix(".md")
        out_path.write_text(result, encoding="utf-8")
        print(f"Converted: {input_path} → {out_path}")

    else:
        print(f"Error: unsupported format '{suffix}'. Use .md or .json.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
