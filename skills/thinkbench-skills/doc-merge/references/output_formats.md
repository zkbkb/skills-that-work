# Output Formats

Markdown templates for Phase 1's two outputs: the annotated diff document and the
diagnostic report.

---

## Output A: Annotated Diff Document

The annotated diff embeds differences directly within the flow of the text, so the user
can see divergences in their original context rather than reading about them in the
abstract.

### Construction Method

1. Use the reference document as the base text
2. Reproduce the base text in full, preserving its structure
3. At each point of divergence, insert a **diff block** showing how other documents differ
4. For content unique to non-reference documents, insert it at the logically appropriate
   position with a source marker

### Formatting Conventions

#### Shared text

Reproduce shared passages as normal paragraphs. No special formatting needed — the
absence of markers signals agreement.

#### Divergence within a sentence or paragraph

When documents share most of a passage but diverge on specific phrases, use inline
markers:

```markdown
Germany's innovation strength derives from its **[A]** dense network of applied research
institutions, particularly the Fraunhofer system | **[B]** high R&D expenditure (3.1% of
GDP) and strong industry-academia collaboration | , which bridges basic research and
industrial application.
```

The `|` delimiter separates alternatives inline. Use this for expression-level and
minor argument-level differences where the surrounding context is shared.

#### Divergence at the paragraph or argument level

When entire paragraphs differ, use labelled blockquotes:

```markdown
On the causes of Spain's innovation lag:

> **[Doc A]** Spain's innovation deficit stems primarily from institutional fragmentation.
> Overlapping competencies between central and regional governments create coordination
> failures that dilute national innovation strategy. The absence of a unified governance
> framework means that R&D funding is allocated through competing and sometimes
> contradictory channels.

> **[Doc B]** Spain's innovation deficit is driven by chronically low R&D intensity —
> 1.25% of GDP compared to the EU average of 2.2%. This reflects systematic
> underinvestment by both the public sector (austerity-constrained budgets) and the
> private sector (dominance of SMEs with limited R&D capacity).

`D-3-01` | Argument | Alternative — framework choice (D-1-01) may constrain this decision
```

The metadata line at the end links this divergence to the corresponding entry in the
diagnostic report, giving the user a bridge between the two outputs.

#### Content unique to one document

```markdown
---
**[UNIQUE to Doc C]** The following section appears only in Doc C:

> ### Risk Assessment
>
> Beyond the structural factors discussed above, Spain faces an emerging risk from
> brain drain. Between 2010 and 2020, an estimated 87,000 researchers emigrated...

`[Not present in Doc A or Doc B — potential gap or deliberate scoping choice]`
---
```

#### Content absent from one document

When the reference document includes something that another document omits:

```markdown
The Fraunhofer system's 76 institutes employ over 30,000 staff and generated €2.8bn
in contract research revenue in 2022. ~~**[Absent from Doc B]**~~
```

Use strikethrough wrapping around the absence marker, not around the content itself
(the content exists in the reference; it is the other document that lacks it).

### Section-Level Divergence

When entire sections are ordered differently or structured differently across documents,
note this at the section heading:

```markdown
## Core Analysis

`Structure note: Doc A presents this as a single section. Doc B splits this across
§3 (quantitative analysis) and §4 (qualitative interpretation). Content is aligned
below following Doc A's structure.`

[... annotated content follows ...]
```

### Handling Three or More Documents

With three documents, inline alternatives use the same pattern but extend:

```markdown
**[A]** version one | **[B]** version two | **[C]** version three |
```

For blockquote-level differences, stack the quotes:

```markdown
> **[Doc A]** ...
> **[Doc B]** ...
> **[Doc C]** ...
```

If two documents agree and one diverges, note the agreement:

```markdown
> **[Doc A + Doc C]** Both adopt the institutional fragmentation argument...

> **[Doc B]** Takes the R&D underinvestment approach instead...
```

---

## Output B: Diagnostic Report

The report is an analytical document, not a diff view. It organises differences by
type and dependency rather than by position in the text.

### Template

```markdown
# Document Comparison Report

**Documents compared**: Doc A ("filename_a"), Doc B ("filename_b"), Doc C ("filename_c")
**Reference document**: Doc A (longest / most complete)
**Overall similarity**: [High / Moderate / Low] — [one-sentence characterisation]

**Difference summary**:
| Level       | Count | Independent | Blocked by upstream |
|-------------|-------|-------------|---------------------|
| Meta        | 2     | 2           | 0                   |
| Structural  | 3     | 1           | 2                   |
| Argument    | 10    | 4           | 6                   |
| Expression  | 3     | 3           | 0                   |
| **Total**   | **18**| **10**      | **8**               |

**Decisions needed**: 18 total, first batch of 10 can be resolved immediately.

---

## Alignment Map

| # | Topic              | Doc A | Doc B    | Doc C       | Confidence |
|---|--------------------|-------|----------|-------------|------------|
| 1 | Introduction       | §1    | §1       | §1          | High       |
| 2 | Literature review  | §2    | [ABSENT] | §2 (brief)  | —          |
| 3 | Methodology        | §3    | §2       | [EMBEDDED §1]| High      |
| 4 | Core analysis      | §4    | §3–4     | §3          | High       |
| 5 | Policy implications| §5    | §5       | §4          | High       |
| 6 | Risk assessment    | —     | —        | §5 [UNIQUE] | —          |

---

## Difference Inventory

### Meta-Level

**D-1-01** | Overall Framework
> **Doc A**: National Innovation Systems — institutional complementarities, path dependence
> **Doc B**: Endogenous growth model — R&D intensity, human capital, knowledge spillovers

- Sub-type: Alternative
- Dependencies: D-3-01, D-3-02, D-3-05 depend on this
- Impact: Determines the analytical lens for the entire document

---

### Argument-Level

**D-3-01** | Core Analysis — cause of innovation gap | *Alternative*
> **Doc A**: Institutional fragmentation and coordination failures
> **Doc B**: Low R&D intensity and systematic underinvestment

- Depends on: D-1-01
- Dependencies: D-3-08
- Impact: Determines policy prescription direction

[... continue for all differences ...]

---

## Dependency Overview

D-1-01 (framework) → D-3-01, D-3-02, D-3-05
D-1-01 → D-2-01 (structure)
D-2-01 → D-4-01, D-4-02
D-3-01 → D-3-08

**First batch** (no upstream dependencies): D-1-01, D-1-02, D-2-03, ...
**Blocked until first batch resolves**: D-2-01, D-3-01, D-3-02, ...
```

---

## Merge Log Template

Used at the end of Phase 2 to record all decisions:

```markdown
# Merge Log

**Base document**: Doc A
**Documents compared**: Doc A, Doc B, Doc C
**Date**: [timestamp]

| ID     | Level      | Section         | Decision    | Detail                      |
|--------|------------|-----------------| :---------: |-----------------------------|
| D-1-01 | Meta       | Overall         | Accept A    | Institutionalist framework   |
| D-2-01 | Structural | Overall         | Accept A    | Thematic structure           |
| D-3-01 | Argument   | Core Analysis   | Merge A+B   | Combined both evidence sets  |
| D-4-01 | Expression | Introduction    | Accept B    | Batch rule: B's phrasing     |

**Summary**: 18 decisions — Accept A: 8 | Accept B: 4 | Merge: 3 | Rewrite: 2 | Deferred: 1
```
