---
name: sophie-option-strategy
description: Add a new option strategy or update an existing one in the Sophie platform's Strategy Explorer.
triggers:
  - /sophie-option-strategy
---

# Sophie Option Strategy Skill

Add a new option strategy page or modify an existing one in the Strategy Explorer.

## Permissions

Read `C:/Users/lswht/.claude/settings.json` and confirm `"permissions": { "defaultMode": "bypassPermissions" }` is set before proceeding.

## Input (ask if not provided)

- **Action**: `add` (new strategy) or `update` (existing strategy)
- **Strategy name** — e.g., `Seagull Spread`
- For `update`: which fields to change (config fields, detail component sections, or both)

---

## File Map

All three files must be kept in sync:

| File | Purpose |
|---|---|
| `F:/workspace/ai-stock-suggestion-client/src/components/options/strategy-config.ts` | Central config: strategy data, payoff calc, component reference |
| `F:/workspace/ai-stock-suggestion-client/src/components/options/strategies/{name}.tsx` | Detail component: educational content sections |
| `F:/workspace/ai-stock-suggestion-client/src/app/option/strategies/[[...slug]]/page.tsx` | Route metadata: name + description for SEO |

---

## Step 1 — Gather Strategy Information

Ask the user for all required fields (or infer from context if obvious):

### Config fields (strategy-config.ts)

| Field | Type | Notes |
|---|---|---|
| `id` | string | snake_case, unique. e.g. `seagull_spread` |
| `name` | string | Display name. e.g. `Seagull Spread` |
| `category` | `StrategyCategory[]` | Pick from: `Bullish`, `Bearish`, `Neutral`, `Volatility`, `Income`, `Featured`, `Risk Defined` |
| `description` | string | 1-2 sentences for strategy cards |
| `profile` | string | e.g. `Defined Risk, Defined Profit` |
| `volatility` | string | e.g. `Benefits from falling IV (Short Vega)` |
| `time` | string | e.g. `Benefits from time decay (Long Theta)` |
| `payoffCalculator` | function | `(p, { strike1, strike2, strike3, strike4, premium }) => number` |
| `youtubeId?` | string | YouTube video ID (not full URL) |
| `payoffExplanation?` | string | One sentence describing the payoff diagram |
| `relatedArticles?` | string[] | Article slugs from the articles data files |
| `infographicUrl?` | string | Imgur URL for strategy infographic |

### Route metadata (page.tsx)
| Field | Notes |
|---|---|
| `slug` | kebab-case ID, e.g. `seagull-spread` |
| `name` | Same as config name |
| `description` | 1 sentence for SEO |

### Detail component content
Ask the user what educational content to include, or generate it from the strategy name/description if adding a new strategy. See Section 4 for required sections.

---

## Step 2 — For `update`: Read Existing Files First

Read the three files to understand current state before making changes:

```
strategy-config.ts    — find the strategy's entry in the strategies array
{name}.tsx            — read the full detail component
page.tsx              — find the metadata entry
```

Show the user what currently exists and what will change.

---

## Step 3 — Show Preview and Confirm

**For `add`**, show the full new strategy config entry and outline the detail component sections.

**For `update`**, show a diff-style preview: `OLD → NEW` for each changed field.

Ask: "Does this look correct? Should I proceed?"

Only write after confirmation.

---

## Step 4 — Detail Component Structure

The detail component lives at:
`src/components/options/strategies/{kebab-name}-strategy.tsx`

Export name convention: `{PascalCase}StrategyDetail`

### Required template:

