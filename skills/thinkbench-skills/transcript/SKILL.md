---
name: transcript
description: >
  Export the current conversation as a structured transcript file preserving all user inputs
  and AI responses in chronological order. Use this skill when the user wants to save, export,
  or download the current conversation as a text file. Trigger phrases include "/transcript",
  "导出对话", "导出对话记录", "保存对话", "保存对话记录", "export conversation",
  "export chat", "save conversation", "save chat log", or any expression of wanting to
  preserve the full conversation record as a downloadable file. This skill differs from
  context-handoff (/handoff, /compact) which compresses conversation state for session
  continuation — this skill produces a faithful, verbatim record of the conversation for
  archival, review, and reference purposes.
license: MIT
compatibility: Requires Python 3.8+
metadata:
  author: Kaibin Zhang
  version: "1.0.0"
---

# Transcript — Conversation Record Export

## Overview

This skill exports the current conversation as a structured transcript file, preserving
every user message and AI response in chronological order. The output is a faithful
archival record (not a summary or compression) designed for later review by humans or AI.

**Default output:** Markdown (.md) with YAML front-matter.
**Optional output:** JSON (.json), available on request alongside or instead of Markdown.

Core difference from `/handoff`: handoff compresses state for resumption; transcript
preserves the full conversation verbatim for archival.

## When to Use This Skill

Trigger when the user expresses any of these intents:

- Wants to save or export the current conversation as a file
- Wants a downloadable record of the conversation
- Uses trigger phrases: "/transcript", "导出对话", "导出对话记录", "保存对话",
  "export conversation", "save chat", etc.

**This skill is NOT for:**
- Compressing context for a new session (use context-handoff)
- General summarisation requests
- Extracting a single piece of information from the conversation

## Workflow

### Step 1: Read the Output Template

ALWAYS begin by reading the output template before generating any files:

```
Read: references/output-template.md  (relative to this skill's directory)
```

This template contains the exact Markdown and JSON formats with all conventions.

### Step 2: Determine Output Format

- **Default:** Markdown only
- If the user says "also JSON", "也要 JSON", "同时输出 JSON" → output both MD and JSON
- If the user says "only JSON", "只要 JSON" → output JSON only
- If unclear, output Markdown only

### Step 3: Resolve the Conversation Title

The conversation title is needed for the filename and the document heading.
Follow this sequence:

1. **Attempt to obtain the real title** via any available mechanism (API, tool, etc.).
   As of March 2026 in claude.ai, no such mechanism exists — proceed to step 2.
2. **Generate a suggested title** based on conversation content: a short English phrase,
   hyphen-separated, descriptive of the main topic (e.g., `Python-Data-Cleaning`,
   `Experience-Effect-Research-Design`, `Skill-Design-Discussion`).
3. **Ask the user:** present the suggested title and ask them to confirm or paste the
   actual conversation title from the UI. Example prompt:

   > 建议的文件标题为 `Skill-Design-Discussion`。可以使用吗？
   > 或者你可以粘贴对话侧边栏中的实际标题。

4. Use whichever title the user confirms.

### Step 4: Obtain Timestamp

Call the `user_time` tool to get the current time. This timestamp is used for:
- The `export_date` field in front-matter/metadata
- The `YYYYMMDD` portion of the filename

### Step 5: Generate the Transcript

Walk through every message in the conversation context, from first to last, and produce
the Markdown transcript following all formatting rules below.

**Scope of export:**
- Include the user's export trigger message (e.g., "/transcript") as the final user message
- Do NOT include the AI's export response (i.e., this very response executing the skill)
- End with the marker: `[对话导出于此处终止]`

**Dual-format handling:** Always generate the Markdown file first. If the user also
requested JSON, use `scripts/transcript_converter.py` to convert the Markdown to JSON
automatically (do NOT generate the JSON content manually — the converter handles this).

### Step 6: Validate, Save and Present

1. Generate the Markdown file in `/home/claude/`
2. Run `scripts/transcript_validator.py` on the generated file via `bash`.
   If errors are found, fix them before proceeding. Warnings can be noted internally.
3. If dual-format requested, run `scripts/transcript_converter.py` to generate JSON,
   then validate the JSON file as well.
4. Copy final file(s) to `/mnt/user-data/outputs/`
5. Use `present_files` to share with the user
6. Provide a brief confirmation message (do NOT restate the entire transcript content)

