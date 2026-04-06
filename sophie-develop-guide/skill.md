---
name: sophie-develop-guide
description: Architecture reference for the Sophie finance platform. Read this before building any new feature — ETL pipeline, GraphQL server, and Next.js frontend patterns with real Investment Clock examples.
argument-hint: [optional: feature name to focus on]
allowed-tools: [Read, Bash, Glob, Grep]
---

# Sophie Platform — Development Guide

The user invoked this with: $ARGUMENTS

Read this guide to understand the Sophie platform architecture before building or extending any feature.
If a specific feature was requested in $ARGUMENTS, focus on that context; otherwise give a full overview.

---

## Platform Overview

Sophie is a personal finance / investment analysis platform with three repos:

| Layer | Repo | Purpose |
|-------|------|---------|
| ETL pipeline | `F:/workspace/sophie-pipeline` | Fetch external data (FRED, etc.), compute signals, upsert to PostgreSQL |
| GraphQL API | `F:/workspace/ai-stock-suggestion-server` | Apollo Server — exposes data to frontend |
| Frontend | `F:/workspace/ai-stock-suggestion-client` | Next.js 14 app (App Router), Apollo Client, Tailwind + shadcn/ui |
| Skills | `/c/Users/lswht/.claude/skills/` | Claude Code slash-command skills for recurring workflows |

Database: PostgreSQL (accessed via psycopg2 in Python, `pg` pool in Node).

---

## Standard Feature Pattern

Every new feature follows this exact layered pattern. **Investment Clock** is the canonical example — reference it when building anything new.

### 1. ETL Agent (Python)

**Location:** `F:/workspace/sophie-pipeline/src/agents/<feature>.py`
**Example:** `investment_clock.py`

Responsibilities:
- Fetch external data (FRED API, scraping, etc.)
- Resample/normalize to monthly if needed
- Compute signals (Z-scores, ratios, etc.)
- Upsert rows to a PostgreSQL table using `ON CONFLICT (biz_date) DO UPDATE SET ...`

Key patterns:
```python
# DB connection — always use the shared helper
import sys, pathlib
ROOT = pathlib.Path(__file__).parent.parent.parent  # sophie-pipeline root
sys.path.insert(0, str(ROOT))
from src.tools.api_db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("INSERT INTO ... ON CONFLICT (biz_date) DO UPDATE SET ...")
conn.commit()
cursor.close(); conn.close()
```

EWM Z-score pattern (use for any time-series normalization):
```python
def ewm_z_score(series, span=24, min_periods=12):
    ewm_mean = series.ewm(span=span, min_periods=min_periods, ignore_na=True).mean()
    ewm_std  = series.ewm(span=span, min_periods=min_periods, ignore_na=True).std()
    z = (series - ewm_mean) / ewm_std.replace(0, float('nan'))
    return z.ffill().fillna(0)
```

**Runner script:** `F:/workspace/sophie-pipeline/<feature>/run.py`
- Entry point that calls `run_etl()` plus any prompt/report generation
- Run with: `cd F:/workspace/sophie-pipeline && poetry run python <feature>/run.py`

### 2. PostgreSQL Tables

Two-table pattern for features with AI evaluation:
- `<feature>_data` — raw/computed time series, upserted weekly by ETL
- `<feature>_evaluation` — AI-generated analysis, upserted after Claude/Gemini analysis

Both use `biz_date DATE PRIMARY KEY` (or UNIQUE) for upsert.

SQL files live in: `F:/workspace/sophie-pipeline/sql/`

### 3. GraphQL Schema

**Location:** `F:/workspace/ai-stock-suggestion-server/src/schema/<feature>.js`
**Example:** `investment-clock.js`

Pattern:
```js
const { gql } = require('apollo-server');
const schema = gql`
  type FeatureDataPoint { bizDate: String! ... }
  type FeatureEvaluation { bizDate: String! ... }
  type FeatureResult {
    current: FeatureEvaluation
    latestData: FeatureDataPoint
    history: [FeatureDataPoint!]!
  }
  extend type Query {
    featureName: FeatureResult!
  }
`;
module.exports = schema;
```

Register in `F:/workspace/ai-stock-suggestion-server/src/schema/index.js`.

### 4. GraphQL Resolver

**Location:** `F:/workspace/ai-stock-suggestion-server/src/resolvers/<feature>.js`
**Example:** `investment-clock.js`

Pattern:
```js
const { getLatestEvaluation, getLatestData, getHistoricalData } = require('../db/<feature>');
const resolvers = {
  Query: {
    featureName: async () => {
      const [current, latestData, history] = await Promise.all([
        getLatestEvaluation(), getLatestData(), getHistoricalData(24),
      ]);
      // JSONB columns from pg come back as JS objects — convert for GraphQL:
      if (current) {
        current.someArray = Array.isArray(current.someArray) ? current.someArray : [];
      }
      return { current, latestData, history };
    },
  },
};
module.exports = resolvers;
```

Register in `F:/workspace/ai-stock-suggestion-server/src/resolvers/index.js`.

### 5. DB Query Layer

**Location:** `F:/workspace/ai-stock-suggestion-server/src/db/<feature>.js`
**Example:** `investment-clock.js`

Key patterns:
- Always alias snake_case columns to camelCase: `biz_date AS "bizDate"`
- Use `CAST(col AS FLOAT)` for numeric columns — pg returns strings otherwise
- Use `LAG()` window function for YoY deltas in the same query
- JSONB columns (arrays/objects) come back as JS objects automatically from `pg`

