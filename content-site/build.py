#!/usr/bin/env python3
"""Build the Room 39 med-spa content site from the Track B markdown drafts.

Content source of truth: src/page-*.md (copied from the ROO-4 draft documents).
This script converts each draft into a static HTML page with intact on-page SEO
fields (title, meta description, canonical, H1/H2, JSON-LD Article + FAQPage,
internal links) and an offer-site CTA.

Run:  python3 build.py
No dependencies beyond the stdlib and python-markdown (>=3.4).
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT

# --- Site config -------------------------------------------------------------
# If Forge deploys to a different repo/domain, change SITE_BASE here and rerun.
SITE_BASE = "https://majidraimi.github.io/room39-med-spa-guide"
OFFER_URL = "https://majidraimi.github.io/room39-ai-visibility-preview/"
OFFER_CTA = OFFER_URL + "#lead"
SITE_NAME = "Room 39"
SITE_TAGLINE = "AI search visibility and local SEO for independent med spas"
LAST_UPDATED = "2026-10-05"

PAGES = [
    "page-1-chatgpt-visibility.md",
    "page-5-seo-pricing.md",
    "page-6-ai-visibility-tools.md",
]

# Anchor-text -> destination. Value None means "unwrap the link" (target page
# not published yet); never ship a link to a page that does not exist.
LINK_MAP = {
    "ai visibility audit": OFFER_CTA,
    "$99 ai visibility snapshot": OFFER_CTA,
    "$750 visibility audit + fix": OFFER_CTA,
    "$2,500/month local ai visibility retainer": OFFER_CTA,
    "$2,500/month retainer": OFFER_CTA,
    "med spa seo pricing": "/med-spa-seo-pricing/",
    "med spa seo pricing — what all of this actually costs": "/med-spa-seo-pricing/",
    "best ai visibility tracking tools for med spas": "/best-ai-visibility-tools-med-spa/",
    "how to get your med spa to show up in chatgpt": "/med-spa-chatgpt-visibility/",
    "chatgpt visibility guide": "/med-spa-chatgpt-visibility/",
    "page 4": None,
    "google business profile for med spas": None,
    "med spa schema markup": None,
    "how to audit your med spa's ai visibility": None,
    "how to choose a med spa marketing agency": None,
    "profound vs semrush vs ahrefs": None,
    "roo-2": None,
}

MD_EXTENSIONS = ["extra", "tables", "sane_lists"]

INTERNAL_LINKS = {  # slug -> (nav label, short description for the hub)
    "/med-spa-chatgpt-visibility/": (
        "ChatGPT visibility",
        "How to get your med spa named in ChatGPT answers, with a 30-day plan.",
    ),
    "/med-spa-seo-pricing/": (
        "Med spa SEO pricing",
        "What agencies actually charge, what drives the number, and how to decide.",
    ),
    "/best-ai-visibility-tools-med-spa/": (
        "AI visibility tools",
        "Five clinic-sized tools compared, plus the free method you can run today.",
    ),
}


def parse_title_meta(text: str) -> dict:
    def grab(pattern: str, default: str = "") -> str:
        m = re.search(pattern, text)
        return m.group(1).strip() if m else default

    title = grab(r"\*\*Title tag[^:]*:\*\*\s*(.+)")
    # strip a trailing "(NN chars)" note if present
    title = re.sub(r"\s*\(\d+\s*chars?\)\s*$", "", title).strip()
    meta = grab(r"\*\*Meta description[^:]*:\*\*\s*(.+)")
    meta = re.sub(r"\s*\(\d+\s*chars?\)\s*$", "", meta).strip()
    slug = grab(r"\*\*Slug:\*\*\s*`?([^`\n]+?)`?\s*$")
    if not slug:
        slug = grab(r"\*\*Slug:\*\*\s*(\S+)")
    return {"title": title, "meta": meta, "slug": slug.strip().strip("`").strip("/")}


def extract_body(text: str) -> str:
    """Body = from the content '# H1' line to end (includes Sources).

    The source drafts carry a leading '# Draft — Page N: …' marker plus a
    'Target query / SEO fields' scaffolding block before the real content H1.
    Start at the first top-level H1 that is not the draft marker so the
    scaffolding never reaches the published page.
    """
    matches = list(re.finditer(r"^#\s+.+$", text, re.MULTILINE))
    if not matches:
        raise ValueError("no H1 found")
    content = [m for m in matches if not re.match(r"#\s*Draft\b", m.group(0))]
    m = content[0] if content else matches[-1]
    return text[m.start():].strip()


def extract_disclosure(raw: str) -> str | None:
    """Pull the required affiliate disclosure out of the draft scaffolding."""
    m = re.search(r"\*\*Affiliate disclosure[^:]*:\*\*\s*(.+)", raw)
    return m.group(1).strip() if m else None


def rewrite_links(text: str) -> str:
    text = text.replace(
        "(See [Page 4](/ROO/issues/ROO-4), Med Spa Schema Markup.)",
        "(A dedicated guide on med spa schema markup is coming next.)",
    )

    def repl(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        if target.startswith("/ROO/issues/"):
            dest = LINK_MAP.get(label.strip().lower(), None)
            if dest is None:
                return label  # unwrap: no dead links
            return f"[{label}]({dest})"
        return m.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, text)


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html5")


def plain(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`>#]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_faq(body_md: str) -> list[dict]:
    m = re.search(r"^##\s+Frequently asked questions\s*$", body_md, re.MULTILINE)
    if not m:
        return []
    section = body_md[m.end():]
    # stop at the next H2 that is not an FAQ item (e.g. "What to do next")
    end = re.search(r"^##\s+", section, re.MULTILINE)
    if end:
        section = section[: end.start()]
    faqs = []
    for block in re.split(r"^###\s+", section, flags=re.MULTILINE)[1:]:
        lines = block.strip().splitlines()
        q = lines[0].strip()
        answer = plain("\n".join(lines[1:]))
        if q and answer:
            faqs.append({"q": q, "a": answer})
    return faqs


def jsonld(page: dict, faqs: list[dict]) -> str:
    graph = [
        {
            "@type": "Article",
            "headline": page["h1"],
            "description": page["meta"],
            "datePublished": LAST_UPDATED,
            "dateModified": LAST_UPDATED,
            "inLanguage": "en",
            "author": {
                "@type": "Person",
                "name": "Quill",
                "jobTitle": "Content & SEO",
                "worksFor": {"@type": "Organization", "name": SITE_NAME},
            },
            "publisher": {"@type": "Organization", "name": SITE_NAME},
            "mainEntityOfPage": {"@type": "WebPage", "@id": page["absolute_url"]},
        }
    ]
    if faqs:
        graph.append(
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
                    }
                    for f in faqs
                ],
            }
        )
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)


def head(page: dict, faqs: list[dict]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(page['title'])}</title>
  <meta name="description" content="{html.escape(page['meta'])}" />
  <link rel="canonical" href="{page['absolute_url']}" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <meta name="theme-color" content="#21453A" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{html.escape(page['title'])}" />
  <meta property="og:description" content="{html.escape(page['meta'])}" />
  <meta property="og:url" content="{page['absolute_url']}" />
  <meta property="og:site_name" content="{SITE_NAME}" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%2321453A'/%3E%3Cpath d='M9 23V9h6.2c2.6 0 4.3 1.3 4.3 3.4 0 1.5-.8 2.6-2.2 3 1.7.3 2.8 1.5 2.8 3.3 0 2.4-1.9 3.9-4.9 3.9H9z' fill='%23FBF9F6'/%3E%3C/svg%3E" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/style.css" />
  <script type="application/ld+json">
{jsonld(page, faqs)}
  </script>
</head>"""