## Filename Convention

```
YYYYMMDD_Transcript_Title.{md|json}
```

- `YYYYMMDD`: export date (from Step 4), date only — precise time is in front-matter
- `Transcript`: fixed identifier
- `Title`: the confirmed title from Step 3, hyphen-separated words
- Extension: `.md` for Markdown, `.json` for JSON

Example: `20260327_Transcript_Skill-Design-Discussion.md`

## Formatting Rules — Markdown

### Front-matter (YAML)

The front-matter block uses a fixed schema. Every field is always present; if a value
cannot be determined, use `"N/A"`. No blank lines between `---` delimiters and content.

```yaml
---
export_date: "YYYY-MM-DD HH:MM:SS UTC+N"
model: "Claude Opus 4.6"
total_turns: N
estimated_length: "~X characters (~Y tokens)"
topic_summary: "1-2 sentence summary of the conversation in the conversation's primary language"
tags:
  - conversation
keywords:
  - keyword1
  - keyword2
user_files:
  - "filename.ext"
generated_files:
  - "filename.ext"
tools_used:
  - tool_name
---
```

Field notes:
- `tags`: always and only `conversation` — this is a type-level tag for filtering
- `keywords`: content-level terms for this specific conversation
- `user_files`: all files the user uploaded during the conversation; empty list `[]` if none
- `generated_files`: all artifacts/files the AI generated; empty list `[]` if none
- `tools_used`: all tool types invoked (e.g., web_search, bash, ask_user_input, google_drive_search); empty list `[]` if none
- `estimated_length`: rough estimate of total conversation character/token count; mark as approximate

### Document Heading

Immediately after front-matter, one H1 heading:

```markdown
# Transcript: {Descriptive Title in Conversation Language}
```

This title can differ from the filename title — it should be more human-readable and can
use the conversation's primary language.

### Message Structure

Each turn consists of a User message and an Assistant response, formatted as:

```markdown
**User:**
{user message content}

**Assistant:**
{assistant response content}

---
```

Rules:
- `**User:**` and `**Assistant:**` are always bold, on their own line
- Content follows immediately on the next line (no blank line after the role marker)
- Turns are separated by `---` (horizontal rule)
- No turn numbers or turn headings — the sequential order is the implicit structure
- The final `---` after the last turn is optional

### Tool Calls

Tool calls are recorded as inline markers within the Assistant's response, placed at
the point where they logically occurred:

```markdown
[tool: {tool_name} — {one-sentence purpose description}]
```

Examples:
- `[tool: web_search — 查询 pandas to_datetime 混合日期格式最佳实践]`
- `[tool: bash — 执行 Python 脚本读取 CSV，输出列名和缺失值统计]`
- `[tool: google_drive_search — 搜索 Q3 销售报告]`

For consecutive tool calls serving a single purpose, they may be combined:
`[tools: web_search + web_fetch — 搜索并读取 Malmendier & Nagel (2016) 论文全文]`

### Interactive Choices (ask_user_input)

When the AI presented interactive choices and the user made a selection, record as:

```markdown
[choice] Q: {question text} → {user's selected option}
```

If there were multiple questions in one interaction, use one `[choice]` line per question.

### Files — User Uploads and Artifacts

User-uploaded files and AI-generated artifacts are recorded using Obsidian callout syntax,
always placed at the END of the relevant message (User or Assistant):

```markdown
> [!file]
> `filename.ext` (user upload)
```

```markdown
> [!file]
> `filename.ext` (artifact, {brief type/description})
```

Examples:
- `> [!file]`
  `> \`sales_data_2025.csv\` (user upload)`
- `> [!file]`
  `> \`data_cleaner.py\` (artifact, Python script, ~65 lines)`
- `> [!file]`
  `> \`data_cleaner.py\` (artifact, updated)`

### Code Blocks

- **≤30 lines:** preserve verbatim in the transcript
- **>30 lines with a corresponding artifact:** summarise as
  `[代码块: {language}, {N} 行, 功能为 {description} — 完整代码见 {filename}]`
- **>30 lines without a corresponding artifact:** preserve verbatim (this is the only
  copy of the code)
- **Content-container code blocks** (code fences used to wrap Markdown, text, config,
  or other non-code content for copy-paste purposes): always preserve verbatim regardless
  of length — these are conversation content, not code

