---
name: investment-clock-analyze
description: Analyze a Gemini Deep Research paper + FRED quantitative data to produce a final Investment Clock evaluation and save it to the database.
argument-hint: <path/to/gemini-paper.md>
allowed-tools: [Bash, Read]
---

# Investment Clock Analyze

The user invoked this with: $ARGUMENTS

Analyze a Gemini Deep Research paper combined with live FRED quantitative data to produce a structured Investment Clock evaluation and persist it to the database.

## Usage

```
/investment-clock-analyze <path/to/gemini-paper.md>
```

Example:
```
/investment-clock-analyze C:\Users\lswht\Downloads\gemini-investment-clock-research.md
```

## What this skill does

1. Reads the Gemini research paper from the provided file path
2. Queries `investment_clock_data` for the latest data point + 24-month history
3. Queries `investment_clock_evaluation` for the last 3 prior evaluations (for continuity)
4. Claude synthesizes all inputs and produces a structured evaluation
5. Upserts the result into `investment_clock_evaluation`
6. Prints a summary

## Instructions for Claude

When this skill is invoked with a file path argument:

### Step 1: Read the Gemini paper
Use the Read tool to read the full content of the file at the provided path.
If the file does not exist, tell the user and stop.

### Step 2: Query the database
Run these queries via the Bash tool using psql:

```sql
-- Latest data point
SELECT
  TO_CHAR(biz_date, 'YYYY-MM-DD') as biz_date,
  ROUND(growth_z_score::numeric, 4) as growth_z,
  ROUND(inflation_z_score::numeric, 4) as inflation_z,
  data_phase,
  ROUND(clock_angle::numeric, 2) as clock_angle,
  ROUND(gdp_value::numeric, 2) as gdp,
  ROUND(cpi_value::numeric, 2) as cpi,
  ROUND(tcu_value::numeric, 1) as tcu,
  ROUND(unrate_value::numeric, 1) as unrate,
  ROUND(indpro_value::numeric, 2) as indpro,
  ROUND(cli_value::numeric, 2) as cli,
  ROUND(icsa_value::numeric, 0) as icsa,
  ROUND(cpi_yoy::numeric, 2) as cpi_yoy,
  ROUND(cpi_mom_ann::numeric, 2) as cpi_mom_ann,
  ROUND(t5yie_value::numeric, 2) as t5yie,
  ROUND(ppi_yoy::numeric, 2) as ppi_yoy
FROM investment_clock_data
ORDER BY biz_date DESC LIMIT 1;

-- 24-month trajectory
SELECT
  TO_CHAR(biz_date, 'YYYY-MM') as month,
  ROUND(growth_z_score::numeric, 3) as growth_z,
  ROUND(inflation_z_score::numeric, 3) as inflation_z,
  data_phase
FROM investment_clock_data
WHERE biz_date >= CURRENT_DATE - INTERVAL '24 months'
ORDER BY biz_date ASC;

-- Last 3 evaluations for continuity
SELECT
  TO_CHAR(biz_date, 'YYYY-MM-DD') as biz_date,
  final_phase,
  ROUND(phase_confidence::numeric, 1) as confidence,
  phase_direction,
  LEFT(reasoning, 400) as reasoning_preview,
  LEFT(outlook, 200) as outlook_preview
FROM investment_clock_evaluation
ORDER BY biz_date DESC LIMIT 3;
```

### Step 3: Synthesize and evaluate

With all three inputs (Gemini paper + quantitative data + prior evaluations), reason through:

1. **What does the quantitative data say?** (Z-scores, phase, 24-month trajectory)
2. **What does the Gemini research paper say?** (Extract key conclusions, phase assessment, risks, recommendations)
3. **What do prior evaluations say?** (Identify continuity, direction, any phase transitions)
4. **Resolve any conflicts** between quantitative signals and qualitative research

Then produce a final structured evaluation. Extract all fields carefully from the research paper where explicitly stated.

**Writing style rules — strictly enforced:**
- `reasoning`: exactly 3–4 bullet strings separated by `\n`. Each bullet ≤ 20 words. Start each with `•`. One bullet = one concrete reason for the phase call (Z-score signal, trajectory, macro catalyst, prior eval continuity). No prose, no paragraphs.
- `outlook`: exactly 2–3 bullet strings separated by `\n`. Each bullet ≤ 15 words. Start each with `•`. Cover: (1) most likely path, (2) key risk caveat, (3) one watchlist catalyst.
- `gemini_research_summary`: 1–2 sentences max. State the single most important finding from the research that influenced the phase call. No generic summaries.
- `key_indicators`: 3–5 items. Each ≤ 15 words. Lead with the metric name and value, then the signal meaning.
- `risks`: 2–3 items. Each ≤ 12 words. Start with the risk driver noun.