def header_html() -> str:
    links = "\n".join(
        f'        <a href="{slug}">{label}</a>' for slug, (label, _) in INTERNAL_LINKS.items()
    )
    return f"""<body>
  <header class="site-head">
    <div class="wrap head-inner">
      <a class="brand" href="/"><span class="brand-mark">R39</span><span>Room&nbsp;39</span></a>
      <nav aria-label="Content">
{links}
      </nav>
      <a class="btn btn-sm" href="{OFFER_CTA}">$99 snapshot</a>
    </div>
  </header>
  <main>"""


def cta_html(page: dict) -> str:
    return f"""    <aside class="cta">
      <h2>See where your clinic stands in AI answers</h2>
      <p>Our <strong>$99 AI Visibility Snapshot</strong> checks whether ChatGPT, Google AI
      Overviews, and Perplexity name your med spa for your top treatments, then gives you a
      prioritized fix list. Fixed price, delivered in 48 hours.</p>
      <a class="btn" href="{OFFER_CTA}">Get my $99 AI Visibility Snapshot</a>
    </aside>"""


def footer_html() -> str:
    return f"""  </main>
  <footer class="site-foot">
    <div class="wrap">
      <p class="foot-brand">{SITE_NAME} — {SITE_TAGLINE}.</p>
      <p>Not medical advice. We work on organic visibility and never handle patient data.</p>
      <p><a href="{OFFER_URL}">Offer site &amp; pricing</a> ·
         <a href="/sitemap.xml">Sitemap</a></p>
    </div>
  </footer>
</body>
</html>
"""


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    built = []

    for fname in PAGES:
        raw = (SRC / fname).read_text(encoding="utf-8")
        meta = parse_title_meta(raw)
        if not meta["title"] or not meta["meta"] or not meta["slug"]:
            raise ValueError(f"missing SEO fields in {fname}: {meta}")
        body_md = extract_body(raw)
        h1 = plain(body_md.splitlines()[0].lstrip("# ").strip())
        disclosure = extract_disclosure(raw)
        body_md = rewrite_links(body_md)
        faqs = extract_faq(body_md)
        slug = "/" + meta["slug"].strip("/") + "/"
        page = {
            **meta,
            "h1": h1,
            "slug": slug,
            "absolute_url": SITE_BASE + slug,
        }
        article_html = md_to_html(body_md)
        # Inject byline after the H1.
        byline = (
            f'<p class="byline">By Quill, Content &amp; SEO, {SITE_NAME} · '
            f'<span class="updated">Last updated {LAST_UPDATED}</span></p>'
        )
        article_html = article_html.replace("</h1>", "</h1>\n" + byline, 1)
        if disclosure:
            callout = (
                '<p class="affiliate-disclosure"><strong>Affiliate disclosure:</strong> '
                + html.escape(disclosure)
                + "</p>"
            )
            article_html = article_html.replace(byline, byline + "\n" + callout, 1)

        page_html = (
            head(page, faqs)
            + "\n"
            + header_html()
            + '\n    <article class="prose">\n'
            + article_html
            + "\n    </article>\n"
            + cta_html(page)
            + "\n"
            + footer_html()
        )

        outdir = OUT / meta["slug"].strip("/")
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "index.html").write_text(page_html, encoding="utf-8")
        built.append(page)
        print(f"built {slug}  (faq items: {len(faqs)})")

    write_hub(built)
    write_sitemap(built)
    write_robots()
    write_llms(built)
    print("done")


