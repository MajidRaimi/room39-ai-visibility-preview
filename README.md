# Room 39 — one-page offer site (preview)

Static one-page site for Room 39's productized offer: **AI Search Visibility + Local SEO for independent med spas**.

Built from the Phase 1 niche recommendation in [ROO-2](/ROO/issues/ROO-2):
$99 AI Visibility Snapshot → $750 Visibility Audit + Fix → $2,500/mo Local AI Visibility Retainer.

## What it does

- One page: headline, the problem, how it works, pricing, trust, and a lead form.
- Primary CTA ("Get my $99 AI Visibility Snapshot") scrolls to the form; plan buttons preselect the matching option.
- Lead form validates required fields and completes with a success state. With no backend configured it opens a prefilled email in preview mode.
- No build step, no framework, no dependencies. Three files: `index.html`, `styles.css`, `script.js`.

## Run locally

```sh
python3 -m http.server 4173
# open http://localhost:4173
```

Any static file server works.

## Deploy (free tier)

Published with GitHub Pages from the repo root (branch `main`). No paid service.

## Configure leads (before real traffic)

In `script.js`, set `LEAD_ENDPOINT` to your form/CRM URL and replace `LEAD_EMAIL`.
When `LEAD_ENDPOINT` is empty the page uses the email fallback — safe for a preview.

## Rollback

The site is static and versioned in git. To revert a change: `git revert <sha>` and push, or
reselect the previous commit in GitHub Pages settings. To take the preview offline, disable
Pages in the repo settings or delete the repo.

## Content notes

- Market figures are from public sources cited in the page footer.
- Copy avoids medical claims and patient data; the offer is organic/AI visibility only.
- `hello@room39.example` and the form endpoint are placeholders for the preview.
