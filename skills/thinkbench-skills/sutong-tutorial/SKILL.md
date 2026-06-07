---
name: sutong-tutorial
description: Generate high-density knowledge speed-through tutorials (高密度知识速通教程) that help readers achieve deep understanding with minimal cognitive load. Use this skill when the user requests to "speed through" (速通) a topic or asks for rapid, comprehensive understanding of a subject. Trigger phrases include "速通", "帮我速通", "带着我速通", "速通一下", or similar requests for fast but thorough conceptual coverage  Creates tutorials that build understanding from first principles through logical chains, naturally weaving theory and practice together.
license: MIT
metadata:
  author: Kaibin Zhang
  version: "1.0.0"
---

# 高密度知识速通教程生成器 (Sutong Tutorial Generator)

## Overview

This skill enables Claude to generate "high-density knowledge speed-through tutorials" (高密度知识速通教程) - a specialized educational format that prioritizes deep conceptual understanding over rote memorization. Unlike traditional tutorials that either stay superficial or drown in details, these tutorials trace the "growth logic" (生长逻辑) of concepts: why they emerged, what fundamental problems they solve, and how they evolved from simple to complex.

## Core Philosophy

The speed-through approach is built on three principles:

1. **Essence-first (本质先行)**: Start from first principles, not technical definitions. Ask "why is this needed" before "what is this".

2. **Logical coherence (逻辑连贯)**: Build inevitable causal chains through a "problem → attempt → new problem → refinement" cycle.

3. **Practice fusion (实践融合)**: Tools and methods emerge naturally in problem-solving contexts, not as separate introductions.

## When to Use This Skill

Trigger this skill when the user requests:
- "速通 [topic]" 
- "帮我速通一下 [topic]"
- "带着我速通 [topic]"
- "速通一下 [concept]"
- Any variation asking for rapid but comprehensive understanding

## Workflow

### Step 1: Read the Complete Template

ALWAYS begin by reading the detailed template before generating any content:

```bash
view /home/claude/sutong-tutorial/references/tutorial-template.md
```

This template contains:
- Complete structural templates for each section
- Detailed writing principles and techniques
- Quality checklist
- Examples of correct vs. incorrect approaches

### Step 2: Identify the Topic

Extract the subject the user wants to learn. This can be:
- Technical concepts (e.g., "CORS", "深度学习", "Transformer")
- Academic fields (e.g., "计量经济学", "machine learning")
- Methods or frameworks (e.g., "因果推断", "强化学习")

### Step 3: Generate Following Template Structure

Create the tutorial following this flow:

1. **引入部分** (Introduction): Establish cognitive foundation by positioning the concept and deepening the problem
2. **概念发展部分** (Concept Development): Build understanding framework through origin tracing, early exploration, and key breakthroughs
3. **技术深化部分** (Technical Depth): Explain core mechanisms, extensions, and variations
4. **实践应用部分** (Practical Application): Connect theory to reality through workflows, tools, and accumulated experience
5. **总结升华部分** (Summary): Integrate insights and explore future directions

### Step 4: Apply Writing Principles

Ensure every paragraph:
- Advances understanding (no redundancy)
- Maintains natural flow from intuition to technical detail
- Allows concepts to be "discovered" rather than "defined"
- Surfaces practical knowledge when contextually appropriate

### Step 5: Quality Check

Before presenting, verify:
- Starts from reader's existing knowledge
- Maintains coherent logical chain without jumps
- Naturally integrates theory and practice
- Captures essence over superficial characteristics
- Uses appropriate analogies
- Controls cognitive load effectively

## Key Constraints

1. **Language**: Respond in Chinese with English terms in parentheses for key concepts
2. **Format**: Use prose and paragraphs; avoid excessive bullet points, lists, or headers unless explicitly requested
3. **Length**: No limit, but content must be specific, detailed, and comprehensive
4. **Style**: Build from first principles, use analogies, maintain narrative flow

## Important Reminders

- Do NOT simply list definitions and characteristics
- Do NOT pile up historical details and names unnecessarily  
- Do NOT force-insert tool introductions
- Do NOT use excessive jargon
- DO make complex simple without losing depth
- DO make abstract concrete without losing accuracy
- DO make theory practical without losing elegance

## Reference Material

For complete details on:
- Content structure templates with fill-in examples
- Writing techniques (precision vs. accessibility, analogy art, rhythm control)
- Information organization strategies (spiral deepening, problem-driven, example threading)
- Quality checklist with specific criteria

Refer to: `references/tutorial-template.md`