def write_hub(built: list[dict]) -> None:
    cards = []
    for p in built:
        label, desc = INTERNAL_LINKS[p["slug"]]
        cards.append(
            f"""      <a class="card" href="{p['slug']}">
        <h2>{html.escape(p['h1'])}</h2>
        <p>{html.escape(desc)}</p>
        <span class="read">Read the guide &rarr;</span>
      </a>"""
        )
    cards_html = "\n".join(cards)
    page = {
        "title": "Room 39 — AI visibility and local SEO for independent med spas",
        "meta": "Plain-English guides on getting your med spa found in ChatGPT, Google AI "
        "Overviews, and local search. Published prices and real numbers.",
        "absolute_url": SITE_BASE + "/",
        "h1": "Get your clinic named in AI answers",
    }
    doc = f"""{head(page, [])}
{header_html()}
    <section class="hub-hero wrap">
      <span class="eyebrow">For independent med spa owners</span>
      <h1>Get your clinic named in AI answers</h1>
      <p class="lede">Practical, sourced guides on AI search visibility and local SEO for
      1&ndash;3 location medical aesthetics clinics. No jargon, no hidden prices.</p>
      <a class="btn" href="{OFFER_CTA}">Get my $99 AI Visibility Snapshot</a>
    </section>
    <section class="wrap">
      <div class="cards">
{cards_html}
      </div>
    </section>
{footer_html()}"""
    (OUT / "index.html").write_text(doc, encoding="utf-8")
    print("built /")


def write_sitemap(built: list[dict]) -> None:
    urls = [SITE_BASE + "/"] + [p["absolute_url"] for p in built]
    items = "\n".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{LAST_UPDATED}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n"
        f"    <priority>{'1.0' if u == SITE_BASE + '/' else '0.8'}</priority>\n  </url>"
        for u in urls
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n</urlset>\n",
        encoding="utf-8",
    )


def write_robots() -> None:
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n"
        "User-agent: GPTBot\nAllow: /\n"
        "User-agent: ChatGPT-User\nAllow: /\n"
        "User-agent: PerplexityBot\nAllow: /\n"
        "User-agent: Google-Extended\nAllow: /\n"
        f"\nSitemap: {SITE_BASE}/sitemap.xml\n",
        encoding="utf-8",
    )


def write_llms(built: list[dict]) -> None:
    lines = [
        f"# {SITE_NAME}",
        "",
        f"> {SITE_TAGLINE}",
        "",
        "## Guides",
        "",
    ]
    for p in built:
        lines.append(f"- [{p['h1']}]({p['absolute_url']}): {p['meta']}")
    lines += ["", "## Offer", "", f"- [$99 AI Visibility Snapshot]({OFFER_CTA})"]
    (OUT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
