# Context Handoff — Prompt Template & Compression Rubric

This document contains the complete instructions for generating a context handoff document.
It is the core "rubric" that governs the compression process.

---

## Continuation Prefix

Every handoff document MUST begin with the following prefix. This tells the receiving
Claude instance how to interpret the document:

```
---
type: context-handoff
generated: [ISO 8601 date of generation]
source_conversation: [brief topic identifier]
---

> **Continuation Notice:** This conversation is a continuation of a previous session.
> The structured summary below captures the essential context from that session.
> Please read it carefully before proceeding, and treat it as the shared history
> between us — not as background reading, but as work we have already done together.
> If you need more detail on any point, ask the user rather than guessing.
```

---

## Analysis Instructions

Before producing the final summary, you must conduct a thorough analysis of the
entire conversation. This analysis serves as a completeness check.

### Analysis Process

1. **Chronologically walk through every message in the conversation.** For each
   message or section, identify:
   - The user's explicit requests and intents
   - Your approach to addressing those requests
   - Key decisions made, concepts introduced, frameworks adopted
   - Specific details: file names, uploaded documents, key terms, referenced sources,
     generated artefacts, search queries and results
   - Any errors, misunderstandings, or corrections — and how they were resolved
   - Pay special attention to user feedback, especially instances where the user
     told you to change approach, adjust tone, fix mistakes, or do something differently

2. **Double-check for completeness and accuracy.** After the chronological walkthrough,
   verify that you have not missed:
   - Any user message (these are high-value, low-volume — missing even one risks
     losing critical intent signals)
   - Any significant reasoning shift or logical pivot
   - Any user-stated constraint or preference
   - Any file read, web search, or deep research conducted
   - Any artefact generated (documents, code, frameworks, etc.)

### Where to Place the Analysis

- **If extended thinking is enabled:** Conduct the analysis in the thinking block.
  Output only the `<summary>` section to the user.
- **If extended thinking is NOT enabled:** Output the analysis in explicit
  `<analysis>` tags before the `<summary>`, using the same structure and rigour
  described above. Example:

```xml
<analysis>
[Chronological walkthrough of every conversation turn, covering all points above]
[Completeness verification checklist]
</analysis>

<summary>
[The 12-module handoff document]
</summary>
```

---

## The 12-Module Schema

Your summary MUST include ALL of the following sections. If a section is genuinely
not applicable to this conversation, write "N/A — [brief reason]" rather than
omitting it entirely.

---

### 1. Primary Request, Intent & Intent Evolution

Capture the user's original request in specific, concrete terms — not abstracted
"goals" but what they actually asked for. Then trace how their intent evolved
through the conversation: did they refine their question? Change direction?
Add constraints? Narrow or broaden scope?

**What to include:**
- The initial request (as specifically as possible)
- Each significant shift in intent, with what triggered the shift
- The final/current state of the user's intent

---

### 2. Key Concepts & Frameworks

List all important concepts, theories, frameworks, methodologies, technical terms,
and domain-specific vocabulary that were discussed or adopted during the conversation.
This section serves as a "vocabulary and conceptual foundation" for the next session.

**What to include:**
- Theoretical frameworks referenced or constructed
- Technical terms and their working definitions as used in this conversation
- Methodological choices (e.g., "we decided to use comparative case study approach")
- Any distinctions or taxonomies established (e.g., "we distinguished between X-as-A
  and X-as-B")

---

### 3. Problem Solving & Reasoning Evolution

Document how problems were approached and solved, AND trace the broader evolution
of reasoning and logic throughout the conversation. This module captures both
concrete problem-solving events and the abstract trajectory of thought.

**What to include:**
- Specific problems encountered and how they were resolved
- Alternatives considered and reasons for elimination
- Pivotal reasoning shifts — moments where the direction of thinking changed
- Key logical steps: "We started from A, which led us to consider B, but because
  of C, we concluded D"
- Any hypotheses that were tested, validated, or rejected
- Ongoing unresolved questions or tensions

This module is not limited to academic or technical contexts. In any discussion
involving deliberation — design decisions, brainstorming, strategic planning,
creative choices — there is a reasoning path worth capturing.

---

### 4. Sources, References & Research

Record everything that was consulted, read, or searched during the conversation.
This is the "input side" — what information entered the conversation.

**What to include:**
- Files uploaded by the user (with file names)
- Web searches conducted (key queries and what was found)
- Deep research results (sources consulted, key findings)
- Documents or articles read or referenced
- Any data sources consulted
- For each source: a brief note on what it contributed to the conversation

---

### 5. Outputs & Artefacts

Record everything that was produced during the conversation. This is the "output
side" — what the conversation generated.

**What to include:**
- Documents, files, or artefacts created (with file names/types)
- Frameworks, schemas, or structural designs drafted
- Key passages, analyses, or formulations produced
- For each output: what it is, why it was created, and any modifications/iterations
  it went through

---

### 6. Corrections, Revisions & Lessons

Document all instances where errors were made and corrected, or where the user
provided negative feedback that changed the approach. This is the "error memory"
that prevents the next session from repeating mistakes.

**What to include:**
- Misunderstandings by Claude and how they were corrected
- User feedback of the form "that's wrong", "don't do X", "change this approach"
- Approaches that were tried and failed, with reasons for failure
- Specific instructions the user gave for how to do things differently
- Lessons that should carry forward (e.g., "user prefers X over Y in this context")

---

### 7. User Preferences & Constraints

Extract and list all explicit preferences, constraints, rules, and negative
instructions the user expressed during the conversation. These are "hard rules"
for the next session.

**What to include:**
- Format preferences ("use prose, not bullet points")
- Scope constraints ("only focus on X, don't touch Y")
- Style preferences ("more concise", "use academic tone")
- Negative instructions ("don't do X", "avoid Y approach")
- Tool/method preferences ("use web search for this", "don't generate files")
- Any recurring patterns in how the user prefers to work

---

### 8. All User Messages & Response Summary

This is a chronological log of the entire conversation flow. User messages should
be preserved as close to verbatim as possible. Claude's responses should be
summarised concisely.

**Format:**

```
- User [Turn 1]: [verbatim or near-verbatim user message]
  → Claude: [concise summary of Claude's response — what was done, what was said]
- User [Turn 2]: [verbatim or near-verbatim user message]
  → Claude: [concise summary]
...
```

**Rules:**
- User messages are typically low in token count but high in information value.
  Preserve them fully in the vast majority of cases.
- Only summarise user messages if they contain very large embedded content
  (e.g., a full article pasted inline). In such cases, note "[user provided full
  text of article X — omitted here for brevity]".
