# Room 39 — med spa content site (Track B)

Static content site for Room 39's Track B asset: AI-search visibility and local SEO
guides for independent med spas (1–3 locations).

Built from the [ROO-4](/ROO/issues/ROO-4) content plan and the three finished drafts.
The content site links to the offer site CTA
(`https://majidraimi.github.io/room39-ai-visibility-preview/#lead`) on every page.

## Pages

| Page | Slug | Target query | Schema |
|---|---|---|---|
| How to Get Your Med Spa to Show Up in ChatGPT | `/med-spa-chatgpt-visibility/` | how to get your business to show up in chatgpt | Article + FAQPage |
| Med Spa SEO Pricing: What Agencies Actually Charge | `/med-spa-seo-pricing/` | med spa seo pricing | Article + FAQPage |
| Best AI Visibility Tools for Med Spas | `/best-ai-visibility-tools-med-spa/` | best ai visibility tools | Article + FAQPage |

Plus `/` (hub), `sitemap.xml`, `robots.txt`, and `llms.txt`.

## Build

Content source of truth is `src/page-*.md` (verbatim copies of the ROO-4 draft
documents). The generator rewrites internal links, injects the byline, wraps the
body in a head with title/meta/canonical/OG/JSON-LD, and adds the offer CTA.

```sh
python3 build.py      # requires python-markdown (>=3.4)
python3 -m http.server 4173   # preview at http://localhost:4173
```

## Deploy (free tier)

GitHub Pages from the repo root (branch `main`), via
`.github/workflows/pages.yml`. No paid service, no build step on the host.

`SITE_BASE` in `build.py` is the assumed production URL
(`https://majidraimi.github.io/room39-med-spa-guide`). If the repo is created under
a different name, change `SITE_BASE`, rerun `build.py`, and commit the regenerated
files so canonical URLs, OG tags, and the sitemap stay correct.

## Standards kept

- One target query per page, answered in the first screen.
- Title tag 50–60 chars, meta description 140–160 chars.
- One H1, question-shaped H2/H3s.
- Every number has an inline, dated source.
- Affiliate disclosure on the tools page.
- No medical claims, no patient data, no invented reviews.
- No secrets in the repo.
