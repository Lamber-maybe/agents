---
name: blog-seo-optimizer
description: >-
  Optimize blog posts and entire blog sites for SEO (search engines), GEO
  (Generative Engine Optimization — getting cited by ChatGPT, Perplexity,
  Claude, Google AI Overviews), and AEO (Answer Engine Optimization — featured
  snippets, direct answers). Use this skill whenever the user wants to: polish
  a finished article before publishing, improve a post's search ranking or
  discoverability, get more traffic/impressions/citations, audit a blog or
  static site (Hugo/Hexo/Jekyll/Astro/Next.js/WordPress...) for SEO issues,
  add meta tags/structured data/sitemap/robots.txt/llms.txt, or improve
  exposure of their content. Trigger on phrases like "SEO", "GEO", "AEO",
  "优化文章", "SEO 优化", "提高曝光", "收录", "被搜到", "被 AI 引用", "引流",
  "optimize my post", "more traffic", "get indexed", "rank better" — even when
  the user just says "帮我优化这篇文章" or "review my blog before I publish".
---

# Blog SEO / GEO / AEO Optimizer

Make blog content maximally discoverable across the three channels people find
content today:

- **SEO** — classic search engines (Google, Bing, Baidu): crawling, indexing, ranking, click-through.
- **GEO** (Generative Engine Optimization) — AI answer engines (ChatGPT, Perplexity, Claude, Google AI Overviews/AI Mode, Copilot): being retrieved and **cited** in generated answers.
- **AEO** (Answer Engine Optimization) — featured snippets, People-Also-Ask boxes, voice assistants: being the extracted direct answer.

These overlap heavily. One well-structured page serves all three; the workflows below produce that page.

## Language rules

- Optimize content **in the article's language** (Chinese article → Chinese title/description/FAQ; don't translate).
- Report findings to the user **in the user's language**.
- Character budgets differ for CJK: a CJK character occupies roughly double the SERP width of a Latin character. `scripts/seo_check.py` handles this automatically — trust its width-based numbers over raw character counts.

## Non-negotiables (why they matter)

1. **Never fabricate** statistics, quotes, studies, dates, or credentials. Citations and data boost AI-engine visibility *because* engines weigh trustworthiness; fake evidence destroys exactly what you're optimizing for. Add numbers only from the article itself, the user, or sources you actually verified. If the article would benefit from data it doesn't have, add a `TODO(author)` note instead of inventing it.
2. **Preserve the author's voice and technical substance.** Restructure, tighten, and enrich — don't sand the personality off or dumb the content down. Experience-flavored writing ("我们踩过的坑", "in my testing") is an E-E-A-T *asset*; keep it.
3. **No spam techniques**: no keyword stuffing, hidden text, doorway pages, or fake freshness (bumping dates without real updates). These get sites demoted and are the opposite of durable exposure.
4. **Optimize for humans first.** Snippets, citations, and rankings all ultimately reward content people actually want to read. If a change makes the article worse to read, don't make it.

## Choosing a workflow

| User intent | Workflow |
|---|---|
| "我写完了这篇文章，帮我优化" / optimize this post | **A — Single article** (below) |
| "帮我整站做 SEO 体检/优化" / audit my blog | **B — Site-wide audit** (below) |
| "怎么提高曝光/引流/被 AI 引用" (no specific file) | **C — Distribution & exposure plan**: read `references/distribution.md` and produce a prioritized action plan for their situation |

When the user gives a file *and* mentions the site, do A, then offer B.

---

## Workflow A: Optimize a single article

### 1. Measure the baseline

```bash
python3 scripts/seo_check.py <article> [--keyword "主关键词"]
```

The script scores the article 0–100 against mechanical rules (title/description width, heading hierarchy, alt text, links, FAQ, evidence density, frontmatter completeness...). Save the score to compare after optimizing. It never modifies files.

### 2. Read the article fully and identify the search intent

Read the whole article, then determine:

- **Primary query**: the one search/AI question this article should be *the* answer to. Phrase it the way a real person would type or ask it.
- **Query cluster**: 3–6 related questions/phrasings (these become headings and FAQ items).
- **Intent type**: informational how-to, comparison, troubleshooting, opinion/experience? The intent dictates structure (how-to → steps + HowTo schema; comparison → table; troubleshooting → problem/cause/fix blocks).

If the user supplied a target keyword, use it; otherwise infer and state your choice in the report so the user can correct it.

Also judge whether the post *wants* full treatment: personal notes, diaries,
and year-in-review posts deserve metadata hygiene (description, slug, tags)
but not FAQ sections and keyword-tuned headings — over-optimizing personal
writing reads as spam and erodes the site's human voice. Say so in the report
instead of forcing the checklist.

### 3. Optimize — read `references/article-checklist.md` and apply it

That file is the full per-item guide (targets, examples, CJK variants, why each item works). The high-level moves, in order of impact:

