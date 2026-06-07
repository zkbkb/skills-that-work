#!/usr/bin/env python3
"""
transcript_validator.py — Validate transcript files against the /transcript skill spec.

Usage:
    python transcript_validator.py file.md           # Validate a Markdown transcript
    python transcript_validator.py file.json         # Validate a JSON transcript
    python transcript_validator.py *.md              # Validate multiple files
    python transcript_validator.py file.md --strict   # Strict mode (warnings become errors)

Exit codes:
    0 — All checks passed
    1 — Errors found
    2 — File not found or unreadable
"""

import json
import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    filepath: str
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    info: list = field(default_factory=list)

    def error(self, msg: str):
        self.errors.append(f"  ERROR: {msg}")

    def warn(self, msg: str):
        self.warnings.append(f"  WARN:  {msg}")

    def ok(self, msg: str):
        self.info.append(f"  OK:    {msg}")

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def report(self, strict: bool = False) -> str:
        lines = [f"\n{'='*60}", f"  {self.filepath}", f"{'='*60}"]
        for i in self.info:
            lines.append(i)
        for w in self.warnings:
            lines.append(w)
        for e in self.errors:
            lines.append(e)

        err_count = len(self.errors)
        warn_count = len(self.warnings)
        if strict:
            err_count += warn_count

        if err_count == 0:
            lines.append(f"\n  RESULT: PASS ({len(self.info)} checks passed, {warn_count} warnings)")
        else:
            lines.append(f"\n  RESULT: FAIL ({err_count} errors, {warn_count} warnings)")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Required metadata fields
# ---------------------------------------------------------------------------

REQUIRED_META_FIELDS = [
    "export_date", "model", "total_turns", "estimated_length",
    "topic_summary", "tags", "keywords", "user_files",
    "generated_files", "tools_used"
]

LIST_FIELDS = ["tags", "keywords", "user_files", "generated_files", "tools_used"]


# ---------------------------------------------------------------------------
# Markdown validation
# ---------------------------------------------------------------------------

