# Structured Data (JSON-LD) Templates

Schema.org markup in JSON-LD form — the machine-readable layer that makes a
page's meaning unambiguous to search engines and answer engines. Google
explicitly recommends JSON-LD over microdata/RDFa.

**Rules that keep markup safe and effective:**

1. **Only mark up content visible on the page.** Invisible/extra markup violates Google's guidelines and can earn manual actions.
2. One `<script type="application/ld+json">` block can hold an array of objects, or use multiple blocks — both fine. Use `@graph` with `@id` cross-references for the cleanest setup (template below).
3. Validate after adding: paste the rendered HTML (not the template source) into https://search.google.com/test/rich-results and https://validator.schema.org.
4. Templates below use `{{placeholders}}` — fill from the site config / frontmatter. In static-site themes, these become template variables, written once in the theme and correct for every page.

## Which types matter for a blog (priority order)

| Type | Where | Why |
|---|---|---|
| `BlogPosting` | every post | Post metadata: author, dates, image — the baseline |
| `Person` (author) | site-wide + referenced from posts | E-E-A-T author entity; `sameAs` disambiguates you |
| `WebSite` | home page | Site identity (+ optional SearchAction for site search) |
| `FAQPage` | posts with FAQ sections | Maps FAQ to People-Also-Ask / rich results |
| `BreadcrumbList` | every post | SERP breadcrumb display, site structure clarity |
| `HowTo` | step-by-step tutorials | Rich results for how-to queries |
| `Organization` | if the blog is a company blog | Publisher entity |

## Combined per-post template (`BlogPosting` + author + breadcrumb)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "{{page_url}}#article",
      "headline": "{{title — max 110 chars}}",
      "description": "{{meta description}}",
      "image": "{{absolute cover image URL, ideally 1200x630}}",
      "datePublished": "{{2026-07-20T09:00:00+08:00}}",
      "dateModified": "{{2026-07-24T10:00:00+08:00}}",
      "inLanguage": "{{zh-CN | en-US | ...}}",
      "author": { "@id": "{{site_url}}/#author" },
      "publisher": { "@id": "{{site_url}}/#author" },
      "mainEntityOfPage": { "@type": "WebPage", "@id": "{{page_url}}" },
      "keywords": "{{tag1, tag2, tag3}}"
    },
    {
      "@type": "Person",
      "@id": "{{site_url}}/#author",
      "name": "{{author name — identical everywhere it appears}}",
      "url": "{{site_url}}/about/",
      "description": "{{one-line bio with the expertise area}}",
      "sameAs": [
        "https://github.com/{{username}}",
        "https://twitter.com/{{username}}",
        "https://www.linkedin.com/in/{{username}}"
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "{{page_url}}#breadcrumb",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "首页", "item": "{{site_url}}/" },
        { "@type": "ListItem", "position": 2, "name": "博客", "item": "{{site_url}}/posts/" },
        { "@type": "ListItem", "position": 3, "name": "{{title}}" }
      ]
    }
  ]
}
```

Notes:
- `dateModified` must track real content updates — it's cross-checked against sitemap `<lastmod>` and page content.
- `sameAs` is the author-entity disambiguator: link every profile that confirms identity/expertise (GitHub, X/Twitter, LinkedIn, Zhihu, StackOverflow, ORCID…). Consistent `name` + `sameAs` across the web is what builds the author entity engines can trust.
- Personal blog: author doubles as `publisher` (shown above). Company blog: separate `Organization` publisher with `logo`.

## FAQPage (only when the page shows a FAQ)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{{question exactly as it appears on the page}}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{answer text — plain text or simple HTML, matching the visible answer}}"
      }
    }
  ]
}
```

- 3–5 questions; text must match the visible FAQ (rule 1).
- Google now shows FAQ rich results mainly for authoritative sites, but the markup still helps AI engines parse Q→A pairs regardless of rich-result display.

## HowTo (step-by-step tutorials)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{{goal, e.g. 把 Docker 镜像从 1.2GB 压缩到 200MB 以内}}",
  "totalTime": "PT30M",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "{{step heading}}",
      "text": "{{what to do, standalone}}",
      "url": "{{page_url}}#{{step-anchor}}"
    }
  ]
}
```

Use when the article's core is a numbered procedure. Step `name`s should match
the H2/H3s; anchor URLs let engines deep-link a single step.

## WebSite (home page, once)

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "{{site_url}}/#website",
  "name": "{{site name}}",
  "url": "{{site_url}}/",
  "description": "{{site tagline}}",
  "inLanguage": "{{zh-CN}}",
  "publisher": { "@id": "{{site_url}}/#author" }
}
```

## Where to put it, per platform

- **Hugo**: partial in `layouts/partials/` (e.g. `schema.html`), included from `head.html` / `baseof.html`. Many themes ship one — check `jsonld`/`schema`/`structured` in the theme before writing your own; prefer fixing the theme's data flow (params) over duplicating.
- **Hexo**: theme's `head.ejs`/`head.swig`, or `hexo-helper-live2d`-style injector plugins; simplest is editing the theme partial.
- **Jekyll**: `_includes/head.html`; the `jekyll-seo-tag` plugin already emits `BlogPosting` + `WebSite` — enable it and configure `_config.yml` (author, social) instead of hand-writing.
- **Astro**: a `<SchemaOrg>` component (or `astro-seo-schema`) in the base layout, fed from frontmatter via `Astro.props`.
- **Next.js**: render `<script type="application/ld+json" dangerouslySetInnerHTML={{__html: JSON.stringify(jsonLd)}} />` in the page/layout (App Router: in the page component; also set the `metadata` export for title/description/OG).
- **VitePress/Docusaurus**: head config in the site config, or a theme slot component.
- **WordPress**: Yoast/RankMath already emit a full graph — configure, don't duplicate.

**Verify what already exists first** (`grep -r "application/ld+json" layouts/ themes/ src/`): duplicate conflicting graphs are worse than one imperfect graph.

## Beyond schema: the rest of `<head>`

While editing head templates, ensure these coexist with JSON-LD (details in
`site-audit.md`):

```html
<title>{{page title}} · {{site name}}</title>
<meta name="description" content="{{description}}">
<link rel="canonical" href="{{page_url}}">
<meta property="og:type" content="article">
<meta property="og:title" content="{{title}}">
<meta property="og:description" content="{{description}}">
<meta property="og:image" content="{{absolute cover URL}}">
<meta property="og:url" content="{{page_url}}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" href="{{site_url}}/index.xml">
```
