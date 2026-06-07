# Batch Logic

Dependency-aware batching algorithm for grouping differences into resolution rounds.

---

## Why Batching Matters

Presenting differences one at a time is precise but slow — the user makes N individual
decisions for N differences. Presenting all at once is fast but chaotic — some choices
logically depend on others.

Batching finds the middle ground: group independent decisions together while respecting
dependency order.

---

## Dependency Types

### Hard Dependencies

A hard dependency means Decision X **must** be resolved before Decision Y can be
meaningfully presented, because X's outcome changes what Y means or which options
are available for Y.

Examples:
- A meta-level framework choice (D-1-01) constrains which argument-level positions
  are internally consistent (D-3-*)
- A structural decision about section ordering (D-2-01) affects which expression-level
  comparisons are relevant (D-4-*)
- An argument-level decision in §3 (D-3-05) determines whether a follow-up claim
  in §4 (D-3-08) makes sense

### Soft Dependencies

A soft dependency means Decision X *informs* but does not *constrain* Decision Y.
The user might want to know the outcome of X when deciding Y, but Y is still a
meaningful choice regardless.

Examples:
- An expression-level tone choice in §1 might inform tone choices in §2, but each
  can be decided independently
- Two argument-level differences in separate sections that share a common evidence
  base — resolving one suggests a consistent approach for the other, but does not
  require it

Soft dependencies do **not** block batching. They are noted as context when presenting
the later decision.

---

## Batching Algorithm

### Step 1: Construct the Dependency Graph

For each difference D-i, record its hard dependencies as a list of other difference IDs.
This forms a directed acyclic graph (DAG).

```
D-1-01 → D-3-01, D-3-02, D-3-05
D-1-01 → D-2-01
D-2-01 → D-4-01, D-4-02
D-3-01 → D-3-08
(all others have no hard dependencies)
```

### Step 2: Topological Layering

Assign each difference to a layer:
- **Layer 0**: All differences with no incoming hard dependencies
- **Layer 1**: All differences whose dependencies are all in Layer 0
- **Layer 2**: All differences whose dependencies are all in Layers 0-1
- Continue until all differences are assigned

### Step 3: Form Batches Within Layers

Within each layer, further group by:
1. **Level** — meta-level differences first, then structural, then argument, then expression
2. **Section** — group differences from the same aligned section together

This produces sub-batches that are thematically coherent and cognitively manageable.

### Step 4: Size Control

Target batch sizes of **3-6 decisions**. If a batch exceeds this:
- Split by section or level
- Prioritise keeping related decisions together over hitting exact size targets

If a batch is just 1 decision, present it alone — this happens naturally for high-impact
meta-level choices.

---

## Batch Presentation Order

Present batches in this order:

1. **Meta-level differences** (Layer 0, Level 1) — always first, always one at a time
   if they have downstream impact
2. **Structural differences** (Layer 0-1, Level 2) — after meta choices are settled
3. **Argument-level differences** (Layer 1-2, Level 3) — the bulk of decisions
4. **Expression-level differences** (Layer 2+, Level 4) — last, and often batchable
   in large groups

This mirrors the natural decision process: decide the big picture first, then fill in
details.

---

## Progress Tracking

After each batch is resolved, show progress:

```
Resolution Progress:
  ████████░░░░░░░░░░░░ 40%
  Batch 2 of 5 complete
  Resolved: 8/20 differences
  Remaining: 12 (next batch: 4 argument-level decisions in §3)
```

This helps the user gauge how much effort remains and plan their time.

---

## Efficiency Shortcuts

At any point during resolution, the user may invoke shortcuts:

- **"Default to [Doc X] for all remaining [level]"** — applies a blanket rule to all
  unresolved differences at a specified level
- **"Auto-resolve expression-level"** — Claude picks the clearer/more concise phrasing
  for all expression-level differences, logs choices, and lets the user review after
- **"Just pick the best for all remaining"** — Claude makes its best judgement for all
  unresolved differences, presents the result for review

When shortcuts are used, always produce a summary of the auto-resolved decisions so the
user can spot-check.
