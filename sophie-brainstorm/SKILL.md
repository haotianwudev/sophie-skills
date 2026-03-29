---
name: sophie-brainstorm
description: Brainstorm new article, video, or content ideas for Sophie Daddy's finance channel, based on existing article history and content gaps.
argument-hint: [topic or category hint - optional]
allowed-tools: [Bash, Read, Glob]
---

# Sophie Brainstorm Skill

Generate new content ideas for Sophie Daddy's finance platform by analyzing existing articles and identifying gaps, trends, and opportunities.

## Arguments

The user invoked this with: $ARGUMENTS

---

## Step 1 — Read existing articles

Read all quarter files to understand what's already been covered:

```
F:/workspace/ai-stock-suggestion-client/src/data/articles/2026-q2.ts
F:/workspace/ai-stock-suggestion-client/src/data/articles/2026-q1.ts
F:/workspace/ai-stock-suggestion-client/src/data/articles/2025-q4.ts
F:/workspace/ai-stock-suggestion-client/src/data/articles/2025-q3.ts
F:/workspace/ai-stock-suggestion-client/src/data/articles/2025-q2.ts
```

Also read types to understand the label taxonomy:
```
F:/workspace/ai-stock-suggestion-client/src/data/articles/types.ts
```

---

## Step 2 — Analyze coverage

Build a mental map of:
- Which **labels/categories** are well-covered vs underrepresented
- Which **series** are in progress (e.g. volatility surface, options strategies, factor models)
- Which **formats** are missing (article vs video vs podcast balance)
- What was covered **most recently** (to suggest natural follow-ups)

---

## Step 3 — Generate ideas

If $ARGUMENTS specifies a topic or category, focus ideas there. Otherwise generate a broad set across all labels.

For each idea, output in this format:

### [Title Idea]
- **Label(s):** `QUANT` / `AI_ML` / `OPTIONS` / `STOCK_ANALYSIS` / `MARCO` / `FINANCE101` / `CRYPTO` / `FORM13F` / `BOOK`
- **Format:** Deep Research Article / YouTube Video / Both (article + video)
- **Why now:** Why this topic fits the current content mix or fills a gap
- **Angle:** What makes this treatment unique vs generic finance content
- **Connects to:** Existing articles it pairs with or extends

---

## Step 4 — Output structure

Group ideas by label. Aim for 3-5 ideas per active category. Highlight the top 3 highest-impact picks at the end with a brief rationale.

If the user gave a specific topic hint in $ARGUMENTS, lead with 5+ ideas on that topic before the broader list.

---

## Step 5 — Deep Research Plan (when topic is clear)

If $ARGUMENTS contains a **specific, clear topic** (not just a vague category), also generate a **Gemini Deep Research prompt** after the brainstorm ideas.

A clear topic example: "quant strategies bull to bear transition", "options skew trading", "private credit BDCs"
A vague topic: "options" or "macro" alone — skip this step and just brainstorm.

### Deep Research Prompt format:

Output a ready-to-paste Gemini Deep Research prompt under this heading:

---
## Gemini Deep Research Prompt

> *"[The full prompt — 200-400 words. Structure it as:]
>
> Conduct a deep research analysis of [TOPIC]. Target audience: quantitatively-minded investors and finance professionals.
>
> Cover the following areas:
> 1. [Core concept / theoretical foundation]
> 2. [Mechanics / how it works in practice]
> 3. [Quantitative frameworks / models]
> 4. [Strategy applications / trading implementation]
> 5. [Risk management and common pitfalls]
> 6. [Historical case studies or empirical evidence]
> 7. [Connections to related strategies or factors — especially those covered in Sophie Daddy's existing content: [list 2-3 relevant existing articles]]
>
> Include specific metrics, formulas, and practitioner frameworks where relevant. Cite academic research and real-world examples. Output should be comprehensive enough to form the basis of a 3,000-5,000 word deep research article."*

---

Then provide **3 variations** of the prompt with different angles:
- **Variation A — Broad:** Full coverage for a flagship deep research article
- **Variation B — Technical:** Math-heavy, quant-focused, for premium/advanced readers
- **Variation C — Practical:** Strategy-focused, actionable, for traders wanting to implement

---

## Platform Context

- **Site:** Sophie Daddy's AI-powered finance platform (ai-stock-suggestion-client)
- **Audience:** Quantitatively-minded retail investors, finance professionals, and algo traders
- **Tone:** Rigorous, technical, educational — not clickbait
- **Content mix:** Deep research articles (primary), YouTube videos (companion), podcasts (Spotify)
- **Labels available:**
  - `QUANT` — Quantitative Finance (factor models, vol surface, derivatives math)
  - `AI_ML` — AI & Machine Learning in finance
  - `OPTIONS` — Options trading strategies and mechanics
  - `STOCK_ANALYSIS` — Fundamental valuation, stock picks
  - `MARCO` — Macro economics and market outlooks
  - `FINANCE101` — Accessible educational content
  - `CRYPTO` — Crypto / DeFi / Web3
  - `FORM13F` — Institutional 13F filings and flow analysis
  - `BOOK` — Book summaries and reviews
- **Flags:** `deepResearch`, `isVideo`, `options`, `premiumContent`, `podcastUrl`
