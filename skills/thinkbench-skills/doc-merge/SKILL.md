---
name: doc-merge
description: >
  Multi-document semantic comparison, difference diagnosis, and interactive merge resolution.
  Use when the user uploads or references multiple documents on the same topic and wants to
  compare, contrast, reconcile, or merge them. Trigger on phrases like "compare these documents",
  "what are the differences between", "merge these drafts", "which version is better",
  "reconcile these essays", "diff these articles", "align these texts", or when the user
  provides multiple files covering the same subject and asks for analysis. Also trigger when
  the user mentions having multiple AI-generated drafts, multiple agent outputs, or parallel
  writing attempts that need consolidation. Even if the user just says "help me pick the best
  parts from these", this skill applies.
license: MIT
metadata:
  author: Kaibin Zhang
  version: "1.0.0"
---

# Doc-Merge

Systematic multi-document semantic comparison and interactive merge resolution. Takes multiple
documents on the same topic, diagnoses their differences at multiple levels of abstraction,
and guides the user through resolving conflicts to produce a single authoritative output.

## Core Concept

Traditional text diff tools compare character-by-character. Doc-merge operates at the
**semantic level**: it identifies differences in argumentation, framing, evidence selection,
logical structure, and rhetorical strategy, even when two documents say similar things in
completely different words.

The workflow has two phases:
1. **Diagnose** — automated full-spectrum comparison producing a structured report
2. **Resolve** — interactive, dependency-aware conflict resolution converging on a final document

Users can stop after Phase 1 (just want the analysis) or continue into Phase 2 (want a
merged final version). Always ask after Phase 1 completes.

---

## Phase 1: Diagnose

**Goal**: Produce a structured comparison report that maps differences across all input
documents at multiple granularity levels.

### Step 1: Ingest and Identify

Read all uploaded documents. For each document, extract:
- Title / identifier (use filename or ask user to label them, e.g. "Draft A", "Draft B")
- Overall structure (section headings, logical flow)
- Core thesis or central argument
- Methodology / framework / theoretical lens
- Key claims and supporting evidence

### Step 2: Structural Alignment

Map which sections of each document correspond to each other. Documents may use different
headings or ordering but discuss the same topics. Build an alignment table:

```
Section Topic        | Doc A Section    | Doc B Section    | Doc C Section
---------------------|------------------|------------------|------------------
Introduction         | §1 (paras 1-3)   | §1 (paras 1-2)   | §1 (paras 1-4)
Theoretical framing  | §2               | §2               | [not present]
Empirical analysis   | §3               | §4 (reordered)   | §2
...
```

Flag sections that exist in one document but not others (unique contributions vs omissions).

### Step 3: Multi-Level Difference Analysis

For each aligned section pair/group, classify differences using the four-level taxonomy.
Read `references/difference_taxonomy.md` for the full classification system. The levels are:

1. **Meta-level** — framework, methodology, theoretical lens, implicit assumptions
2. **Structural level** — section organisation, argument ordering, logical flow
3. **Argument level** — specific claims, evidence choices, reasoning chains, causal logic
4. **Expression level** — wording, phrasing, rhetorical style, terminology

For each difference found, record:
- Which level it belongs to
- Which documents diverge and how
- Whether it represents a genuine substantive disagreement or merely a stylistic variation
- Dependencies: does resolving this difference constrain or influence other differences?

### Step 4: Produce Phase 1 Outputs

Phase 1 produces **two complementary outputs** that serve different purposes.
Read `references/output_formats.md` for detailed formatting templates.

#### Output A: Annotated Diff Document

A document that shows differences **in context**, inline within the text. This is the
"see the differences" view — analogous to a code diff but operating at the semantic level.

How it works:
- Take the reference document (the longest, or user-designated) as the base text
- Walk through it section by section following the alignment map
- At each point where other documents diverge, insert annotated markers showing what
  each document says differently
- For sections unique to a non-reference document, append them at the corresponding
  logical position with a `[UNIQUE to Doc X]` marker

The annotated diff uses Markdown formatting conventions:
- `**[Doc A]**` / `**[Doc B]**` prefixes to label sources
- Blockquotes (`>`) to set off each document's version
- `~~strikethrough~~` for content present in one document but absent in another
- Horizontal rules (`---`) between difference blocks
- Inline `(*)` markers at points of divergence within otherwise shared sentences

This output lets the user visually scan where and how documents differ, much like
reading tracked changes in a word processor.

#### Output B: Diagnostic Report

