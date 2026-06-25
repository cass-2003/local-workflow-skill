---
name: research-paper-writing
description: AI辅助学术论文写作最佳实践：工作流架构、分章节Prompt工程、学术写作风格指南、常见陷阱与缓解策略、Prompt模板库
disable-model-invocation: false
user-invocable: false
---

# AI-Assisted Academic Paper Writing: Best Practices

> A practical reference for researchers using LLMs to draft, refine, and polish scientific papers.
> Last updated: 2026-03

---

## Table of Contents

1. [Overview & Philosophy](#1-overview--philosophy)
2. [Workflow Architecture](#2-workflow-architecture)
3. [Prompt Engineering by Section](#3-prompt-engineering-by-section)
4. [Academic Writing Style Guide](#4-academic-writing-style-guide)
5. [Common Pitfalls & Mitigations](#5-common-pitfalls--mitigations)
6. [Tool Ecosystem](#6-tool-ecosystem)
7. [Section-Specific Strategies](#7-section-specific-strategies)
8. [Prompt Template Library](#8-prompt-template-library)

---

## 1. Overview & Philosophy

### The Right Mental Model

AI is a **writing accelerator**, not a writing replacement. The researcher owns:
- The research question and hypothesis
- Experimental design and data
- Interpretation of results
- Intellectual contribution claims

AI assists with:
- Drafting prose from structured notes
- Improving clarity and flow
- Suggesting transitions and hedging language
- Reformatting and restructuring sections

### Core Principle: Input Quality Determines Output Quality

The single biggest lever is what you feed the model. Bullet-point notes → mediocre draft. Structured outline with key claims, evidence, and citations → publication-ready prose.

**Bad input:**
```
Write the introduction for my paper about transformers.
```

**Good input:**
```
Write an introduction for a NeurIPS paper. Context:
- Problem: Transformer attention is O(n²) — bottleneck for long sequences
- Gap: Existing sparse attention methods sacrifice accuracy for speed
- Our contribution: FlashLinear — linear attention with no accuracy loss on GLUE/LongBench
- Tone: confident but measured, cite [Vaswani 2017] and [Dao 2022]
- Length: ~300 words, 3 paragraphs (hook → gap → contribution)
```

---

## 2. Workflow Architecture

### Phase 1: Pre-Writing (Research → Structure)

```
Raw research notes
      ↓
Outline with claims + evidence per section
      ↓
Key citations identified (Semantic Scholar / Elicit)
      ↓
Section-by-section bullet points
```

**Tools**: Elicit (literature synthesis), Semantic Scholar (citation graph), Obsidian/Notion (note organization)

### Phase 2: Drafting (Structure → Prose)

```
Section bullet points + context prompt
      ↓
LLM first draft
      ↓
Researcher review: facts, logic, tone
      ↓
Targeted revision prompts
      ↓
Section draft v1
```

**Tools**: Claude / GPT-4 / Gemini (drafting), Writefull (academic phrasing), Paperpal (journal-specific style)

### Phase 3: Refinement (Prose → Submission-Ready)

```
Full draft assembled
      ↓
Consistency pass (terminology, notation, tense)
      ↓
Style pass (hedging, formality, transitions)
      ↓
Citation integration check
      ↓
Venue-specific formatting (Overleaf AI / LaTeX)
```

**Tools**: Grammarly Academic, Writefull for Overleaf, SciSpace (reading + writing), journal style checkers

### Phase 4: Verification (Never Skip)

- Every factual claim: verify against your own data or cited source
- Every citation the AI suggests: confirm it exists and says what AI claims
- Every number: cross-check with your tables/figures
- Run plagiarism check (iThenticate / Turnitin)

---

## 3. Prompt Engineering by Section

### Universal Prompt Structure

```
[ROLE] You are an expert academic writer in [field].
[CONTEXT] This is a [venue] paper about [topic].
[INPUT] Here are my notes/outline: [structured notes]
[CONSTRAINTS] Tone: formal. Length: ~[N] words. Tense: [past/present].
[CITATIONS] Integrate these references: [list]
[OUTPUT] Write [section name] following [venue] conventions.
```

### Abstract Prompt

```
Write a structured abstract (~250 words) for a [venue] paper.
Follow this structure:
1. Motivation (1-2 sentences): why this problem matters
2. Problem statement (1 sentence): what is unsolved
3. Method (2-3 sentences): what we propose
4. Results (2-3 sentences): key quantitative findings
5. Significance (1 sentence): broader impact

My notes:
- Problem: [your problem]
- Method: [your approach]
- Key results: [metric1=X, metric2=Y, baseline=Z]
- Significance: [impact statement]

Avoid: passive voice overuse, vague claims, missing numbers.
```

### Introduction Prompt

```
Write a 4-paragraph introduction for a [field] paper submitted to [venue].

Paragraph structure:
1. Hook + broad motivation (why this research area matters)
2. Specific problem + existing limitations (cite [ref1], [ref2])
3. Our approach + key insight (what makes it different)
4. Contributions list (3-4 bullet points) + paper organization

Key claims to include:
- [claim 1 with evidence]
- [claim 2 with evidence]

Tone: confident, not overclaiming. Use "we propose", "we demonstrate".
Avoid: "In this paper, we..." as the opening sentence.
```

### Related Work Prompt

```
Write a related work section (~500 words) organized into [N] subsections.

Subsections:
1. [Topic A]: covers [ref1, ref2, ref3] — note how our work differs
2. [Topic B]: covers [ref4, ref5] — note the gap we address
3. [Topic C]: covers [ref6, ref7] — note orthogonal vs. complementary

For each subsection:
- Summarize the line of work in 2-3 sentences
- Identify the limitation or gap
- One sentence positioning our work

Tone: objective, not dismissive of prior work. Use "while X achieves Y, it does not address Z".
```

### Methodology Prompt

```
Write the methodology section for a [field] paper. Be precise and reproducible.

Structure:
1. Problem formulation (define notation: [your notation])
2. Method overview (high-level description + figure reference)
3. [Component A]: [detailed description]
4. [Component B]: [detailed description]
5. Training/optimization details (if applicable)
6. Complexity analysis (if applicable)

My technical notes:
[paste your detailed technical notes here]

Requirements:
- Define all symbols on first use
- Use past tense for what we did, present tense for the model description
- Include equation placeholders as: [EQ: description]
- Length: ~800 words
```

### Experiments Prompt

```
Write the experiments section for a [venue] paper.

Structure:
1. Experimental setup
   - Datasets: [list with stats]
   - Baselines: [list with citations]
   - Metrics: [list with definitions]
   - Implementation details: [hardware, hyperparams]

2. Main results
   - Reference Table [N]: [describe what the table shows]
   - Key finding: our method achieves [X] vs. best baseline [Y] ([Z]% improvement)
   - Analysis of why

3. Ablation studies
   - Component A removed: [result]
   - Component B removed: [result]
   - Interpretation

4. Analysis / qualitative results (if applicable)

Write in past tense. Be specific with numbers. Avoid hedging on your own results.
```

### Conclusion Prompt

```
Write a conclusion section (~200 words) for a [field] paper.

Structure:
1. Summary (2-3 sentences): restate problem + our approach + key result
2. Broader impact (1-2 sentences): what this enables
3. Limitations (2-3 sentences): honest, specific, not dismissive
4. Future work (2-3 sentences): concrete next steps

Key points to include:
- Main result: [your result]
- Limitation: [honest limitation]
- Future direction: [specific next step]

Avoid: introducing new claims, repeating the abstract verbatim, vague "future work" statements.
```

---

## 4. Academic Writing Style Guide

### Formality Levels

| Context | Style | Example |
|---------|-------|---------|
| Claims about your work | Confident, direct | "Our method achieves..." |
| Claims about others | Attributed, neutral | "Smith et al. report..." |
| Uncertain findings | Hedged | "This suggests...", "may indicate" |
| Limitations | Honest, specific | "Our approach is limited to..." |
| Future work | Conditional | "Future work could explore..." |

### Hedging Language (Use Appropriately)

**Strong hedges** (high uncertainty):
- "may", "might", "could", "appears to", "seems to"
- "it is possible that", "one interpretation is"

**Moderate hedges** (reasonable confidence):
- "suggests", "indicates", "is consistent with"
- "tends to", "generally", "in most cases"

**Weak hedges** (near-certain):
- "demonstrates", "shows", "confirms"
- "we observe that", "results indicate"

**Rule**: Match hedge strength to your actual confidence. Over-hedging your own results weakens the paper. Under-hedging others' limitations is dishonest.

### Tense Conventions

| Section | Tense | Rationale |
|---------|-------|-----------|
| Abstract | Mixed (past for results, present for claims) | Standard |
| Introduction | Present | Describing current state of field |
| Related Work | Past | Describing completed prior work |
| Methodology | Present (model) / Past (what we did) | Convention |
| Experiments | Past | Completed experiments |
| Results | Past | Observed results |
| Conclusion | Past (summary) / Present (implications) | Standard |

### Transition Phrases by Function

**Contrast**: "However,", "In contrast,", "Despite this,", "Nevertheless,"
**Addition**: "Furthermore,", "Moreover,", "In addition,", "Building on this,"
**Causation**: "As a result,", "Consequently,", "This leads to,"
**Concession**: "While X, Y", "Although X, we find Y", "Despite X, our results show"
**Emphasis**: "Notably,", "Importantly,", "Crucially,", "Of particular interest,"

### Citation Integration Patterns

```
# Inline attribution
Smith et al. [1] propose a method that...

# Parenthetical
...has been widely studied [1, 2, 3].

# Contrast setup
While prior work focuses on X [1, 2], we address Y.

# Building on
Following the approach of [1], we extend...

# Negative result framing
Although [1] achieves strong results on A, performance degrades on B.
```

---

## 5. Common Pitfalls & Mitigations

### Pitfall 1: AI Hallucinated Citations

**Problem**: LLMs confidently cite papers that don't exist or misattribute findings.

**Mitigation**:
- Never ask AI to suggest citations — provide your own
- If AI mentions a paper, verify on Semantic Scholar / Google Scholar before including
- Prompt: "Do not suggest any citations. I will provide all references."

### Pitfall 2: Inconsistent Terminology

**Problem**: AI uses "model", "network", "system", "approach" interchangeably across sections.

**Mitigation**:
- Define a terminology glossary before drafting:
  ```
  Terminology: always use "model" not "network".
  Our method is called "FlashLinear" (not "our approach" or "the system").
  ```
- Run a consistency pass prompt:
  ```
  Review this draft for terminology consistency.
  Flag any inconsistent use of: [term1, term2, term3].
  ```

### Pitfall 3: Generic / Vague Language

**Problem**: AI produces filler phrases: "In recent years...", "It is well known that...", "This is an important problem..."

**Mitigation**:
- Explicitly ban these in your prompt:
  ```
  Avoid: "In recent years", "It is well known", "This is an important/challenging problem",
  "state-of-the-art", "novel approach". Be specific instead.
  ```
- Replace with specific claims: "Since 2020, transformer models have grown from 175B to 1T parameters..."

### Pitfall 4: Overclaiming / Underclaiming

**Problem**: AI either oversells results ("our method is superior in all cases") or undersells them.

**Mitigation**:
- Provide exact numbers and let AI frame them
- Prompt: "State results precisely. Do not editorialize beyond what the numbers show."
- Review every superlative: "best", "first", "only", "always" — verify each one

### Pitfall 5: Passive Voice Overuse

**Problem**: AI defaults to passive voice, which obscures agency and weakens clarity.

**Mitigation**:
- Prompt: "Prefer active voice. Use 'we' as subject. Passive only when agent is unknown or unimportant."
- Post-draft check: search for "is/are/was/were + past participle" patterns

### Pitfall 6: Section Isolation (Incoherent Paper)

**Problem**: Each section drafted separately → paper reads as disconnected fragments.

**Mitigation**:
- Always include prior section summary in next section's prompt
- Final coherence pass:
  ```
  Read this full paper draft. Identify:
  (1) claims in intro not supported in experiments
  (2) methods described but not evaluated
  (3) inconsistent notation across sections
  (4) missing transitions between sections
  ```

### Pitfall 7: Ethical / Integrity Issues

**Problem**: Undisclosed AI use, AI-generated fabricated data descriptions, plagiarism.

**Mitigation**:
- Follow your target venue's AI disclosure policy (most top venues now require disclosure)
- AI writes prose, not data — never ask AI to "describe results" without providing actual results
- Run iThenticate before submission
- Keep all AI prompts and outputs for audit trail

---

## 6. Tool Ecosystem

### Literature Discovery & Synthesis

| Tool | Best For | Key Feature |
|------|----------|-------------|
| **Elicit** | Systematic literature review | Extracts claims from papers, builds evidence tables |
| **Semantic Scholar** | Citation graph, paper search | AI-powered relevance ranking, citation context |
| **Connected Papers** | Visual literature mapping | Graph of related papers by citation overlap |
| **ResearchRabbit** | Ongoing literature monitoring | Alerts for new related papers |
| **Consensus** | Quick evidence synthesis | "What does research say about X?" |

### Writing & Editing

| Tool | Best For | Key Feature |
|------|----------|-------------|
| **Writefull** | Academic phrasing, language polish | Trained on published papers, Overleaf integration |
| **Paperpal** | Journal-specific style | Checks against target journal conventions |
| **SciSpace** | Reading + writing in one place | Chat with PDFs, draft assistance |
| **Grammarly Academic** | Grammar, clarity, tone | Academic register detection |
| **QuillBot** | Paraphrasing, summarization | Useful for related work synthesis |

### LaTeX & Formatting

| Tool | Best For | Key Feature |
|------|----------|-------------|
| **Overleaf AI** | In-editor writing assistance | Context-aware suggestions in LaTeX |
| **LaTeX GPT** | LaTeX code generation | Equations, tables, figures from description |
| **Mathpix** | Equation OCR | Convert handwritten/image equations to LaTeX |

### Verification & Integrity

| Tool | Best For | Key Feature |
|------|----------|-------------|
| **iThenticate** | Plagiarism detection | Industry standard for journals |
| **GPTZero / Originality.ai** | AI content detection | Useful for self-audit before submission |
| **Semantic Scholar API** | Citation verification | Programmatic paper lookup |

### Recommended Stack by Use Case

**Solo researcher, fast drafting**: Claude/GPT-4 + Writefull + Semantic Scholar + Overleaf
**Systematic review paper**: Elicit + Connected Papers + Claude + Grammarly
**ML/CS conference paper**: Claude + LaTeX GPT + Mathpix + Overleaf AI
**Journal submission**: Paperpal + Writefull + iThenticate + Grammarly Academic

---

## 7. Section-Specific Strategies

### Abstract

**Goal**: Standalone summary that sells the paper in 150-250 words.

**Strategy**:
1. Write abstract LAST (after all sections are drafted)
2. Extract one sentence from each section: problem, gap, method, result, impact
3. Use AI to synthesize into flowing prose
4. Check: can a reader understand the contribution without reading the paper?

**Quality checklist**:
- [ ] States the problem specifically (not "an important problem")
- [ ] Identifies the gap in prior work
- [ ] Names your method/approach
- [ ] Includes at least one quantitative result
- [ ] States broader significance

### Introduction

**Goal**: Motivate the problem, establish the gap, state contributions clearly.

**Strategy**:
- Paragraph 1: Start with a concrete, specific observation — not a broad statement
- Paragraph 2: Survey the landscape of prior work (3-5 citations), identify the gap
- Paragraph 3: "In this paper, we..." — your approach and key insight
- Paragraph 4: Bulleted contributions (3-4 items, each falsifiable/verifiable)
- Final paragraph: Paper organization ("Section 2 reviews..., Section 3 presents...")

**AI tip**: Draft contributions list first, then ask AI to write backwards from it.

### Related Work

**Goal**: Position your work in the literature, not just summarize papers.

**Strategy**:
- Organize by theme/approach, not chronologically
- For each cluster: summarize → identify limitation → position your work
- End each subsection with a sentence connecting to your contribution
- Avoid: "Paper X does Y. Paper Z does W." (no synthesis)

**AI tip**: Provide a table of papers with columns [paper, method, limitation] and ask AI to synthesize into prose.

### Methodology

**Goal**: Enable reproducibility. A reader should be able to reimplement from this section.

**Strategy**:
- Start with problem formulation (math notation)
- Provide a figure/algorithm overview before details
- Each component: motivation → formulation → implementation detail
- End with complexity analysis and training procedure

**AI tip**: Write pseudocode first, then ask AI to convert to prose. Preserves precision.

### Experiments

**Goal**: Convince reviewers your claims are supported by evidence.

**Strategy**:
- Setup before results (datasets, baselines, metrics, hardware)
- Main table first, then ablations, then analysis
- Every claim in intro must have a corresponding experiment
- Ablations should isolate each contribution independently

**AI tip**: Provide the actual table data as text/CSV and ask AI to write the results narrative. Never ask AI to "describe results" without giving it the numbers.

### Conclusion

**Goal**: Synthesize, not repeat. Leave the reader with the "so what."

**Strategy**:
- 1 paragraph: what we did and what we found (compressed)
- 1 paragraph: what this enables / broader impact
- 1 paragraph: honest limitations + concrete future directions
- No new claims, no new citations

**AI tip**: Prompt AI to write conclusion from the abstract + contributions list. Ensures alignment.

---

## 8. Prompt Template Library

### Template 1: Section Draft from Bullet Points

```
You are an expert academic writer in [FIELD].
Target venue: [VENUE] (e.g., NeurIPS, ACL, Nature, CVPR)

Write the [SECTION] section of a research paper.

My structured notes:
[PASTE BULLET POINTS]

Requirements:
- Length: ~[N] words
- Tense: [TENSE]
- Tone: formal, precise, [confident/hedged as appropriate]
- Do NOT suggest citations — I will add them manually
- Avoid: "In recent years", "It is well known", "state-of-the-art"
- Use active voice with "we" as subject

Output: prose only, no headers unless I specify.
```

### Template 2: Revision / Improvement Pass

```
Revise the following [SECTION] excerpt for a [VENUE] paper.

Issues to fix:
- [ISSUE 1, e.g., "too vague in paragraph 2"]
- [ISSUE 2, e.g., "passive voice throughout"]
- [ISSUE 3, e.g., "missing transition to next section"]

Preserve:
- All technical claims and numbers
- Citation markers [1], [2], etc.
- Section structure

Original text:
[PASTE TEXT]

Return: revised text only.
```

### Template 3: Terminology Consistency Check

```
Review the following paper draft for terminology consistency.

Defined terms (always use these exact forms):
- Method name: [NAME]
- Key concept 1: [TERM] (not [VARIANT1] or [VARIANT2])
- Key concept 2: [TERM]

Flag every inconsistency with: [LINE QUOTE] → should be [CORRECT TERM]
Do not rewrite — only flag issues.

Draft:
[PASTE DRAFT]
```

### Template 4: Reviewer Response Drafting

```
Help me draft a response to this reviewer comment for a [VENUE] rebuttal.

Reviewer comment:
"[PASTE COMMENT]"

My response strategy:
- [AGREE/DISAGREE/PARTIALLY AGREE]
- Evidence: [what I can point to in the paper or new experiments]
- Action: [what I will add/change in revision]

Write a professional, concise rebuttal (~100-150 words).
Tone: respectful, direct, evidence-based. Not defensive.
```

### Template 5: Abstract Synthesis

```
Write a structured abstract (~200 words) synthesizing these section summaries.

Problem (from intro): [1-2 sentences]
Gap (from related work): [1 sentence]
Method (from methodology): [2-3 sentences]
Results (from experiments): [key numbers: metric=X, baseline=Y]
Impact (from conclusion): [1 sentence]

Format: single paragraph, no subheadings.
Tense: present for claims, past for experiments.
Must include: at least one quantitative result.
Avoid: "In this paper", "We propose a novel", vague impact statements.
```

### Template 6: Related Work Synthesis from Paper List

```
Write a related work subsection on [TOPIC] (~200 words).

Papers to cover (I provide summaries — do not invent details):
1. [Author Year]: [method] — limitation: [limitation]
2. [Author Year]: [method] — limitation: [limitation]
3. [Author Year]: [method] — limitation: [limitation]

Our work addresses these limitations by: [YOUR APPROACH]

Structure:
- Sentence 1-2: introduce the line of work
- Sentences 3-5: cover each paper, noting limitations
- Final sentence: position our work

Do not use "et al." — I will add proper citations manually.
```

### Template 7: Figure Caption Writing

```
Write a caption for Figure [N] in a [VENUE] paper.

Figure description: [describe what the figure shows]
Key takeaway: [what the reader should conclude from this figure]
Reference in text: this figure is discussed in Section [N] where we claim [CLAIM]

Caption format:
- First sentence: what the figure shows (factual)
- Second sentence: key observation or takeaway
- Length: 2-3 sentences, ~50-80 words
```

---

## Quick Reference: Do's and Don'ts

| Do | Don't |
|----|-------|
| Provide structured notes as input | Ask AI to write from scratch with no context |
| Verify every AI-suggested citation | Trust AI citation suggestions |
| Give AI your actual numbers | Ask AI to "describe results" without data |
| Define terminology before drafting | Let AI choose your technical vocabulary |
| Use AI for prose, own the ideas | Let AI determine your contributions |
| Disclose AI use per venue policy | Submit without checking venue AI policy |
| Run plagiarism check before submission | Skip integrity verification |
| Keep prompts and outputs for audit | Delete your AI interaction history |

---

## Venue-Specific Notes

### ML/CS Conferences (NeurIPS, ICML, ICLR, CVPR, ACL)
- Double-blind: remove identifying info from AI prompts too
- Reproducibility statements now required at most venues
- Broader impact / ethics sections: write yourself, AI tends to be generic here
- Appendix: AI can help draft, but main paper claims must be self-contained

### Nature / Science / Cell (High-Impact Journals)
- Extremely high bar for novelty claims — hedge carefully
- Methods section must be exhaustively detailed
- Supplementary materials: AI very useful here
- Cover letter: AI can draft, but personalize heavily

### Domain Journals (IEEE, ACM, Elsevier, Springer)
- Check journal-specific AI policy (varies widely as of 2026)
- Paperpal has journal-specific style profiles
- Word limits are strict — use AI for compression passes

---

*This document is a living reference. Update prompt templates based on what works for your specific field and writing style.*

