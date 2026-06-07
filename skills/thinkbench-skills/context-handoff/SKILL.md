---
name: context-handoff
description: >
  Generate structured context handoff documents that capture the essential state of a conversation
  for seamless continuation in a new session. Use this skill when the user wants to carry over
  context from the current conversation to a new one. Trigger phrases include "context handoff",
  "/handoff", "/compact", "生成交接文档", "帮我整理上下文", "把这次对话的内容整理出来",
  "carry over context", "continue in a new chat", or any expression of wanting to preserve
  conversation context for future use. Also trigger when the user says things like
  "我想把这个对话的内容带到下一个对话", "帮我做一个 summary 以便下次继续",
  or "save this conversation's state". Even if the user doesn't use these exact phrases,
  trigger this skill whenever they express intent to structurally preserve the current
  conversation's context for reuse.
license: MIT
metadata:
  author: Kaibin Zhang
  version: "1.0.0"
---

# Context Handoff — Conversation State Compression for Session Continuity

## Overview

This skill generates a structured "handoff document" that compresses the current conversation
into a state summary optimised for continuing work in a new session. It is inspired by
Claude Code's `/compact` mechanism but redesigned for general-purpose conversations in claude.ai
(academic research, creative projects, technical exploration, brainstorming, and more).

The core principle: **what gets compressed is not "text" but "resumable working state."**

## When to Use This Skill

Trigger when the user expresses any of these intents:

- Wants to carry conversation context into a new chat session
- Wants to preserve discussion state before a conversation gets too long
- Asks for a structured summary specifically for continuation purposes
- Uses trigger phrases: "context handoff", "/handoff", "/compact", "生成交接文档",
  "帮我整理上下文", "carry over context", etc.

**This skill is NOT for:**
- General summarisation requests (use normal summary capabilities)
- Note-taking or meeting minutes (different structure needed)
- The user just wanting a quick recap (overkill)

## Workflow

### Step 1: Read the Prompt Template

ALWAYS begin by reading the full prompt template before generating the handoff document:

```
Read: references/prompt-template.md  (relative to this skill's directory)
```

This template contains the complete compression rubric with all 12 modules,
analysis instructions, output format specifications, and examples.

### Step 2: Check for Additional Focus Instructions

The user may attach optional focus instructions when triggering, e.g.:
- "生成交接文档，重点关注我们讨论的论文框架部分"
- "context handoff, focus on the design decisions we made"
- "/handoff focus on the technical implementation details"

If present, these instructions should be incorporated into the compression process
as additional emphasis areas — they supplement (not replace) the standard 12-module schema.

If no additional instructions are given, proceed with the standard schema.

### Step 3: Perform Analysis

**If extended thinking is enabled:**
Conduct the full chronological analysis in the thinking block. The analysis should:
- Walk through every message in the conversation chronologically
- For each turn, identify: user's request/intent, Claude's approach, key decisions,
  specific details (files, concepts, frameworks), corrections made, user feedback
- Double-check for completeness and accuracy

Then output ONLY the `<summary>` section.

**If extended thinking is NOT enabled:**
Output an explicit `<analysis>` section first (following the rubric's analysis instructions),
then output the `<summary>` section. The analysis constraints from the prompt template
(chronological message-by-message review, completeness verification) apply in both modes.

### Step 4: Generate the Handoff Document

Generate the handoff document as a Markdown file following the 12-module schema.
The document must begin with the continuation prefix (see prompt template).

**Language strategy:**
- Module headings: English (as structural anchors)
- Content body: Use whichever language most precisely represents the original meaning.
  If the original discussion was in a non-English language, preserve that language
  and add English annotations in parentheses for key terms and concepts.
- Always choose the language that achieves maximum semantic fidelity.

### Step 5: Output the Document

1. Generate the handoff document as a `.md` file
2. Save to `/mnt/user-data/outputs/` for user download
3. Also display the document in the conversation for immediate reference

## The 12-Module Schema

The handoff document follows this structure (detailed rubric in prompt-template.md):

| # | Module | Purpose |
|---|--------|---------|
| 1 | Primary Request, Intent & Intent Evolution | What the user asked for and how their intent shifted |
| 2 | Key Concepts & Frameworks | Important concepts, theories, frameworks, terminology |
| 3 | Problem Solving & Reasoning Evolution | How problems were solved; logic chain and reasoning shifts |
| 4 | Sources, References & Research | What was read, searched, cited (input side) |
| 5 | Outputs & Artefacts | What was produced (output side) |
| 6 | Corrections, Revisions & Lessons | Errors, corrections, negative feedback, lessons learnt |
| 7 | User Preferences & Constraints | Hard rules, style preferences, negative instructions |
| 8 | All User Messages & Response Summary | Verbatim user messages + summarised Claude responses |
| 9 | Pending Tasks | Explicitly requested but unfinished work |
| 10 | Current Work | Precise save-point: what was being worked on at interruption |
| 11 | Optional Next Step | Suggested (not prescribed) next action, with verbatim quotes |
| 12 | Meta-context | Date, topic tags, associated project/course, prior/subsequent chats |

## Key Design Principles

These principles are borrowed from Claude Code's `/compact` and adapted:

1. **Compress state, not text.** The output is not a literary summary but a resumable
   working state — like a save file in a game.

2. **Tool calls and research are first-class citizens.** If web searches, deep research,
   or file reads occurred, their results and sources must be captured.

3. **Constrained output format prevents drift.** The 12-module schema acts as a checklist,
   reducing the chance of omitting critical details.

4. **User messages are preserved near-verbatim.** User messages are typically small in
   token count but high in information value. Preserve them fully; summarise only
   Claude's responses.

5. **The continuation prefix is non-negotiable.** It explicitly tells the next Claude
   instance that this is a session continuation, not background reading.

6. **Optional Next Step respects user autonomy.** The user may want to continue the
   same thread or take the context in a new direction. Next steps are suggestions only.

## Important Reminders

- Do NOT produce a generic summary. Every module must contain specific, actionable details.
- Do NOT omit modules. If a module is genuinely not applicable, write "N/A" with a brief reason.
- Do NOT start working on "next steps" after generating the document. The handoff document
  is the final deliverable of this skill invocation.
- Do NOT fabricate or hallucinate content that was not in the conversation.
- DO preserve the user's exact words whenever possible, especially feedback and corrections.
- DO include verbatim quotes in Optional Next Step to prevent task drift.
- DO note any files that were uploaded, read, or generated during the conversation.

## Reference Material

For the complete compression rubric, output format, continuation prefix template,
and detailed per-module instructions:

Refer to: `references/prompt-template.md`