```json
{
  "final_phase": "Recovery" | "Overheat" | "Stagflation" | "Reflation",
  "phase_confidence": 0-100,
  "phase_direction": "clockwise" | "counterclockwise" | "stable",
  "reasoning": "• Bullet one reason ≤20 words\n• Bullet two reason ≤20 words\n• Bullet three reason ≤20 words",
  "outlook": "• Most likely path ≤15 words\n• Key risk caveat ≤15 words\n• Watchlist catalyst ≤15 words",
  "key_indicators": ["Metric Name X.xx — signal meaning ≤15 words", "..."],
  "risks": ["Risk driver — brief consequence ≤12 words", "..."],
  "best_asset": "Government Bonds" | "Equities" | "Commodities" | "Cash",
  "recommended_sectors": ["ETF1 (Sector)", "ETF2 (Sector)", "ETF3 (Sector)"],
  "gemini_research_summary": "1-2 sentences: the one finding that most influenced the phase call.",
  "phase_probabilities": [
    {"phase": "Recovery", "probability": 70},
    {"phase": "Reflation", "probability": 20},
    {"phase": "Stagflation", "probability": 10}
  ],
  "monitoring_triggers": [
    {"indicator": "ISM Manufacturing Employment", "threshold": "> 50", "meaning": "Signals durable industrial recovery"},
    {"indicator": "5-Year Breakeven Inflation", "threshold": "< 2.75%", "meaning": "Preserves Fed latitude for rate cut"},
    {"indicator": "10-Year Treasury Yield", "threshold": "< 4.75%", "meaning": "Confirms crowding-out risk is contained"}
  ],
  "sector_rationale": [
    {"etf": "IYF", "rationale": "Specific reason from research why this ETF is recommended"},
    {"etf": "IYC", "rationale": "Specific reason from research why this ETF is recommended"},
    {"etf": "IYH", "rationale": "Specific reason from research why this ETF is recommended"}
  ]
}
```

**Notes for `phase_probabilities`**: Extract explicit probabilities from the research paper's outlook section if stated (e.g., "70% Recovery, 20% Reflation stall, 10% Stagflation"). If not stated, estimate based on the confidence and direction.

**Notes for `monitoring_triggers`**: Extract the specific leading indicators and thresholds the research identifies as signals to watch for a phase transition. Always include 2-4 triggers.

**Notes for `sector_rationale`**: For each recommended ETF, write 1-2 sentence rationale grounded in the specific research (e.g., yield curve mechanics, fiscal catalyst, defensive positioning). Use the ETF ticker as the key.

Phase → Asset mapping for reference:
- Reflation   → Government Bonds  | Financials (IYF), Consumer Staples (IYK), Consumer Discretionary (IYC)
- Recovery    → Equities          | Technology (IYW), Telecom (IYZ), Materials (IYM)
- Overheat    → Commodities       | Energy (IYE), Industrials (IYJ), Materials (IYM)
- Stagflation → Cash              | Utilities (IDU), Healthcare (IYH), Consumer Staples (IYK)

### Step 4: Save to database

Use the Python snippet below (via Bash tool) to upsert all fields including the three new enrichment columns:

```python
import sys, json, pathlib
ROOT = pathlib.Path('F:/workspace/sophie-pipeline')
sys.path.insert(0, str(ROOT))
from src.tools.api_db import get_db_connection

evaluation = { ... }  # fill in from Step 3

conn = get_db_connection()
cur = conn.cursor()
cur.execute("""
  INSERT INTO investment_clock_evaluation (
    biz_date,
    final_phase, phase_confidence, phase_direction,
    reasoning, outlook,
    key_indicators, risks,
    best_asset, recommended_sectors,
    gemini_research_summary,
    phase_probabilities, monitoring_triggers, sector_rationale
  ) VALUES (
    CURRENT_DATE,
    %(final_phase)s, %(phase_confidence)s, %(phase_direction)s,
    %(reasoning)s,   %(outlook)s,
    %(key_indicators)s::jsonb, %(risks)s::jsonb,
    %(best_asset)s, %(recommended_sectors)s::jsonb,
    %(gemini_research_summary)s,
    %(phase_probabilities)s::jsonb, %(monitoring_triggers)s::jsonb, %(sector_rationale)s::jsonb
  )
  ON CONFLICT (biz_date) DO UPDATE SET
    final_phase             = EXCLUDED.final_phase,
    phase_confidence        = EXCLUDED.phase_confidence,
    phase_direction         = EXCLUDED.phase_direction,
    reasoning               = EXCLUDED.reasoning,
    outlook                 = EXCLUDED.outlook,
    key_indicators          = EXCLUDED.key_indicators,
    risks                   = EXCLUDED.risks,
    best_asset              = EXCLUDED.best_asset,
    recommended_sectors     = EXCLUDED.recommended_sectors,
    gemini_research_summary = EXCLUDED.gemini_research_summary,
    phase_probabilities     = EXCLUDED.phase_probabilities,
    monitoring_triggers     = EXCLUDED.monitoring_triggers,
    sector_rationale        = EXCLUDED.sector_rationale
""", {
  **{k: v for k, v in evaluation.items() if k not in ('key_indicators','risks','recommended_sectors','phase_probabilities','monitoring_triggers','sector_rationale')},
  'key_indicators':      json.dumps(evaluation['key_indicators']),
  'risks':               json.dumps(evaluation['risks']),
  'recommended_sectors': json.dumps(evaluation['recommended_sectors']),
  'phase_probabilities': json.dumps(evaluation['phase_probabilities']),
  'monitoring_triggers': json.dumps(evaluation['monitoring_triggers']),
  'sector_rationale':    json.dumps(evaluation['sector_rationale']),
})
conn.commit()
print('Saved.')
cur.close(); conn.close()
```

### Step 5: Print summary

After saving, print a formatted summary:

```
=== Investment Clock Evaluation Saved ===
Date:        [biz_date]
Final Phase: [final_phase]
Confidence:  [phase_confidence]%
Direction:   [phase_direction]
Best Asset:  [best_asset]
Sectors:     [recommended_sectors joined by ", "]

Phase Transition Probabilities:
  [phase]: [probability]%  (for each)

Key Indicators:
  • [indicator 1]
  • [indicator 2]
  • ...

Risks:
  • [risk 1]
  • [risk 2]

Monitoring Triggers:
  [threshold] [indicator] — [meaning]

Outlook:
  [outlook text]

Gemini Research Summary:
  [gemini_research_summary]
```