```js
const db = require('../db');  // shared pg pool

async function getLatestData() {
  const result = await db.query(`SELECT ... FROM <feature>_data ORDER BY biz_date DESC LIMIT 1`);
  return result.rows[0] || null;
}

async function getHistoricalData(months = 24) {
  const result = await db.query(
    `SELECT ... FROM <feature>_data WHERE biz_date >= CURRENT_DATE - ($1 || ' months')::INTERVAL ORDER BY biz_date ASC`,
    [months]
  );
  return result.rows;
}
```

### 6. Frontend Page

**Location:** `F:/workspace/ai-stock-suggestion-client/src/app/<feature>/`
**Example:** `investment-clock/page.tsx` + `investment-clock-client.tsx`

Two-file pattern (Next.js App Router):

`page.tsx` — server component, metadata only:
```tsx
import { Metadata } from "next";
import { Header } from "@/components/layout/header";
import { Disclaimer } from "@/components/ui/disclaimer";
import { FeatureClient } from "./feature-client";

export const metadata: Metadata = { title: "...", description: "..." };

export default function FeaturePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto max-w-5xl px-4 py-8">
          <FeatureClient />
        </div>
      </main>
      <Disclaimer />
    </div>
  );
}
```

`feature-client.tsx` — "use client", Apollo useQuery, all UI logic:
```tsx
"use client";
import { useQuery } from "@apollo/client";
import { GET_FEATURE } from "@/lib/graphql/queries";

export function FeatureClient() {
  const { data, loading } = useQuery(GET_FEATURE, { fetchPolicy: "cache-and-network" });
  if (loading && !data) return <LoadingSkeleton />;
  const result = data?.featureName;
  // render...
}
```

Add GraphQL query to: `F:/workspace/ai-stock-suggestion-client/src/lib/graphql/queries.ts`
Add TypeScript types to: `F:/workspace/ai-stock-suggestion-client/src/lib/graphql/types.ts`

### 7. Reusable UI Components

Located in `F:/workspace/ai-stock-suggestion-client/src/components/`:
- `layout/header.tsx` — site header (always include)
- `ui/disclaimer.tsx` — legal disclaimer (always include on finance pages)
- `ui/card.tsx`, `ui/badge.tsx` — shadcn/ui primitives
- `ui/video-tutorial.tsx` — YouTube embed card
- `articles/article-card.tsx` — related article card

For feature-specific components, create a subfolder:
`src/components/<feature>/` (e.g., `investment-clock/clock-face.tsx`)

---

## Investment Clock — Concrete File Map

Use this as the reference when building a new feature:

```
ETL:
  F:/workspace/sophie-pipeline/src/agents/investment_clock.py   ← FRED fetch + EWM Z-score + upsert
  F:/workspace/sophie-pipeline/investment-clock/run.py           ← runner (ETL + prompt generation)
  F:/workspace/sophie-pipeline/investment-clock/generate_prompt.py ← Gemini Deep Research prompt builder

GraphQL Server:
  F:/workspace/ai-stock-suggestion-server/src/schema/investment-clock.js    ← type defs
  F:/workspace/ai-stock-suggestion-server/src/resolvers/investment-clock.js ← resolver
  F:/workspace/ai-stock-suggestion-server/src/db/investment-clock.js        ← SQL queries

Frontend:
  F:/workspace/ai-stock-suggestion-client/src/app/investment-clock/page.tsx               ← server component
  F:/workspace/ai-stock-suggestion-client/src/app/investment-clock/investment-clock-client.tsx ← client component
  F:/workspace/ai-stock-suggestion-client/src/components/investment-clock/               ← feature components

AI Analysis Skills:
  /c/Users/lswht/.claude/skills/investment-clock-prompt/skill.md  ← generate Gemini research prompt
  /c/Users/lswht/.claude/skills/investment-clock-analyze/skill.md ← analyze Gemini result + save to DB
```

DB tables:
- `investment_clock_data` — monthly FRED signals + Z-scores (ETL-managed)
- `investment_clock_evaluation` — AI phase evaluation with JSONB fields (Claude-managed)

---

## Workflow for a New Feature

1. **Design the DB schema** — two tables: `<feature>_data` + `<feature>_evaluation`
2. **Write the ETL agent** in `sophie-pipeline/src/agents/<feature>.py`
3. **Write the runner** in `sophie-pipeline/<feature>/run.py`
4. **Add GraphQL schema** in `server/src/schema/<feature>.js`, register in `schema/index.js`
5. **Add DB queries** in `server/src/db/<feature>.js`
6. **Add resolver** in `server/src/resolvers/<feature>.js`, register in `resolvers/index.js`
7. **Add GraphQL query + types** in `client/src/lib/graphql/`
8. **Create frontend page** under `client/src/app/<feature>/`
9. **Create skills** if there's a recurring Claude workflow (prompt → analyze → save)

---

## Key Environment / Config

- FRED API key: `FRED_API_KEY` env var in sophie-pipeline
- DB connection: `DATABASE_URL` env var (or `DB_USER/DB_PASSWORD/DB_HOST/DB_NAME`)
- sophie-pipeline uses Poetry: `poetry run python ...`
- GraphQL server: Apollo Server (Node), `npm run dev` or `node src/index.js`
- Frontend: Next.js, `npm run dev`
