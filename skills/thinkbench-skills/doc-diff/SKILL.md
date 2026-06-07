---
name: doc-diff
description: >
  Generate Obsidian-compatible Markdown tracked-changes documents that show the differences
  between two versions of the same document. Use this skill whenever the user provides two
  versions of a file and asks to compare, diff, track changes, see what was modified, or
  review edits. Also trigger when the user says things like "what did they change",
  "compare these two drafts", "show me the differences", "对比一下这两个版本", "看看改了什么",
  or uploads two files with similar names (e.g. v1/v2, draft/final, before/after).
  This skill covers both the primary Markdown output and optional diff file generation.
  Do NOT use this skill for comparing code files (use standard diff tools instead) or
  for comparing completely unrelated documents.
license: MIT
metadata:
  author: Kaibin Zhang
  version: "1.0.0"
---

# Document Version Diff & Tracked Changes

## Overview

Given two versions of the same document (original and modified), produce a single continuous
Markdown file that shows all changes inline using Obsidian-compatible syntax: `~~strikethrough~~`
for deletions and `==highlight==` for additions. The output reads as a complete document in
the modified version's structure, with changes visually marked.

## Workflow

### Step 1: Identify Inputs

1. **Determine which file is original and which is modified.**
   - If the user states it explicitly, follow their instruction.
   - If filenames contain version indicators (v1/v2, draft/final, old/new, dates), infer from those.
   - If ambiguous, ask the user before proceeding.

2. **Recommended format:** Two Markdown files where one is an edit of the other.
   This produces the cleanest results. Other formats (PDF, docx, txt) are supported
   but may introduce formatting noise.

3. **Extract plain text from non-Markdown inputs:**
   - For `.docx`: use `pandoc` to extract text content.
   - For `.pdf`: use `pdftotext` or read from context if available.
   - For `.txt`: read directly.
   - When the file content is already present in the context window (e.g. uploaded documents
     visible as text or images), use that content directly without running extraction tools.

### Step 2: Normalise Text

Before comparing, normalise both texts to eliminate formatting noise:

- Collapse paragraph-internal line breaks into spaces (preserve paragraph breaks as double newlines).
- Replace tabs with spaces.
- Collapse runs of multiple spaces into single spaces.
- Strip leading/trailing whitespace from each paragraph.

**When cross-format comparison is detected** (e.g. PDF vs docx):
- If an entire class of elements is missing from one version (e.g. all images, all formulae),
  this is likely a format conversion artefact, not an intentional edit. Flag it with a callout
  rather than marking as deleted.
- Individual missing elements (e.g. one image removed while others remain) should still be
  marked as changes.

**Inform the user** in the chat response that normalisation was applied, e.g.:
"两份文本已做空白归一化处理（合并段内换行、清理多余空格），以下对比仅反映内容级别的差异。"

### Step 3: Compare and Generate Tracked-Changes Markdown

#### Output Structure

The output is a **single continuous document** following the **modified version's structure
and paragraph order**. It is NOT split into segment cards or diff hunks. The reader should
be able to read it top-to-bottom as a complete document, with changes marked inline.

#### Marking Syntax

| Change type | Syntax | Obsidian rendering |
|---|---|---|
| Deleted (in original, not in modified) | `~~deleted text~~` | ~~strikethrough~~ |
| Added (in modified, not in original) | `==added text==` | ==highlight== |
| Unchanged | plain text | normal |

#### Comparison Granularity

- **Default: sentence-level inline interleaving.** Even when a paragraph has been heavily
  rewritten, attempt to align on shared anchor text (common words, phrases, sentence openings)
  and interleave `~~deletion~~` and `==addition==` markers within the same paragraph.
- **Fallback to block-level** only when a paragraph is completely rewritten with no alignable
  anchors. In this case, place the full `~~deleted paragraph~~` first, then the full
  `==added paragraph==` immediately after, separated by a blank line.
- For minor edits (single word/phrase changes), mark inline within the sentence:
  `人们做~~任何涉及未来的~~==很多==决策`

#### Structural Changes