1. **Title** — front-load the primary query, add a concrete differentiator (number, year, outcome). Fits SERP width; matches content honestly.
2. **Meta description** — a 1–2 sentence ad for the click: what the reader gets + why this page. Width-checked by the script.
3. **Answer-first opening** — the first paragraph directly answers the primary query in 2–4 sentences (this is what snippets and AI answers extract). Delete throat-clearing intros ("在当今快速发展的时代…" dies here). Then the article expands with the details, evidence, and story.
4. **Heading structure** — one H1; H2s as question-form or claim-form subtopics, one topic per section, each section self-contained (AI engines retrieve *chunks*, and a chunk that stands alone gets cited alone).
5. **Extractable formats** — turn prose enumerations into lists, comparisons into tables, processes into numbered steps. Define key terms with "X 是…" / "X is …" sentences.
6. **Evidence density** — surface the article's real numbers, benchmarks, and firsthand results; attribute external claims ("According to …" / "据 …"). This is the single strongest GEO lever (Princeton GEO research: +30–40% AI-answer visibility).
7. **FAQ section** — 3–5 real adjacent questions (from the query cluster), each answered in 40–60 words, standalone.
8. **Images** — descriptive alt text (in article language), meaningful filenames, cover/OG image set in frontmatter.
9. **Links** — 2–5 contextual internal links (ask for / glob the user's other posts if available), authoritative external links with descriptive anchors.
10. **Frontmatter/metadata completeness** — description, tags, date + lastmod, slug (ASCII, hyphenated, short — especially for CJK blogs), cover image, author.
11. **Structured data** — if the platform supports it, add/verify JSON-LD (`BlogPosting` + `FAQPage` at minimum). Templates and platform placement: `references/structured-data.md`.

Edit the file in place (or as the user directs). Keep the diff reviewable: don't rewrite paragraphs whose content you aren't improving.

### 4. Verify and report

Re-run `seo_check.py` — the score must improve; fix anything still red. Then give the user a report:

```markdown
## 优化报告：<article>
**得分**：58 → 92 | **主关键词**：<primary query> | **意图**：<type>

### 改了什么（按影响排序)
- <change> — <why it increases exposure>
...

### 需要你确认/补充
- <e.g. TODO(author) placeholders, keyword choice, internal link targets>

### 发布后动作（可选但强烈建议）
- <1–3 items from references/distribution.md relevant to this post: e.g. submit URL in Search Console, syndicate with canonical...>
```

---

## Workflow B: Site-wide audit & fix

### 1. Detect the platform

Look for config files: `hugo.toml`/`config.toml` (Hugo), `_config.yml` (Jekyll/Hexo), `astro.config.*`, `next.config.*`, `gatsby-config.*`, `docusaurus.config.*`, `.vitepress/`, `wp-content/` (WordPress). The platform determines where meta templates, sitemap, RSS, and robots.txt come from — many have good defaults that just need enabling. Platform-specific notes: `references/site-audit.md`.

### 2. Technical foundation audit

Work through `references/site-audit.md` — it covers, with per-platform fixes:

- Indexability: sitemap.xml (with real lastmod), robots.txt (and the **AI-crawler allowlist decision** — GPTBot, ClaudeBot, PerplexityBot etc.; blocking them = invisible to AI answers), canonical URLs, no accidental `noindex`, HTTPS, one canonical host.
- Rendering: content must be in the server-rendered HTML. **Most AI crawlers do not execute JavaScript** — a client-side-rendered blog is invisible to them. Static generators pass automatically; SPA blogs need SSR/prerendering.
- Site-wide templates: `<title>` pattern, meta description fallback, Open Graph + Twitter cards, RSS/Atom **full-content** feed, JSON-LD (`WebSite`, `Person`/`Organization`), favicon, 404.
- E-E-A-T pages: about, author page(s) with bio/credentials + `Person` schema + `sameAs` links, contact.
- Performance quick wins: image sizing/lazy-loading, font loading, Core Web Vitals (LCP < 2.5s, INP < 200ms, CLS < 0.1).
- `llms.txt`: cheap to add, be honest with the user — as of 2026 no major AI search crawler is confirmed to consume it in production; it mainly helps docs-style consumption and coding agents. Low priority, non-zero upside.

### 3. Content inventory

Batch-score every post:

```bash
python3 scripts/seo_check.py content/posts/ --json > /tmp/seo_inventory.json
```

From the summary, identify: posts missing descriptions, duplicate/near-duplicate titles, thin posts (merge or expand), stale high-traffic candidates (update + real lastmod), orphan posts (no internal links pointing in), and **topic clusters** — group related posts, designate/create a pillar page, and interlink the cluster (hub-and-spoke internal linking is the highest-leverage structural fix for topical authority).

### 4. Prioritize, fix, report

Produce a prioritized plan — quick wins first (impact ÷ effort), then projects. Apply the fixes the user asked for (or the safe high-impact ones, listing everything you changed). Verify the site still builds if a build command is available. End the report with the top 3 off-site actions from `references/distribution.md` (typically: Search Console + Bing Webmaster submission, IndexNow for instant indexing, one syndication channel with canonical).

---

## Reference files — when to read what

| File | Read when |
|---|---|
| `references/article-checklist.md` | Every Workflow A run (step 3) — full per-item targets & examples |
| `references/structured-data.md` | Adding/verifying JSON-LD (either workflow) |
| `references/site-audit.md` | Every Workflow B run — technical checklist + per-platform fixes |
| `references/distribution.md` | Workflow C; and the closing recommendations of A/B — indexing submission, AI-engine channels, syndication, communities, Chinese-ecosystem (百度/微信/知乎/掘金) specifics |

`scripts/seo_check.py --help` shows all options (`--keyword`, `--json`, directory batch mode).
