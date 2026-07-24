# Site-Wide Audit Checklist

Technical + structural audit for a whole blog. Order = audit order. For each
item: what to check, how to fix per platform, and why it matters. Produce
findings as ✅ / ⚠️ / ❌ with the fix applied or proposed.

## Contents

1. [Platform detection](#1-platform-detection)
2. [Indexability](#2-indexability)
3. [robots.txt & the AI-crawler decision](#3-robotstxt--the-ai-crawler-decision)
4. [Rendering: is the content in the HTML?](#4-rendering)
5. [Head templates](#5-head-templates)
6. [Feeds](#6-feeds)
7. [Site structure & internal linking](#7-site-structure--internal-linking)
8. [E-E-A-T pages](#8-e-e-a-t-pages)
9. [Performance / Core Web Vitals](#9-performance--core-web-vitals)
10. [llms.txt (honest assessment)](#10-llmstxt)
11. [Content inventory](#11-content-inventory)
12. [Prioritization & report format](#12-prioritization--report-format)

---

## 1. Platform detection

| Marker file | Platform | Notable defaults |
|---|---|---|
| `hugo.toml` / `config.toml`+`archetypes/` | Hugo | sitemap ✅ auto, RSS ✅ auto, robots ❌ (needs `enableRobotsTXT = true`) |
| `_config.yml` + `Gemfile` | Jekyll | use `jekyll-sitemap`, `jekyll-seo-tag`, `jekyll-feed` plugins |
| `_config.yml` + `package.json` w/ hexo | Hexo | needs `hexo-generator-sitemap`, `hexo-generator-feed` |
| `astro.config.*` | Astro | needs `@astrojs/sitemap`, `@astrojs/rss` |
| `next.config.*` | Next.js | needs `app/sitemap.ts`, `app/robots.ts`, metadata exports |
| `gatsby-config.*` | Gatsby | `gatsby-plugin-sitemap`, `gatsby-plugin-feed` |
| `docusaurus.config.*` | Docusaurus | sitemap ✅ via preset |
| `.vitepress/config.*` | VitePress | `sitemap` config option |
| `wp-content/` or DB dump | WordPress | Yoast/RankMath handle most of this |

Also note the deploy target if visible (GitHub Pages / Vercel / Netlify /
Cloudflare Pages) — it determines how `_headers`, redirects, and custom
robots/llms files are served.

### Theme note: Hugo + PaperMod (the most common blog stack)

Recent PaperMod ships most SEO plumbing as templates — the audit is mostly
**config flags**, and the fix is enabling them, not writing templates:

| Gap | Fix in `hugo.toml` |
|---|---|
| No robots.txt | `enableRobotsTXT = true` **and** see env row ↓ |
| robots.txt says `Disallow: /` (!) | PaperMod's template blocks ALL crawling unless the build is production: set `[params] env = "production"` (or build with `hugo --environment production`). A staging-flavored build silently de-indexes the whole site — check the *deployed* /robots.txt, not just the config |
| Empty home meta description | `[params] description = "..."` |
| Summary-only RSS | `[params] ShowFullTextinRSS = true` |
| No JSON-LD entity | PaperMod already emits WebSite/Person-or-Org (+ BreadcrumbList, BlogPosting on posts). Feed it: `[params.schema] publisherType = "Person"`, `sameAs = ["https://github.com/...", ...]`; social icons double as fallback sameAs |
| No default OG image | `[params] images = ["/og-default.png"]` (per-post `cover.image` overrides) |
| llms.txt template unused | PaperMod ships a `layouts/llms.txt` — enable via a custom `llms` output format on home in config `[outputs]` (check the theme's docs/wiki for the exact block of the installed version) |
| Meta description per post | fallback chain is page `description` → `summary` → site description — so per-post `description` frontmatter still matters (content inventory, §11) |
| CJK site: wordcount/summary/reading time all wrong | `hasCJKLanguage = true` — without it Hugo counts CJK text as one giant "word", breaking auto-summaries (which feed the description fallback), reading time, and `summaryLength` truncation |
| No FAQPage JSON-LD (theme doesn't ship it) | add via PaperMod's official extension hook `layouts/_partials/extend_head.html` (older versions: `layouts/partials/extend_head.html`) — never edit the theme |
| Every new post starts with bare frontmatter | write `archetypes/default.md` with `description`/`tags`/`lastmod`/`slug` placeholder fields so `hugo new` scaffolds them — fixes the root cause, not just today's posts |

Never edit files inside `themes/PaperMod/` — override by copying the template
into the site's own `layouts/` if customization is truly needed. When changing
a published post's URL (e.g. giving a CJK filename an ASCII `slug`), add the
old path to `aliases` in frontmatter so existing shared links don't break —
and describe it accurately: Hugo aliases are client-side meta-refresh stubs
with a canonical tag, not server 301s. Where the host supports real redirects
(Netlify `_redirects`, Vercel config, Cloudflare rules), prefer those.

## 2. Indexability

- **sitemap.xml** exists, includes all posts, excludes drafts/paginated/tag noise, and has **real `<lastmod>`** values (engines use lastmod to schedule recrawls; fake/absent lastmod = slow re-indexing). Check it's referenced in robots.txt (`Sitemap:` line) and submitted in Search Console + Bing Webmaster.
- **Canonical URLs** on every page, absolute, matching the canonical host. One host only: apex vs `www`, and http→https, must 301 to one form. Trailing-slash policy consistent.
- **No accidental noindex**: grep templates for `noindex` and check HTTP `X-Robots-Tag` headers. Common accident: staging flag left on, or theme noindexing everything but home.
- **Meaningful 404** returning HTTP 404 (not 200 soft-404).
- **HTTPS everywhere**, no mixed content.
- Tag/category/archive pages: keep them crawlable-but-thin-managed — either give tag pages descriptions or `noindex,follow` the near-empty ones. Paginated archives: leave indexable, canonical each page to itself.
- **Multilingual sites**: `hreflang` pairs (including `x-default`), one language per URL, no auto-redirect by IP.

## 3. robots.txt & the AI-crawler decision

robots.txt is now a **strategy file**: it decides visibility in AI answers,
not just crawl control. If exposure is the goal (it is, for this skill),
**allow AI crawlers** — blocked crawlers = the content can never be cited.

The bots that matter (2026):

| Bot | Controls | Blocking means |
|---|---|---|
| `Googlebot` | Google Search **and** AI Overviews/AI Mode grounding | invisible everywhere on Google |
| `Google-Extended` | Gemini **training** (not Search/AI Overviews) | your call — blocking doesn't affect search exposure |
| `Bingbot` | Bing Search → also feeds ChatGPT search & Copilot | invisible in Bing + degraded ChatGPT presence |
| `GPTBot` | OpenAI training | your call |
| `OAI-SearchBot` | ChatGPT **search/browsing citations** | ChatGPT can't cite you |
| `ClaudeBot` / `Claude-User` / `Claude-SearchBot` | Anthropic crawl / user-triggered fetch / search | Claude can't cite you |
| `PerplexityBot` / `Perplexity-User` | Perplexity index / user fetch | Perplexity can't cite you |
| `Applebot` / `Applebot-Extended` | Siri+Spotlight / Apple AI training | Siri suggestions lost / your call |
| `Bytespider`, `Amazonbot`, `cohere-ai`, `meta-externalagent` | various training | your call |

Recommended default for an exposure-maximizing blog:

```
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

…i.e. allow everything, plus explicit `Disallow` only for genuinely private
paths (`/admin/`, `/drafts/`). If the user distinguishes "cite me" from
"train on me": allow the *search/citation* bots (OAI-SearchBot,
Claude-SearchBot, PerplexityBot, Googlebot, Bingbot) and optionally disallow
the pure-training ones (GPTBot, Google-Extended, Applebot-Extended). Present
the trade-off; default to open.

Also check the **CDN/WAF layer**: Cloudflare "Block AI bots" toggle, bot-fight
mode, or aggressive rate limits silently 403 AI crawlers even when robots.txt
allows them. Server logs showing the bots above getting 200s is the ground
truth.

Per-platform: Hugo `enableRobotsTXT = true` + `layouts/robots.txt`; Jekyll:
static `robots.txt` in root; Next.js: `app/robots.ts`; Astro: `public/robots.txt`.

## 4. Rendering

**Most AI crawlers (and Bing's, partially) do not execute JavaScript.** Google
does, with delay. Any content that only exists after client-side JS runs is
invisible to the citation pipeline.

- Test: `curl -s https://site/post-url | grep -c "distinctive body phrase"` — if the article text isn't in the raw HTML, that's a ❌ blocker, priority #1.
- Static generators (Hugo/Jekyll/Hexo/Astro static) pass by construction.
- Next.js/Nuxt: posts must be SSG/SSR (`generateStaticParams` / server components), not client-fetched.
- SPA blogs (CRA, client-only Vue): recommend migration or prerendering — no meta-tag tweak compensates for empty HTML.
- Also verify title/description/OG/JSON-LD are server-rendered per page (not injected client-side by a router).

## 5. Head templates

Fix once in the theme → correct for every page. Required set per page type in
`structured-data.md` §"Beyond schema". Audit specifically:

- `<title>` pattern `{{page}} · {{site}}` — page part first; home page gets a real tagline, not just the site name.
- Meta description: pulled from frontmatter `description`, **fallback to summary/excerpt — never empty, never site-wide identical**.
- OG + Twitter card with **absolute** image URLs and a real default OG image (1200×630) for pages without covers.
- Canonical present (see §2), favicon set, `lang` attribute on `<html>` matching content language (`zh-CN` etc.), viewport meta.
- JSON-LD: `WebSite` + `Person` on home, `BlogPosting` on posts (`structured-data.md`).

## 6. Feeds

- **Full-content RSS/Atom** (not summaries): feeds are how aggregators, readers, and several AI/data pipelines ingest the blog; summary-only feeds cut reach for no real benefit. Hugo: set `[services.rss] limit`, override the RSS template's `.Summary` → `.Content`. Hexo: `hexo-generator-feed` `content: true`. Jekyll: `jekyll-feed` does full by default.
- `<link rel="alternate" type="application/rss+xml">` in head; feed URL visible in the footer/nav.
- JSON Feed optional, cheap via same data.

## 7. Site structure & internal linking

- Every post reachable within ~3 clicks of home; recent + related posts surfaced.
- **Topic clusters** (the highest-leverage structural work): group posts by theme; designate or create a **pillar page** (comprehensive overview) per theme; pillar links to every cluster post, each cluster post links back to the pillar and to 2–3 siblings. Hub-and-spoke linking concentrates topical authority and is how a small blog outranks bigger sites on its niche.
- Find **orphans** (no inbound internal links): cross-reference all posts vs the link graph (`seo_check.py --json` over the content dir gives per-post outbound lists to build the graph from).
- "Related posts" block: by shared tags at minimum; manual curation for the top 20% posts.
- Breadcrumbs visible + `BreadcrumbList` markup.
- Tag hygiene: consolidate near-duplicate tags (`docker` vs `Docker` vs `容器`); each tag should have ≥ 2 posts, else it's noise.

## 8. E-E-A-T pages

Engines evaluate the *site entity* behind the content:

- **About page**: who writes this, what expertise/experience backs it, real name or consistent pen name.
- **Author identity**: byline on posts, matching `Person` JSON-LD `name` exactly, `sameAs` → GitHub/X/LinkedIn/知乎 profiles. On those profiles, link back to the site (bidirectional confirmation).
- Contact route (email or form). Privacy policy if analytics/ads run (legally required in most places).
- Company blog: `Organization` schema, imprint per local law.

## 9. Performance / Core Web Vitals

Targets: **LCP < 2.5s, INP < 200ms, CLS < 0.1** (p75). For blogs, the usual
offenders and cheap fixes:

- Hero/cover images: compress (WebP/AVIF), explicit `width`/`height` (CLS), `loading="lazy"` for below-fold, `fetchpriority="high"` for the LCP image, responsive `srcset`.
- Fonts: `font-display: swap`, preload the one text font, subset CJK fonts (or use system font stack — 中文 webfonts are megabytes; `font-family: system-ui, "PingFang SC", "Microsoft YaHei"` is free and fast).
- Third-party JS (analytics, comments, ads) → `defer`/lazy-init; comment widgets (giscus/disqus) lazy-load on scroll.
- Measure with PageSpeed Insights (field data if the site has traffic; lab otherwise) before/after.
- Static blogs rarely have INP issues; if present, look at hydration cost (Astro islands / partial hydration beats full-page hydration).

## 10. llms.txt

`/llms.txt` (markdown index of the site for LLMs) — honest status 2026:
adoption ~10% of sites; **no major AI search crawler confirmed to fetch it in
production**; primarily consumed by coding agents and docs tooling. Verdict:
**low priority, low cost, non-zero upside** — add it in 10 minutes after the
high-impact items, never instead of them. Format:

```markdown
# {{Site name}}

> {{One-paragraph site description: who writes it, about what, for whom.}}

## Posts

- [{{Post title}}]({{absolute url}}): {{one-line description}}
- ...

## About

- [About the author]({{url}}/about): {{one line}}
```

Generate it from the same data as the RSS template (Hugo: custom output
format; or a small build script). Keep it fresh automatically or not at all.

## 11. Content inventory

Batch-audit all posts:

```bash
python3 scripts/seo_check.py <content-dir> --json > inventory.json
```

Then analyze across posts (not just per-post):

- Posts missing descriptions / covers / lastmod → bulk-fix list.
- Duplicate or near-duplicate **titles** targeting the same query → merge or differentiate (they cannibalize each other).
- **Thin posts** (< 300 words): merge into a stronger post (+ redirect) or expand.
- **Update candidates**: evergreen posts > 12 months old on topics that moved — refreshing these is the cheapest ranking/citation win available.
- Orphans (§7) and cluster gaps ("8 Docker posts but no pillar page").

## 12. Prioritization & report format

Sort findings by impact ÷ effort. Typical order when starting from zero:
rendering blockers → indexability (sitemap/robots/canonical) → head templates
(descriptions/OG/JSON-LD) → answer-first rewrites of top posts → internal
linking/clusters → E-E-A-T pages → performance → llms.txt.

```markdown
## 全站 SEO/GEO/AEO 体检报告 — {{site}}
**平台**: {{platform}} | **文章数**: {{n}} | **总体**: {{one-line verdict}}

### ✅ 已达标
### ❌ 已修复（本次改动）
- {{file}}: {{what & why}}
### ⚠️ 建议修复（按优先级）
1. {{item}} — 影响: {{...}} 工作量: {{S/M/L}}
### 📋 内容清单发现
{{table: post | score | top issues}}
### 🚀 站外行动（见 distribution.md）
1–3 items
```

Verify the site still builds after changes (`hugo`, `bundle exec jekyll
build`, `npm run build`…) when the toolchain is available.