def validate_md(text: str, result: ValidationResult):
    """Validate a Markdown transcript file."""

    # 1. Front-matter existence and delimiters
    fm_match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not fm_match:
        result.error("Missing or malformed YAML front-matter (must start with --- and close with ---)")
        return
    result.ok("Front-matter delimiters present")

    fm_raw = fm_match.group(1)
    body = text[fm_match.end():]

    # 2. No blank lines between --- and content
    if fm_raw.startswith('\n'):
        result.error("Blank line after opening --- (front-matter must start immediately)")
    if fm_raw.endswith('\n'):
        # Trailing newline is OK (just before closing ---), but blank lines are not
        if fm_raw.endswith('\n\n'):
            result.error("Blank line before closing --- in front-matter")

    # 3. Check required metadata fields
    found_keys = set()
    for line in fm_raw.split('\n'):
        kv = re.match(r'^(\w[\w_]*):', line)
        if kv:
            found_keys.add(kv.group(1))

    for field_name in REQUIRED_META_FIELDS:
        if field_name in found_keys:
            result.ok(f"Field '{field_name}' present")
        else:
            result.error(f"Required field '{field_name}' missing from front-matter")

    # 4. Check tags contains 'conversation'
    tags_match = re.search(r'tags:\s*\n((?:\s+-\s+.*\n)*)', fm_raw + '\n')
    if tags_match:
        tags_content = tags_match.group(1)
        if 'conversation' not in tags_content:
            result.warn("'tags' should contain 'conversation'")
        else:
            result.ok("Tag 'conversation' present")

    # 5. Front-matter field indentation (no leading spaces on top-level keys)
    for line in fm_raw.split('\n'):
        if re.match(r'^\s+\w[\w_]*:', line) and not re.match(r'^\s+-', line):
            result.error(f"Top-level front-matter key has leading whitespace: '{line.strip()}'")

    # 6. H1 heading
    h1_match = re.search(r'^#\s+Transcript:', body, re.MULTILINE)
    if h1_match:
        result.ok("H1 Transcript heading present")
    else:
        result.error("Missing '# Transcript: ...' heading after front-matter")

    # 7. Role markers
    user_count = len(re.findall(r'^\*\*User:\*\*', body, re.MULTILINE))
    asst_count = len(re.findall(r'^\*\*Assistant:\*\*', body, re.MULTILINE))

    if user_count == 0:
        result.error("No **User:** markers found")
    else:
        result.ok(f"Found {user_count} **User:** markers")

    if asst_count == 0:
        result.error("No **Assistant:** markers found")
    else:
        result.ok(f"Found {asst_count} **Assistant:** markers")

    # 8. total_turns consistency
    total_match = re.search(r'total_turns:\s*(\d+)', fm_raw)
    if total_match:
        declared_turns = int(total_match.group(1))
        if user_count != declared_turns:
            result.warn(
                f"total_turns ({declared_turns}) does not match "
                f"number of **User:** markers ({user_count})"
            )
        else:
            result.ok(f"total_turns ({declared_turns}) matches User marker count")

    # 9. Turn separators
    separator_count = len(re.findall(r'^---$', body, re.MULTILINE))
    result.ok(f"Found {separator_count} turn separators (---)")

    # 10. Termination marker
    if '[对话导出于此处终止]' in body:
        result.ok("Termination marker present")
    else:
        result.warn("Missing termination marker '[对话导出于此处终止]'")

    # 11. File callouts format check
    file_callouts = re.findall(r'>\s*\[!file\]', body)
    result.ok(f"Found {len(file_callouts)} [!file] callouts")

    # Check for wrong callout names (common mistakes)
    for wrong in ['[!attachment]', '[!artifact]', '[!upload]']:
        if wrong in body:
            result.warn(f"Found '{wrong}' — should be '[!file]' instead")

    # 12. Tool markers format
    tool_markers = re.findall(r'\[tools?:', body)
    result.ok(f"Found {len(tool_markers)} tool markers")

    # Check tool markers have purpose description
    bad_tools = re.findall(r'\[tools?:\s*\w+\s*\]', body)
    for bt in bad_tools:
        result.warn(f"Tool marker missing purpose description: '{bt}'")

    # 13. Choice markers format
    choice_markers = re.findall(r'\[choice\]', body)
    result.ok(f"Found {len(choice_markers)} choice markers")

    # Check choice markers have arrow
    choice_lines = re.findall(r'\[choice\].*', body)
    for cl in choice_lines:
        if '→' not in cl:
            result.warn(f"Choice marker missing '→' (selection arrow): '{cl[:60]}...'")

    # 14. export_date format
    date_match = re.search(r'export_date:\s*"([^"]*)"', fm_raw)
    if date_match:
        date_val = date_match.group(1)
        if re.match(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+UTC[+-]?\d+', date_val):
            result.ok(f"export_date format valid: {date_val}")
        elif date_val == "N/A":
            result.warn("export_date is N/A")
        else:
            result.warn(f"export_date format may be non-standard: '{date_val}'")


# ---------------------------------------------------------------------------
# JSON validation
# ---------------------------------------------------------------------------

def validate_json(text: str, result: ValidationResult):
    """Validate a JSON transcript file."""

    # 1. Parse JSON
    try:
        data = json.loads(text)
        result.ok("Valid JSON")
    except json.JSONDecodeError as e:
        result.error(f"Invalid JSON: {e}")
        return

    # 2. Top-level structure
    if "metadata" not in data:
        result.error("Missing top-level 'metadata' object")
    else:
        result.ok("'metadata' object present")

    if "turns" not in data:
        result.error("Missing top-level 'turns' array")
        return
    else:
        result.ok("'turns' array present")

    meta = data.get("metadata", {})
    turns = data.get("turns", [])

    # 3. Required metadata fields
    for field_name in REQUIRED_META_FIELDS:
        if field_name in meta:
            result.ok(f"Field '{field_name}' present")
        else:
            result.error(f"Required field '{field_name}' missing from metadata")

    # 4. Tags check
    tags = meta.get("tags", [])
    if isinstance(tags, list):
        if "conversation" in tags:
            result.ok("Tag 'conversation' present")
        else:
            result.warn("'tags' should contain 'conversation'")
    else:
        result.error("'tags' should be an array")

    # 5. List fields are arrays
    for field_name in LIST_FIELDS:
        val = meta.get(field_name)
        if val is not None and not isinstance(val, list):
            result.error(f"'{field_name}' should be an array, got {type(val).__name__}")

    # 6. total_turns consistency
    declared = meta.get("total_turns", 0)
    actual = len(turns)
    if declared != actual:
        result.warn(f"total_turns ({declared}) does not match turns array length ({actual})")
    else:
        result.ok(f"total_turns ({declared}) matches turns array length")

    # 7. Turn structure
    for i, turn in enumerate(turns):
        turn_label = f"Turn {i+1}"

        # User object
        if "user" not in turn:
            result.error(f"{turn_label}: missing 'user' object")
            continue

        user = turn["user"]
        if "message" not in user:
            result.error(f"{turn_label}: user missing 'message' field")
        if "files" not in user:
            result.warn(f"{turn_label}: user missing 'files' field (should be [] if empty)")

        # Assistant object
        assistant = turn.get("assistant")
        if assistant is None:
            # Final turn — should have _note
            if "_note" not in turn:
                result.warn(f"{turn_label}: assistant is null but no '_note' field")
            else:
                result.ok(f"{turn_label}: final turn with termination note")
            continue

        if not isinstance(assistant, dict):
            result.error(f"{turn_label}: 'assistant' should be an object or null")
            continue

        # Required assistant sub-fields
        if "message" not in assistant:
            result.error(f"{turn_label}: assistant missing 'message' field")

        for sub_field in ["tools", "choices", "files"]:
            val = assistant.get(sub_field)
            if val is None:
                result.warn(f"{turn_label}: assistant missing '{sub_field}' (should be [])")
            elif not isinstance(val, list):
                result.error(f"{turn_label}: assistant '{sub_field}' should be an array")

        # Tool entries structure
        for t in assistant.get("tools", []):
            if not isinstance(t, dict):
                result.error(f"{turn_label}: tool entry should be an object")
            elif "tool" not in t or "purpose" not in t:
                result.warn(f"{turn_label}: tool entry missing 'tool' or 'purpose' field")

        # Choice entries structure
        for c in assistant.get("choices", []):
            if not isinstance(c, dict):
                result.error(f"{turn_label}: choice entry should be an object")
            elif "question" not in c or "selected" not in c:
                result.warn(f"{turn_label}: choice entry missing 'question' or 'selected'")

        # File entries structure
        for f in assistant.get("files", []):
            if not isinstance(f, dict):
                result.error(f"{turn_label}: file entry should be an object")
            elif "name" not in f:
                result.error(f"{turn_label}: file entry missing 'name'")

    # 8. Last turn should have null assistant
    if turns:
        last = turns[-1]
        if last.get("assistant") is not None:
            result.warn("Last turn has non-null assistant (expected null for export trigger)")

    # 9. export_date format
    date_val = meta.get("export_date", "")
    if re.match(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+UTC[+-]?\d+', date_val):
        result.ok(f"export_date format valid: {date_val}")
    elif date_val == "N/A":
        result.warn("export_date is N/A")
    elif date_val:
        result.warn(f"export_date format may be non-standard: '{date_val}'")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Validate transcript files.")
    parser.add_argument("files", nargs="+", help="Transcript file(s) to validate")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    args = parser.parse_args()

    all_passed = True

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"\nERROR: File not found: {filepath}", file=sys.stderr)
            all_passed = False
            continue

        result = ValidationResult(filepath=str(path))
        text = path.read_text(encoding="utf-8")

        if path.suffix.lower() == ".md":
            validate_md(text, result)
        elif path.suffix.lower() == ".json":
            validate_json(text, result)
        else:
            result.error(f"Unsupported format: {path.suffix}")

        print(result.report(strict=args.strict))

        if args.strict:
            if result.errors or result.warnings:
                all_passed = False
        else:
            if result.errors:
                all_passed = False

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
