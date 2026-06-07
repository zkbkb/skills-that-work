# Difference Taxonomy

A four-level classification system for semantic differences between documents. When
analysing differences, categorise each one into exactly one level. If a difference spans
multiple levels, split it into separate entries.

---

## Level 1: Meta-Level Differences

Differences in the foundational choices that shape the entire document. These are the
highest-impact, lowest-frequency differences. Resolving them first is critical because
they cascade into all lower levels.

### What to look for

- **Theoretical framework**: Does Doc A use institutionalism while Doc B uses evolutionary
  economics? Does one adopt a Marxist lens while the other is neoclassical?
- **Methodology**: Qualitative vs quantitative approaches, different statistical methods,
  different case selection logic
- **Scope and boundaries**: Different definitions of the research question, different
  temporal or geographical boundaries
- **Epistemological stance**: Positivist vs interpretivist, deductive vs inductive
- **Implicit assumptions**: Unstated premises that differ between documents (e.g., one
  assumes rational actors, the other assumes bounded rationality)

### Classification signals

- The difference affects the meaning or validity of arguments across multiple sections
- Changing this choice would require rewriting substantial portions of the document
- The two approaches are not trivially reconcilable (they represent genuine alternatives)

### Example

> Doc A frames innovation capacity through National Innovation Systems theory, emphasising
> institutional complementarities. Doc B uses an endogenous growth model, focusing on
> R&D investment and human capital accumulation. This is a meta-level difference because
> the entire analytical apparatus differs.

---

## Level 2: Structural Differences

Differences in how the argument is organised and sequenced. These affect readability,
logical flow, and emphasis, but do not necessarily change the substantive content.

### What to look for

- **Section ordering**: Same content presented in different sequence
- **Hierarchy**: One document nests a topic as a subsection; another treats it as a
  standalone section
- **Grouping logic**: Different principles for organising material (chronological vs
  thematic, by country vs by indicator)
- **Emphasis through placement**: What comes first signals what the author considers most
  important
- **Presence/absence of sections**: One document includes a literature review; the other
  jumps straight to analysis
- **Transitional logic**: How sections connect — one uses explicit transitions, the other
  relies on implicit logical flow

### Classification signals

- The same substantive points appear in both documents but in different locations
- Rearranging sections in one document could make it structurally match the other without
  changing any claims
- The difference is about *where* something is said, not *what* is said

### Example

> Both documents discuss Germany's patent intensity and Spain's structural funds reliance.
> Doc A discusses these under separate country chapters; Doc B discusses them under
> thematic headings (inputs vs outputs). The analytical content overlaps but the organising
> principle differs.

---

## Level 3: Argument-Level Differences

Differences in the specific claims, evidence, reasoning chains, or causal logic within
aligned sections. This is typically the most populated level.

### What to look for

- **Different claims**: Doc A argues X causes Y; Doc B argues Z causes Y
- **Different evidence**: Same claim supported by different data, citations, or examples
- **Different logical chains**: Same premise and conclusion but different intermediate steps
- **Different strength of claims**: One asserts definitively; the other hedges
- **Different causal direction**: Doc A says A→B; Doc B says B→A
- **Different scope of claims**: One generalises; the other qualifies with conditions
- **Omissions**: A relevant argument present in one document but absent in the other
- **Contradictions**: Directly opposing claims on the same point

### Sub-classification

For argument-level differences, further tag each as:

- **Complementary** — both arguments can coexist; including both strengthens the final
  document
- **Alternative** — the arguments are different approaches to the same point; the user
  must choose or synthesise
- **Contradictory** — the arguments directly conflict; only one can be retained, or a new
  reconciliation must be constructed

### Classification signals

- The difference changes the intellectual content of a specific section
- It could be resolved locally within that section without affecting the rest
- It concerns *what* is argued, not *how* it is said

### Example

> On the topic of Spain's innovation lag, Doc A attributes it primarily to fragmented
> governance structures (argument: institutional failure), while Doc B attributes it to
> insufficient R&D spending as a share of GDP (argument: input deficit). These are
> alternative arguments — both may be valid, but they imply different policy prescriptions.

---

## Level 4: Expression-Level Differences

Differences in wording, phrasing, terminology, tone, and rhetorical style. These affect
readability and voice but do not change the substantive meaning.

### What to look for

- **Word choice**: "utilise" vs "use", "significant" vs "substantial"
- **Sentence structure**: Active vs passive voice, complex vs simple sentences
- **Terminology**: Different technical terms for the same concept (especially across
  disciplinary traditions)
- **Tone**: Formal vs accessible, cautious vs assertive
- **Specificity**: One uses precise figures; the other uses qualitative descriptions
- **Citation style**: Inline citations vs footnotes, heavy citation vs light citation
- **Rhetorical devices**: Use of analogies, examples, hedging language

### Classification signals

- Replacing one version's phrasing with the other's would not change the argument
- The difference is about *how* something is said, not *what* is said
- A reader would understand the same point from either version

### When expression-level differences matter more than usual

Sometimes expression-level choices carry implicit meaning:
- Hedging language ("may contribute to") vs assertion ("drives") signals different
  confidence levels — this could actually be an argument-level difference in disguise
- Discipline-specific terminology signals theoretical allegiance — this could be a
  meta-level marker

If in doubt about whether a difference is expression-level or argument-level, classify it
at the higher level (argument). It is better to over-weight a difference than to dismiss
a substantive disagreement as mere style.

---

## Difference Record Format

For each difference identified, record:

```
ID:           D-[level number]-[sequence number]  (e.g. D-3-05)
Level:        Meta / Structural / Argument / Expression
Section:      Which aligned section this falls under
Documents:    Which documents diverge (e.g. "A vs B+C" or "A vs B vs C")
Description:  What the difference is, neutrally stated
Doc A says:   [Brief summary of Doc A's position]
Doc B says:   [Brief summary of Doc B's position]
(Doc C says:) [If applicable]
Sub-type:     [For Level 3 only: Complementary / Alternative / Contradictory]
Dependencies: [List of other difference IDs that depend on this decision]
Impact:       [Brief note on what resolving this difference affects downstream]
```