- Claude's responses should be summarised to capture: what action was taken,
  what key points were made, what was produced.
- Maintain chronological order strictly.

---

### 9. Pending Tasks

List all tasks that the user explicitly requested but that remain unfinished.

**What to include:**
- Only tasks the user explicitly asked for (not inferred tasks)
- Current status of each task (not started / partially complete / blocked)
- Any relevant context for why the task is pending

---

### 10. Current Work

Describe precisely what was being worked on at the moment this handoff was
requested. This is the "save point" — the exact state of work at interruption.

**What to include:**
- What specific task or discussion was in progress
- How far along it was
- What had been completed vs. what remained
- Any relevant files, drafts, or intermediate outputs
- The state of any ongoing analysis or deliberation

---

### 11. Optional Next Step

**This section is OPTIONAL.** Only include it if there is a clear, natural next
step that follows directly from the current work. If the conversation reached
a natural conclusion, write "N/A — conversation concluded; next direction is
at the user's discretion."

**Critical constraints:**
- The next step must be DIRECTLY in line with the user's most recent explicit
  requests and the work being done immediately before this handoff.
- Do NOT suggest tangential tasks or revisit old completed requests.
- If suggesting a next step, include **verbatim quotes** from the most recent
  conversation showing exactly what was being worked on and where it left off.
  This prevents task drift.
- Remember: the user may want to take the context in an entirely new direction.
  This section is a suggestion, not a prescription.

---

### 12. Meta-context

Provide metadata about this conversation for organisational purposes.

**What to include:**
- **Date**: When this conversation took place
- **Topic tags**: 2-5 descriptive tags for the conversation's subject matter
- **Associated project/course**: If the conversation relates to a specific project,
  course, or ongoing effort, name it
- **Prior conversations**: If this conversation explicitly referenced or continued
  from a previous session, note it
- **Subsequent intent**: If the user indicated what they plan to do next with
  this context, note it

---

## Output Format Example

Below is an abbreviated example showing the expected structure. The actual handoff
document should be much more detailed.

```markdown
---
type: context-handoff
generated: 2026-03-06
source_conversation: AI dynamic capabilities essay framework
---

> **Continuation Notice:** This conversation is a continuation of a previous session.
> The structured summary below captures the essential context from that session.
> Please read it carefully before proceeding, and treat it as the shared history
> between us — not as background reading, but as work we have already done together.
> If you need more detail on any point, ask the user rather than guessing.

## 1. Primary Request, Intent & Intent Evolution

The user initially asked for help reviewing literature on AI and dynamic capabilities
of firms (企业动态能力, dynamic capabilities) for an Economics of Innovation course essay.
The intent evolved from "help me find relevant papers" → "help me structure an argument
about whether AI generates new capabilities or requires existing ones" → "help me
articulate the causal identification problem (因果识别问题, causal identification problem)
I've discovered in this literature."

## 2. Key Concepts & Frameworks

- 动态能力框架 (Dynamic Capabilities Framework) — Teece (1997)
- AI-as-capability vs. AI-as-enabler — distinction established in this conversation
- 因果识别问题 (Causal Identification Problem) — the core analytical insight
- ...

## 3. Problem Solving & Reasoning Evolution

We began by surveying the empirical literature, which surfaced a pattern: studies
claiming AI "creates" dynamic capabilities could not distinguish this from firms
with pre-existing capabilities being better at adopting AI. This led to the user's
key insight about the fundamental causal identification problem...

[etc. for all 12 modules]
```

---

## Handling Additional Focus Instructions

The user may provide additional compression focus when triggering the handoff, e.g.:
- "context handoff, focus on the design decisions"
- "生成交接文档，重点保留我们讨论的框架部分"

When additional focus instructions are present:
1. Still generate ALL 12 modules (do not skip any)
2. Give proportionally more detail and specificity to the modules relevant
   to the user's focus area
3. Other modules can be slightly more concise, but must still contain
   all essential information
4. Note the focus instruction in the Meta-context section

---

## Quality Checklist

Before finalising the handoff document, verify:

- [ ] Continuation prefix is present and correctly filled in
- [ ] All 12 modules are present (with N/A noted where genuinely not applicable)
- [ ] User messages in Module 8 are preserved near-verbatim
- [ ] No fabricated or hallucinated content
- [ ] Corrections and user feedback (Module 6) are specific and actionable
- [ ] Current Work (Module 10) precisely describes the save-point state
- [ ] Optional Next Step (Module 11) includes verbatim quotes if present
- [ ] Language follows semantic fidelity principle (original language preserved,
      English annotations where needed)
- [ ] Meta-context (Module 12) has date, tags, and project association filled in
