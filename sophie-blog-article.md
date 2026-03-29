# Sophie Blog Article Skill

Create a new blog article for SOPHIE's Daddy Quant Blog from 3 inputs.

## Inputs (ask if not provided)
- **Image URL** — Imgur URL
- **Research URL** — Google Doc or sophie-ai-finance.com URL
- **Article body** — full JSX/content to render

## Derive All Fields Automatically

| Field | Source |
|---|---|
| `slug` | Last path segment of research URL; if Google Doc, derive from title in kebab-case |
| `title` | First `#` heading in body |
| `description` | First substantive paragraph (2–3 sentences) |
| `date` | Today's date as "Month DD, YYYY" |
| `googleDoc` | Set if URL is a Google Doc (`docs.google.com`), else omit |
| `deepResearch` | `true` if long-form analytical/data-heavy content |
| `options` | `true` if covers options trading, Greeks, volatility strategies |
| `labels` | `QUANT` (quant/factor/stats), `AI_ML` (ML/AI/neural nets), `STOCK_ANALYSIS` (DCF/valuation/earnings) — omit if unclear |

Only include fields that apply. Omit the rest.

## Quarter File

Map today's date: Jan–Mar=q1, Apr–Jun=q2, Jul–Sep=q3, Oct–Dec=q4
Path: `src/data/articles/{year}-{quarter}.ts`

Insert **at the beginning** of the array (newest first). If file doesn't exist, create it and add import to `src/data/articles/index.ts`.

## Page File

Create `src/app/articles/{slug}/page.tsx`. Follow the structure and style of an existing deep research article (e.g., `src/app/articles/institutional-hft-market-manipulation-regulatory-framework/page.tsx`) with these mandatory elements:

1. `'use client'` at top
2. SEO block (mandatory):
```tsx
{currentArticle && (<><StructuredData article={currentArticle} /><BreadcrumbStructuredData articleTitle={currentArticle.title} articleSlug={currentArticle.slug} /></>)}
```
3. Return to Home button (`bg-blue-800`, ArrowLeft icon, links to `/`)
4. Hero section with `h1` (title) and subtitle (description)
5. Infographic with `FullScreenImageViewer` (if imageUrl present) — clickable, full-screen on click, Maximize2 icon overlay
6. Article body content
7. If `googleDoc` set — add a styled CTA section linking to the doc (indigo gradient, ExternalLink icon, "Read Full Research Report")
8. Risk disclaimer (red left-border box, AlertCircle icon)
9. Footer: `© 2025 SOPHIE's Daddy Quant Blog. Educational content for informational purposes only.`

## Content Rules
- Use HTML entities in JSX: `&amp;` `&mdash;` `&ldquo;` `&rdquo;` `&apos;` — never raw Unicode equivalents
- Educational only, not investment advice
