# Resolution Workflow

Detailed interaction protocol for Phase 2: guiding the user through conflict resolution
to produce a single merged document.

---

## Pre-Resolution Setup

Before presenting the first batch of differences to resolve:

1. **Confirm scope**: Ask the user whether they want to resolve all differences or only
   certain levels (e.g., "I only care about argument-level differences; for expression,
   just pick whichever reads better").
2. **Set a base document**: Ask which document should serve as the starting point for the
   merged output. The merge process will modify this base by incorporating decisions. If
   the user has no preference, suggest the most complete document.
3. **Establish defaults**: For any level the user wants to skip, establish a default rule:
   - Expression-level: "Default to Doc A's phrasing" or "Pick the more concise version"
   - Structural-level: "Follow the reference document's structure"
   - This reduces decision fatigue significantly

---

## Per-Difference Presentation

When presenting a difference for resolution, follow this structure:

### 1. Context Header

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Decision D-3-05 | Argument Level | Section: Core Analysis
Batch 2 of 5 | 3 of 4 decisions in this batch
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. The Difference

Present what each document says. Keep excerpts concise — quote the relevant passage,
not entire paragraphs. If the difference is at the argument level or above, summarise
rather than quote verbatim.

```
Doc A argues:
  Innovation lag in Spain stems primarily from institutional fragmentation —
  overlapping regional competencies create coordination failures that dilute
  national innovation strategy.

Doc B argues:
  Spain's innovation deficit is driven by chronically low R&D intensity
  (1.25% of GDP vs EU average of 2.2%), reflecting underinvestment by both
  public and private sectors.
```

### 3. Stakes Assessment

Briefly explain what this choice affects:
- Does it influence later decisions? (List which ones)
- Does it change the overall narrative arc?
- Is this a high-stakes choice or a minor preference?

### 4. Options

Present the available actions clearly:

```
Options:
  [A] Adopt Doc A's version (institutional argument)
  [B] Adopt Doc B's version (investment argument)
  [M] Merge — include both as complementary explanations
  [R] Rewrite — provide your own direction
  [D] Defer — revisit later
```

Use the ask_user_input tool when choices are discrete and bounded. Use prose when the
user may need to explain a nuanced preference or give rewriting instructions.

### 5. Recommendation (when appropriate)

If one option is clearly stronger (better evidenced, more logically consistent, or more
aligned with earlier decisions), say so briefly. Frame it as a suggestion, not a directive:

> "Note: Given your earlier choice to adopt the institutionalist framework (D-1-01),
> Doc A's argument here is more internally consistent. However, Doc B's data point on
> R&D intensity could be incorporated as supporting evidence."

Only offer recommendations when there is a clear basis for one. Do not recommend when
choices are genuinely balanced.

---

## Decision Tracking

Maintain an internal decision log throughout the resolution process:

```
Decision Log:
  D-1-01: Accept A (institutionalist framework)     [Batch 1]
  D-2-01: Accept A (thematic structure)              [Batch 1]
  D-2-02: Accept B (include lit review section)      [Batch 1]
  D-3-01: Merge (combine both evidence sets)         [Batch 2]
  D-3-02: Accept A                                   [Batch 2]
  ...
```

This log serves two purposes:
1. It helps maintain consistency (reference earlier decisions when they constrain later ones)
2. It becomes the merge log appended to the final output

---

## Handling User Responses

### Quick responses

Users may respond in shorthand:
- "A" → Accept Doc A
- "B for all of these" → Apply to entire batch
- "Merge but lead with A's framing" → Merge with specific instruction
- "Skip expression stuff, just use A" → Set default for expression level

Parse intent generously. If ambiguous, confirm briefly before proceeding.

### Rewrite requests

When the user chooses [R] Rewrite:
1. Ask for direction: "What should this section convey? Any specific points to include?"
2. Draft a replacement passage
3. Present it for approval
4. If approved, record as "Rewrite (user-directed)" in the decision log

### Batch-level decisions

The user may want to apply a rule to an entire batch or level:
- "For all expression-level differences, go with Doc B's style"
- "Accept A for everything in this batch except D-3-04"

This is encouraged — it dramatically reduces interaction overhead. Confirm the rule and
apply it, logging each individual decision as "Accept X (batch rule)".

### Changing a previous decision

If the user wants to revise an earlier choice:
- Acknowledge the change
- Check if any downstream decisions were based on the original choice
- If so, flag them: "This change may affect decisions D-3-02 and D-3-07. Would you like
  to revisit those as well?"
- Update the decision log

---

## Final Output Generation

After all differences are resolved (or deferred with defaults applied):

### The Merged Document

Construct the final document by:
1. Starting from the base document
2. Applying each decision in dependency order (meta → structural → argument → expression)
3. Ensuring internal consistency after all changes are applied
4. Performing a final coherence pass: check that transitions, references, and logical
   flow still work after selective merging

### The Merge Log

Append or produce separately a merge log:

```
# Merge Log

Base document: Doc A
Documents compared: Doc A, Doc B, Doc C

## Decisions Summary

| ID     | Level      | Section         | Decision           | Notes                    |
|--------|------------|-----------------|--------------------| -------------------------|
| D-1-01 | Meta       | Overall         | Accept A           | Institutionalist frame   |
| D-2-01 | Structural | Overall         | Accept A           | Thematic structure       |
| D-3-01 | Argument   | Core Analysis   | Merge A+B          | Combined evidence        |
| D-3-02 | Argument   | Core Analysis   | Accept A           | Consistent with D-1-01   |
| D-4-01 | Expression | Introduction    | Accept B           | Batch rule: B's style    |
| ...    | ...        | ...             | ...                | ...                      |

Total decisions: N
  Accept A: X | Accept B: Y | Accept C: Z | Merge: M | Rewrite: R | Deferred: D
```

This log enables traceability and reproducibility — the user can understand exactly how
the final document was assembled and revisit specific decisions if needed.
