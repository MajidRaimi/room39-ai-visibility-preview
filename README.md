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

Selected backend: **FormSubmit.co** (free tier, no signup, no secret in the
repo). Point `LEAD_ENDPOINT` at the business inbox and leave `LEAD_ACCESS_KEY`
empty:

```js
const LEAD_ENDPOINT = "https://formsubmit.co/ajax/<business-inbox>";
const LEAD_ACCESS_KEY = "";
const LEAD_EMAIL = "<business-inbox>";
```

One-time activation (FormSubmit requirement): the **first** submission triggers a
confirmation email to `<business-inbox>`; the address is only active after
someone opens that email and clicks the activation link. After activation, every
submission is forwarded to the inbox. Limit: 50 submissions/month on the free
tier.

Web3Forms is also supported. Set `LEAD_ENDPOINT` to
`https://api.web3forms.com/submit` and paste the *public* access key in
`LEAD_ACCESS_KEY`. That key can only deliver to the form owner's inbox, so it is
safe to commit. No other secret is used anywhere in the repo.

Finally, set `LEAD_EMAIL` to the same real inbox so the failure message offers a
working mailto fallback.

If the endpoint is unconfigured (or a Web3Forms URL has no key), or `fetch` is
unavailable, the form shows an error and never reports a false success. The
submission body for FormSubmit includes `_captcha: "false"` and
`_template: "table"` so the AJAX request is not blocked and the email is
readable.

## Rollback

The site is static and versioned in git. To revert a change: `git revert <sha>` and push, or
reselect the previous commit in GitHub Pages settings. To take the preview offline, disable
Pages in the repo settings or delete the repo.

## Content notes

- Market figures are from public sources cited in the page footer.
- Copy avoids medical claims and patient data; the offer is organic/AI visibility only.
- `hello@room39.example` is a placeholder until the real business inbox is set.
