# Room 39 — one-page offer site (preview)

Static one-page site for Room 39's productized offer: **AI Search Visibility + Local SEO for independent med spas**.

Built from the Phase 1 niche recommendation in [ROO-2](/ROO/issues/ROO-2):
$99 AI Visibility Snapshot → $750 Visibility Audit + Fix → $2,500/mo Local AI Visibility Retainer.

## What it does

- One page: headline, the problem, how it works, pricing, trust, and a lead form.
- Primary CTA ("Get my $99 AI Visibility Snapshot") scrolls to the form; plan buttons preselect the matching option.
- Lead form validates required fields and POSTs to a free form backend. The success panel appears only after a real 2xx; failures show an error and re-enable the button.
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

Lead capture uses a **free, serverless form backend**. The form POSTs JSON to
`LEAD_ENDPOINT` in `script.js` and shows the success panel **only on a real 2xx
response**; any network error or non-2xx shows a visible error instead.

Default backend: **Web3Forms** (free tier, no server). Set the public access key:

```js
const LEAD_ENDPOINT = "https://api.web3forms.com/submit";
const LEAD_ACCESS_KEY = "<public Web3Forms access key>";
```

The access key is a *public form key*: it can only deliver mail to the form
owner's inbox, so it is safe to commit. No other secret is used.

URL-keyed backends (Formspree, FormSubmit, Getform) work too — set
`LEAD_ENDPOINT` to the provider URL and leave `LEAD_ACCESS_KEY` empty.

Also replace `LEAD_EMAIL` with the real business inbox so the failure message
offers a working mailto fallback.

If `LEAD_ENDPOINT` is a Web3Forms URL with no key, or fetch is unavailable, the
form shows an error and never reports a false success.

## Rollback

The site is static and versioned in git. To revert a change: `git revert <sha>` and push, or
reselect the previous commit in GitHub Pages settings. To take the preview offline, disable
Pages in the repo settings or delete the repo.

## Content notes

- Market figures are from public sources cited in the page footer.
- Copy avoids medical claims and patient data; the offer is organic/AI visibility only.
- `hello@room39.example` is a placeholder until the real business inbox is set.