**Paragraph reordering:** Follow the modified version's order. When paragraphs have been
moved relative to the original, insert a callout at the point of reordering:

```markdown
> [!info] 段落重排
> 此段落在原版中位于 [X段落] 之后，修改版将其移至此处。
```

**Entire paragraphs deleted:** Mark the full paragraph with strikethrough.

**Entire paragraphs added:** Mark the full paragraph with highlight.

#### Callout Usage

Use Obsidian callout syntax for three categories of annotations:

| Situation | Callout type | Example |
|---|---|---|
| Editing residue (stray annotations, misplaced notes) | `> [!warning] 编辑残留` | Accidental text like "做动画——" |
| Placeholder text | `> [!warning] 占位符` | Text like "巴拉巴拉模型" |
| Paragraph reordering | `> [!info] 段落重排` | Noting where a section was moved from |

#### Frontmatter

Every output `.md` file MUST begin with a YAML frontmatter block that makes the document
self-explanatory to any reader or agent, even without knowledge of this skill:

```yaml
---
document_type: tracked-changes
description: >
  This document shows the differences between two versions of the same text.
  It follows the modified version's structure with inline change markers.
original: "filename_of_original.ext"
modified: "filename_of_modified.ext"
generated: "YYYY-MM-DD HH:mm"
legend:
  strikethrough: "~~text~~ = content present in the original but removed in the modified version"
  highlight: "==text== = content added or substituted in the modified version"
  plain: "unmarked text = content unchanged between versions"
  callout_warning: "> [!warning] = editing residue or placeholder text detected"
  callout_info: "> [!info] = structural change such as paragraph reordering"
notes: "Text was normalised before comparison (paragraph-internal line breaks merged, extra spaces collapsed). Only content-level differences are shown."
---
```

#### Compatibility Fallback

If the user explicitly states that their software does not support or recognise the `==highlight==`
syntax, switch to strikethrough-only mode:
- `~~deleted text~~` for deletions (same as default).
- Added text appears as plain unmarked text (no special marking).
- Update the frontmatter legend to reflect this.

Do NOT pre-emptively switch to this mode. Only do so when the user reports the issue.

#### File Naming

Derive the output filename from the input:
- Take the original file's base name (without extension).
- Append `_Tracked-Changes.md`.
- Example: input `Presentation-Script_v5_7.pdf` → output `Presentation-Script_v5_7_Tracked-Changes.md`

### Step 4 (Optional): Generate Diff Files

Only produce these when the user explicitly requests a diff. Two formats are available,
and the user may request either or both:

#### `.diff` file (machine-readable)

- **Must be valid unified diff** that can be applied with `git apply`.
- Use normalised plain text as the basis.
- Standard unified diff header: `--- a/original_filename` / `+++ b/modified_filename`
- Context lines, `-` for deletions, `+` for additions.
- Generate by writing both normalised texts to temporary files and running `diff -u`.
- Filename: `OriginalBaseName_Diff.diff`

#### `.txt` file (human-readable)

- Human-readable diff format, does NOT need to be machine-applicable.
- Can use bracketed annotations like `[招募段全部删除]`, `[内容无实质变化]` for clarity.
- Structural changes (paragraph reordering, wholesale deletions) explained in natural language.
- `-` prefix for deleted lines, `+` prefix for added lines, space prefix for context.
- Filename: `OriginalBaseName_Diff.txt`

## Quality Checklist

Before delivering the output, verify:

- [ ] Frontmatter is present and complete with both filenames, legend, and notes.
- [ ] Document follows modified version's paragraph order.
- [ ] All deletions use `~~strikethrough~~`, all additions use `==highlight==`.
- [ ] Unchanged text has no spurious markers.
- [ ] Paragraph reorderings are flagged with `> [!info]` callouts.
- [ ] Editing residue and placeholders are flagged with `> [!warning]` callouts.
- [ ] Cross-format artefacts (if applicable) are noted as callouts, not marked as deletions.
- [ ] If `.diff` file was requested, it passes `git apply --check` against the normalised original.
- [ ] Output files are saved to `/mnt/user-data/outputs/` and presented to the user.