```tsx
import { StrategyDetailProps } from '../strategy-config';

export const {Name}StrategyDetail = ({ strategy, onBack }: StrategyDetailProps) => {
  return (
    <div className="mt-6 space-y-6">

      {/* Header */}
      <div className="bg-gradient-to-r {header-gradient} p-6 rounded-xl border {header-border} mb-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <span className="text-2xl">📚</span>
          Strategy Details
        </h3>
      </div>

      {/* 1. Strategy Intuition — bg-slate-50 */}
      {/* 2. Implementation Framework — bg-indigo-50 */}
      {/* 3. Best Practices — bg-green-50 */}
      {/* 4. Optimal Market Conditions — bg-blue-50 */}
      {/* 5. Risk Management — bg-red-50 */}
      {/* 6. Advanced Applications (optional) — bg-purple-50 */}
      {/* 7. Educational Resources (optional) — bg-teal-50 */}

      {/* Risk Disclaimer — always last */}
      <div className="bg-gray-100 p-4 rounded-lg border border-gray-300">
        <p className="text-xs text-gray-600">
          <strong>Risk Disclosure:</strong> Options trading involves significant risk...
        </p>
      </div>

    </div>
  );
};
```

### Header gradient by strategy type:
- **Bullish** → `from-green-50 to-emerald-50` / `border-green-200`
- **Bearish** → `from-red-50 to-pink-50` / `border-red-200`
- **Neutral / Income** → `from-blue-50 to-indigo-50` / `border-blue-200`
- **Volatility** → `from-purple-50 to-violet-50` / `border-purple-200`
- **Risk Defined / Mixed** → `from-blue-50 to-indigo-50` / `border-blue-200`

### Section inner structure pattern:
```tsx
<div className="bg-{color}-50 p-4 md:p-6 rounded-xl shadow-lg border border-{color}-200">
  <h3 className="text-xl font-bold text-{color}-800 mb-4 flex items-center gap-2">
    <span className="text-2xl">{emoji}</span>
    Section Title
  </h3>
  <div className="text-sm text-{color}-700 space-y-4">
    <div className="border-l-4 border-{color}-300 pl-4">
      <h4 className="font-semibold mb-2">Subsection</h4>
      <ul className="list-disc list-inside space-y-1 ml-4">
        <li>...</li>
      </ul>
    </div>
  </div>
</div>
```

### Section emojis:
- Strategy Intuition: 🧠
- Implementation Framework: ⚙️
- Best Practices: ✅
- Optimal Market Conditions: 🌤️
- Risk Management: ⚠️
- Advanced Applications: 🎯
- Educational Resources: 📖

---

## Step 5 — Execute Changes

### For `add`, make all three changes:

**A. Create detail component** at `src/components/options/strategies/{kebab-name}-strategy.tsx`

**B. Update strategy-config.ts** — two edits:
1. Add import near the top (after existing imports, alphabetically by component name):
   ```ts
   import { {Name}StrategyDetail } from './strategies/{kebab-name}-strategy';
   ```
2. Add strategy entry to the `strategies` array at an appropriate position (group by category):
   ```ts
   {
       id: '{snake_id}',
       category: [...],
       name: '...',
       description: '...',
       profile: '...',
       volatility: '...',
       time: '...',
       payoffCalculator: (p, { ... }) => ...,
       youtubeId: '...',           // if provided
       payoffExplanation: '...',   // if provided
       relatedArticles: [...],     // if provided
       infographicUrl: '...',      // if provided
       detailComponent: {Name}StrategyDetail as ComponentType<StrategyDetailProps>
   },
   ```

**C. Update page.tsx** — add to `strategyMetadata`:
```ts
  '{kebab-slug}': {
    name: '{Strategy Name}',
    description: '...',
  },
```

### For `update`, only edit what changed.

---

## Step 6 — Verify

After writing all files, confirm:
- [ ] Detail component file created/updated
- [ ] Import added to strategy-config.ts (for new strategies)
- [ ] Strategy entry added/updated in strategies array
- [ ] Route metadata added/updated in page.tsx
- [ ] Export name in detail component matches import name in config

Report which files were changed and what was done.

---

## Real Example

Adding "Seagull Spread":
- `id`: `seagull_spread`
- `slug`: `seagull-spread`
- `category`: `['Neutral', 'Income', 'Risk Defined']`
- Component export: `SeagullSpreadStrategyDetail`
- Component file: `seagull-spread-strategy.tsx`
- Import line: `import { SeagullSpreadStrategyDetail } from './strategies/seagull-spread-strategy';`
