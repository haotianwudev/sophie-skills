---
name: sophie-brainstorm
description: Brainstorm new article, video, or content ideas for Sophie Daddy's finance channel, based on existing article history and content gaps.
argument-hint: [topic or category hint - optional]
allowed-tools: [Read, WebSearch]
---

# Sophie Brainstorm Skill

Generate timely content ideas for Sophie Daddy's finance platform. Target: **complete in under 2 minutes**.

## Arguments

The user invoked this with: $ARGUMENTS

---

## Step 1 — Load blocklist + read recent articles (fast scan)

**First**, read the blocklist of already-suggested ideas — do NOT repeat any topic listed here:
```
C:/Users/lswht/.claude/skills/sophie-brainstorm/suggested.md
```

**Then**, read the two most recent quarter files:

Read ONLY the two most recent quarter files (titles + labels, skip descriptions):

```
F:/workspace/ai-stock-suggestion-client/src/data/articles/2026-q2.ts
F:/workspace/ai-stock-suggestion-client/src/data/articles/2026-q1.ts
```

Do NOT read older quarters or types.ts — use this known label taxonomy:
`QUANT` · `AI_ML` · `OPTIONS` · `STOCK_ANALYSIS` · `MARCO` · `FINANCE101` · `CRYPTO` · `FORM13F` · `BOOK`

Known permanent gaps (never write articles on these): `FORM13F` = 0, `BOOK` = 0, `CRYPTO` = 1 old piece, `STOCK_ANALYSIS` = sparse, `MARCO` = sparse.

---

## Step 2 — Run 2 parallel trend searches

Run these **simultaneously** (do not wait for one before starting the other):

**Search A — arXiv q-fin hot papers:**
> `arxiv q-fin quantitative finance trending papers 2026`

**Search B — community + YouTube buzz:**
> `quant finance algotrading trending topics reddit youtube april 2026`

Extract the top 3–5 signals from both searches combined. Flag these `🔥 Trending`.

---

## Step 3 — Generate exactly 5 ideas

Pick the 5 highest-impact ideas that combine:
- A gap in existing coverage (from Step 1)
- A trend signal (from Step 2)

If $ARGUMENTS specifies a topic, all 5 ideas must be on that topic.

For each idea:

### [Title]
- **Label(s):** [labels]
- **Format:** Article / Video / Both
- **🔥 Trend signal:** [what search result or community buzz backs this — or "gap fill" if no trend]
- **Angle:** One sentence on what makes this unique vs generic finance content

---

## Step 4 — Research question series (5 questions per idea)

For each of the 5 ideas, output 5 sequential LLM questions that scaffold a full article. Keep questions concise but self-contained.

#### Research Questions: [Title]
1. **[Foundation]** ...
2. **[Mechanics + Math]** ...
3. **[Strategy / Application]** ...
4. **[Risks & Pitfalls]** ...
5. **[Synthesis]** Give me a 150-word executive summary of [TOPIC] and a 5-item actionable checklist for retail investors.

---

## Step 5 — Append to blocklist

After outputting all ideas, append today's 5 suggestions to the blocklist file:
```
C:/Users/lswht/.claude/skills/sophie-brainstorm/suggested.md
```

Format:
```
## YYYY-MM-DD

- [Title] — [labels]
- [Title] — [labels]
...
```

---

## Platform Context

- **Audience:** Quantitatively-minded retail investors, finance professionals, algo traders
- **Tone:** Rigorous, technical, educational — not clickbait
- **Format mix:** Deep research articles (primary) + YouTube companion videos