An analytical summary that abstracts away from the raw text and presents differences
as structured, categorised decision points. This is the "understand the differences" view.

The report contains:
1. **Executive Summary** — overall similarity assessment, number of divergence points by
   level, key areas of agreement and disagreement
2. **Alignment Map** — structural correspondence table
3. **Difference Inventory** — itemised list grouped by level (meta → structural → argument
   → expression), each with document-specific descriptions, sub-type tags, and dependency
   annotations
4. **Dependency Graph Summary** — which differences depend on which upstream decisions
5. **Decision Points Count** — "N decisions needed to fully resolve, of which M are
   independent and can be batched in the first round"

#### After presenting both outputs

Ask the user:
> "These are the two diagnostic views — the annotated diff shows differences in context,
> and the report breaks them down by type and dependency. Would you like to proceed to
> interactive resolution to merge these into a single document, or is this analysis
> sufficient for now?"

---

## Phase 2: Resolve

**Goal**: Walk the user through each difference point, collect their decisions, and produce
a unified final document.

Read `references/resolution_workflow.md` for the detailed interaction protocol.

### Batch Construction

Before starting, construct resolution batches using the dependency graph:

1. Identify all difference points with no upstream dependencies → Batch 1
2. Within a batch, group differences that are at the same level and independent of each other
3. After user resolves Batch 1, identify which previously-blocked differences are now
   unblocked → Batch 2
4. Repeat until all differences are resolved

Read `references/batch_logic.md` for the full batching algorithm.

### Per-Batch Interaction Pattern

For each batch:

1. **Present** the differences in this batch, showing each document's version side by side
2. **Contextualise** — briefly explain what is at stake in each choice and whether it
   affects downstream decisions
3. **Collect decision** — use the ask_user_input tool when choices are discrete (pick Doc A
   vs Doc B vs hybrid), or ask in prose when the user may want to rewrite
4. **Confirm** — echo back the decision and its implications before moving on
5. **Update** the internal merged document state

### Resolution Actions

For each difference, the user can:
- **Accept A / B / C** — adopt one document's version wholesale
- **Merge** — combine elements from multiple versions (Claude proposes a merged version,
  user confirms or edits)
- **Rewrite** — discard all versions and write something new (user provides direction,
  Claude drafts)
- **Defer** — skip for now, revisit later

### Final Output

After all batches are resolved, produce the final merged document. Also generate a brief
**merge log** summarising each decision point and the choice made, for traceability.

---

## Output Format

All outputs are in Markdown. For the final merged document, match the genre and style of
the input documents.

---

## Edge Cases

- **More than 3 documents**: The alignment step becomes combinatorial. Prioritise pairwise
  comparisons against a "reference" document (ask the user which one, or default to the
  longest/most complete).
- **Very different structures**: If documents diverge so much at the structural level that
  alignment is infeasible, report this to the user and suggest treating them as
  complementary rather than competing. Offer to produce a synthesis rather than a merge.
- **Near-identical documents**: If differences are minimal (mostly expression-level), skip
  directly to a quick diff-style report and ask if the user wants to just pick one as the
  base and apply minor edits.
- **Non-text content**: Tables, figures, equations — flag these separately and ask the user
  to decide on each.

---

## Reference Files

Read these as needed during execution:

| File | When to Read |
|------|-------------|
| `references/difference_taxonomy.md` | During Step 3 of Phase 1, to classify differences |
| `references/alignment_strategy.md` | During Step 2 of Phase 1, for structural alignment logic |
| `references/output_formats.md` | During Step 4 of Phase 1, for annotated diff and report templates |
| `references/resolution_workflow.md` | At the start of Phase 2, for interaction protocol details |
| `references/batch_logic.md` | Before constructing batches in Phase 2 |

## Template Files

HTML templates for structured output. Use these as scaffolds — replace `{{PLACEHOLDER}}`
values with actual content, and duplicate or remove repeating elements as needed.

| File | Purpose |
|------|---------|
| `assets/diagnostic_report_template.html` | Phase 1 diagnostic report: stats bar, alignment table, collapsible level groups with difference entries, dependency summary |
| `assets/resolution_batch_template.html` | Phase 2 per-batch view: progress bar, decision cards with side-by-side comparison, stakes info, resolution badges, batch decision log |

When the current platform supports HTML artifact rendering, read the appropriate template
file and populate it. When HTML is not supported, fall back to the Markdown formats
described in `references/output_formats.md`.
