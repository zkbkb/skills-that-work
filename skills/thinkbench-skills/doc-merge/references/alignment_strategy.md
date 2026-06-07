# Alignment Strategy

How to map corresponding sections across multiple documents that discuss the same topic
but may be organised differently.

---

## The Alignment Problem

Documents written independently on the same topic will rarely have identical structures.
Common divergences include:

- Different section titles for the same content
- Different ordering of topics
- Different granularity (one document covers a topic in one paragraph; another devotes
  an entire section)
- One document includes a section with no counterpart in the other
- Content that appears in the introduction of one document but the conclusion of another

Alignment must operate on **semantic correspondence**, not surface-level heading matching.

---

## Alignment Algorithm

### Step 1: Extract Section Summaries

For each document, produce a one-sentence summary of each section's core content. This
creates a normalised representation that is structure-agnostic.

### Step 2: Identify Shared Topics

Scan the section summaries across all documents and identify which topics appear in
multiple documents. A "topic" is a coherent unit of discussion — it might be a research
question, a body of evidence, a theoretical claim, a policy recommendation, etc.

### Step 3: Build the Alignment Table

Create a table where:
- Rows = shared topics (plus unique topics flagged as such)
- Columns = documents
- Cells = the section(s) in that document that address this topic

A single section in one document may map to multiple topics if it covers several subjects.
A single topic may map to multiple sections if a document splits it across parts.

### Step 4: Handle Unaligned Content

For sections that have no counterpart in other documents:

- **Unique contribution**: The section adds value that other documents simply lack.
  Flag with `[UNIQUE to Doc X]`.
- **Implicit coverage**: The topic is addressed within another section but not broken out
  separately. Flag with `[EMBEDDED in Doc Y, §N]`.
- **Genuine omission**: The other documents should probably have covered this but did not.
  Flag with `[ABSENT from Doc Y — potential gap]`.

### Step 5: Determine Alignment Confidence

For each row in the alignment table, assess confidence:

- **High**: Sections discuss clearly the same topic, even if differently
- **Medium**: Sections are related but cover overlapping rather than identical ground
- **Low**: Possible correspondence but uncertain — present to user for confirmation

Present low-confidence alignments to the user before proceeding to difference analysis.

---

## Special Cases

### Mismatched Granularity

When one document has a single section covering what another document splits into three
subsections, align the single section to all three and note the granularity difference
as a structural-level difference.

### Cross-Cutting Content

Some content (e.g., methodological notes, definitions, caveats) may appear in different
locations across documents — in the introduction of one, the methodology section of
another, and as footnotes in a third. Treat these as a single alignment unit with a note
about placement variation.

### More Than Three Documents

With N documents, do not attempt N×(N-1)/2 pairwise alignments. Instead:

1. Ask the user to designate a **reference document** (the most complete or the one they
   consider closest to their intended structure)
2. Align all other documents against the reference
3. Note where non-reference documents agree with each other but differ from the reference

If the user does not designate one, default to the longest document as the reference.

---

## Output: The Alignment Map

The alignment map feeds directly into the difference analysis phase. Format it as:

```
## Alignment Map

Reference document: [Doc X]

| # | Topic                    | Doc A        | Doc B        | Doc C        | Notes           |
|---|--------------------------|--------------|--------------|--------------|-----------------|
| 1 | Introduction / framing   | §1           | §1           | §1           | High confidence |
| 2 | Literature context       | §2           | [ABSENT]     | §2 (partial) | Gap in Doc B    |
| 3 | Methodology              | §3           | §2           | [EMBEDDED §1]| Granularity diff|
| 4 | Core analysis            | §4           | §3-4         | §3           | Split in Doc B  |
| 5 | Policy implications      | §5           | §5           | [UNIQUE to C]| §4 in Doc C     |
| 6 | [UNIQUE] Risk assessment | [ABSENT]     | [ABSENT]     | §5           | Only in Doc C   |
```

This table becomes the scaffold for the Phase 1 difference analysis: each row is analysed
for differences at all four taxonomy levels.
