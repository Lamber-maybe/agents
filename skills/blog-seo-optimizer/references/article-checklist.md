# Per-Article Optimization Checklist (SEO + GEO + AEO)

Targets, examples, and the reasoning behind every on-page item. Work through
top to bottom — items are ordered roughly by impact. CJK notes apply to
Chinese/Japanese/Korean content.

## Contents

1. [Search intent & keyword](#1-search-intent--keyword)
2. [Title](#2-title)
3. [Meta description](#3-meta-description)
4. [URL slug](#4-url-slug)
5. [Answer-first opening](#5-answer-first-opening)
6. [Heading structure](#6-heading-structure)
7. [Body: extractable, chunk-friendly writing](#7-body-extractable-chunk-friendly-writing)
8. [Evidence density (the GEO lever)](#8-evidence-density-the-geo-lever)
9. [FAQ section](#9-faq-section)
10. [Images](#10-images)
11. [Links](#11-links)
12. [Frontmatter completeness](#12-frontmatter-completeness)
13. [Freshness](#13-freshness)
14. [E-E-A-T signals inside the article](#14-e-e-a-t-signals-inside-the-article)
15. [Anti-patterns that get content ignored or demoted](#15-anti-patterns)

---

## 1. Search intent & keyword

Decide **one primary query** — phrased as a human types/asks it — plus a
cluster of 3–6 related questions. Everything else on this list serves that
decision.

- Intent types and the structure they demand:
  - **How-to / tutorial** → numbered steps, prerequisites, expected outcome, HowTo schema candidate.
  - **Comparison / "X vs Y" / 选型** → criteria table early, clear recommendation with conditions ("choose X when…").
  - **Troubleshooting / error message** → the error string verbatim in title/H1, cause → fix blocks.
  - **Concept / "what is"** → definition sentence first, then depth.
  - **Opinion / experience / 复盘** → the claim in the title, evidence and story in the body. These earn citations *because* they contain original firsthand material no one else has.
- Placement: primary query appears in the title, the H1, the first paragraph,
  at least one H2, and the meta description — **once each, naturally**. That's
  full coverage; more repetition is stuffing, which engines discount.

## 2. Title

The single highest-leverage line. It is simultaneously a ranking signal, the
SERP ad copy, and the anchor AI engines display when citing you.

- **Width**: ≤ 60 Latin chars / ≈ 30 CJK chars (Google truncates at ~600px). `seo_check.py` measures width correctly for mixed text.
- **Front-load** the primary query — truncation eats the tail, and scanners read the front.
- Add one **concrete differentiator**: a number, a year, a result, a scope. Concrete beats generic in both CTR studies and AI citation behavior.
- The title must be a promise the article keeps. Clickbait mismatch = high bounce = demotion.

**Examples**

| Weak | Strong |
|---|---|
| Docker镜像优化 | Docker 镜像瘦身实战：从 1.2GB 到 180MB 的 6 个步骤 |
| Thoughts on RAG | RAG Chunking Strategies Compared: What Actually Improved Our Retrieval |
| About FastAPI auth | FastAPI JWT Authentication: Complete Setup with Refresh Tokens (2026) |

- Frontmatter `title` vs body H1: most platforms render frontmatter title as
  the H1. If so, do **not** repeat a `# H1` in the body (duplicate H1s). The
  SEO `<title>` and H1 may differ slightly (title optimized for SERP, H1 for
  the page), but must clearly be the same topic.

## 3. Meta description

Not a ranking factor; it is the **click-through** factor — Google bolds query
matches in it, and AI engines read it during retrieval as the page's
self-summary.

- **Width**: 120–160 Latin chars / ≈ 60–80 CJK chars. Under ~70 Latin chars wastes the slot; over gets truncated.
- Formula: *what the reader gets* + *what makes this page the right one* (+ soft CTA). Include the primary query once.
- Write it as the answer to "why click this instead of the other nine results?" — mention the concrete outcome, data, or experience inside.

**Example** (for the Docker post above):
> 通过多阶段构建、Alpine/Distroless 基础镜像和 .dockerignore，把生产镜像从 1.2GB 压到 180MB。附每一步的实测体积对比和踩坑记录。

## 4. URL slug

- Short (3–6 words), lowercase, hyphen-separated, ASCII.
- **CJK blogs**: never leave the slug as raw CJK or the platform's pinyin hash — set an explicit English/pinyin slug in frontmatter (`slug: docker-image-slimming`). CJK URLs become unreadable percent-encoding when shared, which kills link copying and looks broken in SERPs.
- Include the primary keyword's core noun; drop stopwords, dates, and category prefixes that may change.
- Never change slugs of already-published posts without a 301 redirect.

## 5. Answer-first opening

The first paragraph after the H1 is the most-extracted text on the page —
featured snippets, AI Overviews, and chat citations overwhelmingly pull from
it.

- **First 2–4 sentences directly answer the primary query.** A reader who stops there should have the correct short answer.
- Then a bridge sentence that sells reading on: what evidence, steps, or nuance the full article adds.
- 40–60 words (≈ 80–120 CJK chars) is the snippet sweet spot for the answer portion.
- Kill throat-clearing: "在当今数字化时代…", "As we all know…", "Before we dive in, let's briefly discuss the history of…" — engines skip it, readers bounce off it.
- A `> TL;DR` blockquote or a "结论先行" box is a valid alternative form, and doubles as the quotable chunk.

**Example transformation**

Before:
> 随着容器技术的普及，越来越多的团队开始使用 Docker。但是很多人发现镜像越来越大。本文将探讨一些优化方法。

After:
> Docker 镜像过大的主因是把构建环境打进了运行镜像。用多阶段构建剥离编译依赖、换用 Alpine 或 Distroless 基础镜像、再配好 .dockerignore，通常能把镜像压缩 80% 以上——我们的 Go 服务从 1.2GB 降到了 180MB。下面按收益从大到小给出 6 个步骤和每步的实测数据。

## 6. Heading structure

Headings are the retrieval index of the page — for skimmers, for Google's
passage ranking, and for the chunkers AI engines use.

- **Exactly one H1** (usually the rendered title). Body sections start at H2. No level skips (H2 → H4).
- Each H2 = one subtopic = one potential standalone answer. Prefer **question-form** ("为什么多阶段构建能减小镜像？") or **claim-form** ("Alpine 不总是最优选择") over label-form ("背景", "其他", "Introduction", "Miscellaneous").
- Put the query-cluster phrasings into H2s/H3s — each becomes independently findable.
- Parallel grammar across sibling headings (all questions, or all imperatives) — easier to scan, and pattern-consistent sections chunk cleaner.
- 2–6 headings per 1000 words. A 2000-word wall with one heading is invisible to passage retrieval.

## 7. Body: extractable, chunk-friendly writing

AI engines don't read your page top-to-bottom; they retrieve **chunks** (a
section, a list, a table) and cite the chunk. Format so any section can be
lifted out and still make sense.

- **Self-contained sections**: don't start a section with "如上所述" / "As mentioned above" — restate the noun ("多阶段构建的第二个好处是…"). Pronouns that point outside the chunk break it.
- **Lists for enumerations** (3+ parallel items), **tables for comparisons** (engines extract tables into answers verbatim), **numbered steps for processes** (with imperative verbs).
- **Definition sentences** for key terms: "Distroless 镜像是只包含应用及其运行时依赖、不含包管理器和 shell 的极简基础镜像。" The "X is Y" shape is what entity extraction and definition boxes feed on.
- **One idea per paragraph**, 2–4 sentences. Bold the load-bearing phrase of critical paragraphs — sparingly.
- **Quotable sentences**: each major section should contain one sentence that summarizes its point so well it could be quoted alone. Write it deliberately.
- Consistent terminology: pick one name per concept ("镜像" not alternating with "image"/"容器镜像" randomly) — entity consistency helps both rankings and LLM comprehension.
- Code blocks: always language-tagged; add a one-line comment saying what the snippet achieves (the comment is what gets retrieved).

## 8. Evidence density (the GEO lever)

The Princeton/IIT GEO study (Aggarwal et al., KDD 2024) found adding
**citations, quotations, and statistics** raised content's visibility in
generative-engine answers by 30–40% — the largest effect of any tested
optimization. Engines prefer citing pages that *look like sources*, i.e. pages
that themselves cite and quantify.

- **Surface the article's own numbers**: benchmarks, before/after, versions, dates, sample sizes. "很多" → "6 个服务、平均 78%". Firsthand data is the strongest material — nobody else has it, so engines *must* cite you for it.
- **Attribute external claims**: "According to the 2026 Stack Overflow survey…" / "据 Docker 官方文档…" with a link. The "According to…" pattern is a recognized citation shape.
- **Quote experts/docs** where a quote genuinely adds authority (blockquote + source).
- **NEVER invent any of this.** No fake benchmarks, no "studies show" without a study, no rounding personal guesses into statistics. If the article lacks evidence for a claim, either mark `TODO(author): 补充实测数据` or soften the claim. Fabrication is both wrong and — since engines increasingly cross-check — a visibility risk.

## 9. FAQ section

Directly targets People-Also-Ask, voice queries, and long-tail chat questions;
also the natural home for query-cluster phrasings that didn't earn a full
section.

- 3–5 questions, phrased exactly as people ask them (check: would someone type this into ChatGPT?).
- Each answer: **40–60 words (≈ 80–120 CJK chars), fully standalone** (restate the subject; no "同上").
- Real questions only — adjacent doubts, edge cases, comparisons ("Alpine 和 Distroless 怎么选？", "多阶段构建会让 CI 变慢吗？"). Not restatements of section headings already answered above.
- Heading: "常见问题" / "FAQ" as an H2, questions as H3s — this exact shape maps 1:1 onto FAQPage JSON-LD (see `structured-data.md`).

## 10. Images

- **Alt text on every content image**, in the article's language, describing what the image shows *in context* ("多阶段构建前后的镜像体积对比柱状图，1.2GB vs 180MB" — not "图片1", not keyword lists). Screen readers and image search both read it; AI engines use it to understand the page.
- Descriptive filenames (`docker-multistage-size-comparison.png`, not `WX20260722.png`).
- **Cover/OG image** set in frontmatter (`cover`/`image`). 1200×630 for social cards; this is the thumbnail everywhere the post is shared — posts with cards get dramatically more social click-through.
- Compress (WebP/AVIF where the platform supports it); explicit width/height attributes prevent CLS.
- Diagrams > stock photos. A diagram that explains the concept gets saved, embedded, and linked — stock art is noise.

## 11. Links

- **Internal, outgoing**: 2–5 contextual links to the author's related posts, with descriptive anchors ("参考我写的 [.dockerignore 完整指南]" — never "点这里"/"click here"). Internal links distribute authority and keep readers on-site; the anchor text tells engines what the target is about.
  - If you can see the user's other posts (repo/site available), find real link targets. If not, list suggested anchor points in the report for the user to fill.
- **Internal, incoming**: flag in the report — "add links *to* this post from [likely related posts]". New posts with zero inbound internal links are orphans and index slowly.
- **External**: 1–3 links to genuinely authoritative sources (official docs, standards, original studies). Outbound links to good sources are a trust signal, not a leak. Keep default follow (don't blanket-nofollow references).
  - No network access to verify? Canonical, stable URLs you're confident of (official docs landing pages, well-known project repos) may still be added — flag them "verify before publish" in the report. Never add deep links you can't verify, and never invent a URL.
- Check for broken links and missing referenced assets (images that 404) while you're in there.

## 12. Frontmatter completeness

Minimum viable frontmatter for an optimized post (adapt keys to the
platform's convention):

```yaml
title: "..."            # §2
description: "..."      # §3 — the meta description
slug: "ascii-slug"      # §4
date: 2026-07-20
lastmod: 2026-07-24     # real modification date — feeds sitemap <lastmod>
tags: [docker, devops]  # 3–6, reuse the site's existing tag vocabulary
cover: /img/....png     # §10 — OG/social card
author: "..."           # matches the site's author identity (E-E-A-T)
draft: false
```

Platform naming variants: `summary`/`excerpt` (description), `updated`
(lastmod), `image`/`banner`/`og_image` (cover), `keywords` (fine to fill;
minor signal), `categories` (one, broad). Match what the site's other posts
and theme actually use — an unrecognized key does nothing.

## 13. Freshness

- Meaningful update → bump `lastmod` AND note it visibly ("2026-07 更新：新增 BuildKit 缓存挂载一节"). Engines compare content hashes; date-bumping without changes is detected and discounted.
- Year in title only if the content is genuinely maintained ("2026 指南" that's stale is worse than no year).
- In the report, flag evergreen posts worth an update cycle — refreshed posts frequently regain rankings/citations at a fraction of new-post effort.

## 14. E-E-A-T signals inside the article

Engines (and Google's quality raters, and AI-engine source selection)
prefer content with a verifiable, experienced author behind it.

- Keep/add **firsthand markers**: "我们在生产环境跑了三个月", "in my testing on an M3 Max" — experience is the first E and cannot be faked by aggregator content.
- Byline present and consistent with the site's author page (`references/site-audit.md` covers author-page + `Person` schema setup).
- State the *scope of validity* honestly ("以下结论基于 Go 1.24 静态编译场景") — precision reads as expertise; overclaiming reads as content-farm.
- Disclose conflicts (affiliate links, sponsorships) — required by policy in many jurisdictions and a trust signal.

## 15. Anti-patterns

Each of these actively hurts (demotion, filtering out of AI training/retrieval,
or reader bounce):

- Keyword stuffing / unnatural exact-match repetition (write for the query *cluster*, not the string).
- Fabricated or unattributed statistics; fake "expert" quotes. (See §8 — this is the cardinal sin.)
- AI-boilerplate smell: "In today's fast-paced digital landscape…", "综上所述，...是一把双刃剑", symmetric fluff paragraphs that say nothing. Engines and readers both pattern-match this as low-value; one detected page lowers trust in the whole domain.
- Clickbait titles the content doesn't cash. Bounce = demotion.
- Walls of text (no headings/lists for 1000+ words) — unretrievable chunks.
- Doorway/near-duplicate posts targeting keyword variants — consolidate into one strong post instead.
- Auto-translated content published without human review.
- Date-bumping without changes; hidden text; white-on-white keywords (yes, still seen; yes, still penalized).
