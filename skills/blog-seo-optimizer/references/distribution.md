# Distribution & Exposure Playbook (Off-Site)

On-page work makes content *citable*; distribution makes it *found*. This file
covers everything beyond the site itself: getting indexed fast, showing up in
AI answers, syndication, communities, backlinks, and the Chinese ecosystem.
Use it for Workflow C (exposure strategy) and for the closing recommendations
of Workflows A/B.

When producing a plan, pick the 3–5 items with the best effort/return for
*this* user — don't dump the whole file on them.

## Contents

1. [Get indexed (the plumbing)](#1-get-indexed)
2. [Where AI engines actually get content](#2-where-ai-engines-actually-get-content)
3. [Syndication with canonical](#3-syndication-with-canonical)
4. [Communities & aggregators](#4-communities--aggregators)
5. [Earning links & entity presence](#5-earning-links--entity-presence)
6. [Social & the moment of publishing](#6-social--the-moment-of-publishing)
7. [Chinese ecosystem specifics](#7-chinese-ecosystem-specifics)
8. [Measurement loop](#8-measurement-loop)

---

## 1. Get indexed

Unindexed = invisible, regardless of quality. New/small blogs wait weeks for
organic discovery; these cut it to hours/days:

- **Google Search Console**: verify the site (DNS or meta tag), submit sitemap.xml. For important new/updated posts, use *URL Inspection → Request Indexing* (manual, per-URL, but works within hours). Note: Google's Indexing API is restricted to job postings/broadcast events — Request Indexing is the legit path for blogs.
- **Bing Webmaster Tools**: one-click *import from Search Console*. Disproportionately valuable: Bing's index feeds **ChatGPT search and Copilot** (§2), and almost no small blogs bother — less competition.
- **IndexNow** (Bing/Yandex/Naver/Seznam — *not* Google): push-on-publish protocol. Set up once: host a key file, ping `https://api.indexnow.org/indexnow?url=...&key=...` on each publish. Integrations: Hugo/CI step (one `curl` in the deploy workflow), Next.js route handler, WordPress plugin. Near-instant Bing indexing.
- **Ping by architecture**: RSS feed listed in the head (aggregators poll it), sitemap `lastmod` accurate (recrawl scheduling).
- Verify indexation later: `site:yourdomain.com` in Google/Bing; Search Console *Pages* report for exclusions (crawled-not-indexed usually = thin/duplicate content, fix quality not plumbing).

## 2. Where AI engines actually get content

Optimize channels by knowing whose index feeds whom (2026):

| Answer engine | Content source | Practical action |
|---|---|---|
| ChatGPT (search mode) | **Bing index** + OAI-SearchBot crawl | be in Bing (§1), allow OAI-SearchBot |
| Microsoft Copilot | Bing index | same |
| Google AI Overviews / AI Mode / Gemini grounding | **Google index** (Googlebot) | normal Google SEO; no separate opt-in |
| Perplexity | own index (PerplexityBot) + partners | allow PerplexityBot; Reddit/community presence helps (it cites forums heavily) |
| Claude (web search) | search-partner results + Claude-SearchBot/Claude-User fetch | allow the Claude bots |
| DeepSeek / 豆包 / Kimi / 元宝 (Chinese) | mixed: Bing/搜狗/自建 + 百度生态 | Bing + Chinese platforms (§7) |

Implications:

- **Bing matters far more than its market share** — it's the retrieval layer for ChatGPT + Copilot. The 10 minutes to set up Bing Webmaster + IndexNow may be the best-value action in this whole file.
- AI engines cite **community threads and comparison/list pages** at high rates (Reddit is among the most-cited domains in English答案; 知乎 plays the analogous role in Chinese). Being *mentioned* in such threads earns citations your own domain wouldn't get yet (§4).
- The citation gap is real: ~28% of pages ChatGPT cites most have near-zero Google visibility — AI citation is a parallel game a small blog can win early by being the clearest, best-evidenced source on a narrow topic.

## 3. Syndication with canonical

Republishing on platform sites borrows their domain authority and audience
while (done right) crediting your blog as the origin.

**The one rule: your blog publishes first, the copy points back.**

- Platforms with proper canonical support: **Medium** (import tool sets `rel=canonical`), **dev.to** (`canonical_url` frontmatter), **Hashnode** (originalArticleURL). Set it, verify in the copy's page source.
- Platforms without real canonical (知乎/掘金/CSDN/SegmentFault…): open with "本文首发于 [博客链接]" and link specific related posts inline. Weaker signal, still worthwhile for reach + branded search (§7).
- Delay syndication ~3–7 days after publishing so the origin gets indexed first (prevents the copy outranking the original).
- Don't syndicate everything — the 20% best posts, adapted (platform-native intro, maybe shortened, ending with "full version + updates on my blog").

## 4. Communities & aggregators

The high-variance, high-ceiling channel: one well-received thread can beat a
year of organic growth, and community threads themselves get cited by AI
engines (§2).

- Where (match the content): Hacker News (Show HN for tools, technical war stories), relevant subreddits, lobste.rs, dev.to, V2EX, 知乎话题, Discord/Slack/微信群 of the niche.
- **The etiquette that works**: participate genuinely before/beyond posting your own links; write a platform-native summary (not bare link-drop) — post the核心结论 as text and link for depth; answer every comment in the first hours (engagement drives ranking everywhere); never astroturf or multi-account.
- Answer questions where your post *is* the answer: Stack Overflow (link as reference, answer must stand alone), Reddit/知乎 questions matching your query cluster. These live for years and get retrieved by AI engines.
- Blog aggregators/directories still work for niches: 独立博客导航/BlogFinder/十年之约-style lists (Chinese indie-blog webrings), planet-style feeds, newsletter curators (submit your best piece to the 2–3 newsletters of your niche — one inclusion = thousands of targeted readers + a quality backlink).

## 5. Earning links & entity presence

Backlinks remain the strongest domain-level ranking input, and *brand/entity
mentions* increasingly drive AI-answer inclusion. You earn both with
**linkable assets** — content whose format attracts references:

- Original data/benchmarks ("we measured X across N…") — the single most linkable format, and the most AI-cited.
- Free tools/calculators/checklists; comprehensive glossaries; annually-updated "state of X" pages; canonical comparison tables.
- Every strong external mention of your name/blog + link = one more confirmation of the author entity (pair with `Person`/`sameAs` markup, `structured-data.md`).
- Guest posts on established niche blogs (bio link + entity mention); podcast/interview appearances (show notes link).
- Skip: link farms, paid link schemes, mass directory spam — penalty risk, zero durable value.

## 6. Social & the moment of publishing

Social links are mostly nofollow — the value is *initial velocity*: early
readers → engagement signals → aggregator/algorithm pickup → the people who
*can* link/cite see it.

- Publish checklist (make it a habit, ~15 min): verify OG card renders (platform debuggers / opengraph.xyz) → post native-format threads/摘要 to your 1–2 active networks (X/LinkedIn/即刻/朋友圈) → send to newsletter/RSS subscribers → drop in 1–2 relevant communities (§4 etiquette) → Search Console Request Indexing (§1).
- Build the owned channel: an email list/newsletter is the only audience no algorithm can take away; add a low-friction subscribe (RSS + email) to every post footer.
- Repurpose the answer-first blocks: the TL;DR you wrote (article-checklist §5) is the social post; the FAQ items are individual posts/threads.

## 7. Chinese ecosystem specifics

For Chinese-language blogs, Google/Bing best practices above apply unchanged
(and cover 出海/海外华人 readers + most AI engines), plus:

- **百度**: verify at 百度搜索资源平台 (ziyuan.baidu.com); use 普通收录/API 推送 to submit URLs (sitemap alone is slow). Realities to set expectations with: 百度 strongly prefers established/备案 domains; independent blogs on GitHub Pages historically index poorly (Baiduspider has been blocked/throttled there — host on Vercel/Cloudflare/国内主机 if 百度流量矩阵 matters); HTTPS + mobile-friendly are hard requirements. If the user's audience is developers, note honestly: Chinese devs increasingly search via Bing/Google/AI 引擎, so 百度 effort is optional, not foundational.
- **微信生态**: 公众号 is a parallel distribution channel (its content is siloed from web search but feeds 微信搜一搜). Republish there with 阅读原文 → blog. 搜一搜 has its own SEO: title keyword + 原创标记 + 合集/标签.
- **知乎**: answer existing questions in your query cluster with genuinely complete answers, linking the blog for depth; 知乎专栏 for republishing (§3). 知乎 content ranks well in both Baidu *and* Bing/Google for Chinese queries, and is heavily retrieved by Chinese AI engines — it's the Chinese Reddit in the §2 sense.
- **掘金/SegmentFault/少数派/CSDN**: developer syndication targets, "首发于" convention (§3). 少数派 Matrix 投稿 = editorial amplification if accepted.
- 中文 AI 引擎 (Kimi/豆包/DeepSeek/元宝): retrieval leans on Bing-中国 + 搜狗(微信/知乎 content) + 百度 — covered by doing Bing + 知乎/公众号 above.
- Typography/quality signals: proper 全角标点, 中英文之间留空格 (盘古之白), consistent terminology — quality proxies both readers and 平台编辑 use.

## 8. Measurement loop

Optimize what you measure; review monthly (calendar reminder or a recurring
task):

- **Search Console + Bing Webmaster**: impressions, CTR, average position by page & query. CTR low + position decent → rewrite title/description (article-checklist §2–3). Impressions growing + position 8–15 → strengthen that post (evidence, internal links) to break into top 5.
- **AI-answer presence** (manual, 10 min): ask ChatGPT/Perplexity/Claude/豆包 your top 5 target queries; record whether you're cited. Perplexity shows sources explicitly — easiest tracker. Rising tools (Ahrefs Brand Radar, Otterly-style AI-visibility trackers) automate this if the user wants tooling.
- **Server logs / CDN analytics**: hits from `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot` = you're in the pipelines (and confirms they're not being 403'd, site-audit §3).
- Referral analytics: which communities/syndication copies actually send readers → double down there.
- Attribute honestly: rankings move in weeks, not days; AI-citation changes lag content changes by re-crawl cycles. Change → wait a crawl cycle → measure → iterate.