When in doubt about whether a code block is "content-container" vs actual code, preserve it.

### Conversation Termination

The final entry is the user's export trigger message, followed by:

```markdown
[对话导出于此处终止]
```

## Formatting Rules — JSON

The JSON format mirrors the Markdown structure with a fixed schema:

```json
{
  "metadata": {
    "export_date": "...",
    "model": "...",
    "total_turns": N,
    "estimated_length": "...",
    "topic_summary": "...",
    "tags": ["conversation"],
    "keywords": [...],
    "user_files": [...],
    "generated_files": [...],
    "tools_used": [...]
  },
  "turns": [
    {
      "user": {
        "message": "...",
        "files": ["filename.ext"]
      },
      "assistant": {
        "message": "...",
        "tools": [{"tool": "...", "purpose": "..."}],
        "choices": [{"question": "...", "selected": "..."}],
        "files": [{"name": "...", "type": "artifact|upload", "note": "..."}]
      }
    }
  ]
}
```

Rules:
- `metadata` fields are identical to the YAML front-matter
- Every turn has `user` and `assistant` objects
- `assistant` is `null` for the final export-trigger turn
- `tools`, `choices`, `files` are always present as arrays (empty `[]` when not applicable)
- The final turn includes `"_note": "对话导出于此处终止"`
- Code block handling follows the same rules as Markdown (>30 lines summarised, etc.)

## Important Reminders

- This is a VERBATIM record, not a summary. Preserve the user's and AI's actual words.
- Do NOT rephrase, beautify, or editorially adjust message content.
- Do NOT fabricate content that was not in the conversation.
- Do NOT include system prompts, user preferences, or memory contents in the transcript.
- DO preserve all formatting within messages (lists, bold, inline code, etc.).
- DO maintain strict front-matter/schema consistency across all exports — every field
  always present, missing values marked as N/A or empty arrays.
- DO use the `user_time` tool for accurate timestamps.
- DO ask the user to confirm the conversation title before generating the file.

## Bundled Scripts

Two Python scripts are available in `scripts/` (both are zero-dependency, standard library only):

### `scripts/transcript_converter.py` — Format Conversion

Converts transcript files between Markdown and JSON formats. Use this when:
- The user requests dual-format output: generate Markdown first, then run the converter
  to produce JSON automatically (saves output tokens vs. generating both from scratch)
- The user wants to convert an existing transcript to the other format

```bash
python scripts/transcript_converter.py transcript.md              # → transcript.json
python scripts/transcript_converter.py transcript.json            # → transcript.md
python scripts/transcript_converter.py input.md -o output.json    # explicit output path
```

**Integration into workflow (Step 5–6):** When the user requests both MD and JSON output,
generate only the Markdown file, then invoke the converter via `bash` to produce the JSON
automatically. This avoids generating the JSON content from scratch and significantly
reduces output token usage.

### `scripts/transcript_validator.py` — Format Validation

Validates transcript files against the skill's format specification. Run this after
generating any transcript file to catch formatting errors before presenting to the user.

```bash
python scripts/transcript_validator.py transcript.md              # validate single file
python scripts/transcript_validator.py transcript.md --strict     # warnings become errors
python scripts/transcript_validator.py file.md file.json          # validate multiple files
```

Checks performed (Markdown): front-matter structure (no blank lines, no leading whitespace
on top-level keys), required fields present, `tags` contains `conversation`, `total_turns`
matches actual User marker count, H1 heading present, role markers present, callout names
correct (`[!file]` not `[!attachment]`), tool/choice marker format, termination marker,
`export_date` format.

Checks performed (JSON): valid JSON, top-level `metadata`/`turns` structure, required
metadata fields, array type enforcement, turn sub-field structure (`tools`/`choices`/`files`
always arrays), last turn has null assistant with `_note`, `export_date` format.

**Integration into workflow (Step 6):** After generating the transcript file(s), run the
validator via `bash` before presenting files to the user. If errors are found, fix them
before output. If only warnings are found, proceed but note them internally.

## Reference Material

For the complete output template with a worked example:
Refer to: `references/output-template.md`

For format conversion and validation:
Refer to: `scripts/transcript_converter.py`, `scripts/transcript_validator.py`
