#!/usr/bin/env python3
"""seo_check.py — deterministic SEO/GEO/AEO checker for blog articles.

Checks markdown (.md/.mdx, YAML/TOML frontmatter) or basic HTML articles
against mechanical on-page rules and prints a scored report. CJK-aware:
lengths are measured in display-width units (CJK char = 2, Latin = 1),
matching how SERPs truncate.

Usage:
  python3 seo_check.py article.md [--keyword "primary query"]
  python3 seo_check.py content/posts/          # batch mode, summary table
  python3 seo_check.py content/ --json         # machine-readable output
  python3 seo_check.py article.md --min-score 80   # exit 1 below threshold

Read-only: never modifies files. Stdlib only (uses PyYAML/tomllib if present).
"""

import argparse
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------- utilities

def display_width(text):
    """SERP-style width: CJK/fullwidth chars count 2, others 1."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1
               for c in text)


def is_cjk_text(text):
    cjk = len(re.findall(r"[一-鿿぀-ヿ가-힯]", text))
    return cjk > max(10, len(text) * 0.1)


def word_count(text):
    """CJK chars count as one word each; Latin words normally."""
    cjk = len(re.findall(r"[一-鿿぀-ヿ가-힯]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))
    return cjk + latin

# ------------------------------------------------------- frontmatter parsing

def _naive_yaml(block):
    """Fallback YAML-ish parser: flat keys, inline/dash lists, quoted strings."""
    data, cur_key = {}, None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^(\w[\w.-]*)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            cur_key = key
            if not val:
                data[key] = []
            elif val.startswith("[") and val.endswith("]"):
                items = [v.strip().strip("'\"") for v in val[1:-1].split(",")]
                data[key] = [v for v in items if v]
            else:
                data[key] = val.strip("'\"")
        elif re.match(r"^\s+-\s+", line) and cur_key is not None:
            if isinstance(data.get(cur_key), list):
                data[cur_key].append(line.split("-", 1)[1].strip().strip("'\""))
    return data


def parse_frontmatter(text):
    """Return (frontmatter_dict, body, kind) for YAML(---)/TOML(+++) blocks."""
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if m:
        block, body = m.group(1), text[m.end():]
        try:
            import yaml  # type: ignore
            data = yaml.safe_load(block) or {}
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = _naive_yaml(block)
        return data, body, "yaml"
    m = re.match(r"\A\+\+\+\s*\n(.*?)\n\+\+\+\s*\n?", text, re.DOTALL)
    if m:
        block, body = m.group(1), text[m.end():]
        try:
            import tomllib
            data = tomllib.loads(block)
        except Exception:
            data = _naive_yaml(block.replace(" = ", ": "))
        return data, body, "toml"
    return {}, text, None


def fm_get(fm, *keys):
    """First present frontmatter value among alias keys (case-insensitive)."""
    lower = {str(k).lower(): v for k, v in fm.items()}
    for k in keys:
        if k in lower and lower[k] not in (None, "", []):
            return lower[k]
    return None

# ------------------------------------------------------------ article model

FLUFF_PATTERNS = re.compile(
    r"^(在当今|在这个|随着.{0,12}(发展|普及|兴起)|众所周知|近年来|如今|"
    r"In today'?s|As we all know|In the ever[- ]|In this (fast|rapidly)|"
    r"In the (digital|modern) (age|era|world))", re.IGNORECASE)

QUESTION_HEAD = re.compile(
    r"([?？]$|^(为什么|如何|怎么|怎样|什么是|哪个|哪些|何时|要不要|该不该|"
    r"why|how|what|when|which|where|should|can|does|do|is|are)\b)",
    re.IGNORECASE)

FAQ_HEAD = re.compile(r"(FAQ|常见问题|问答|Q\s*&\s*A|Frequently Asked)",
                      re.IGNORECASE)

EVIDENCE_RES = [
    re.compile(r"\d+(?:\.\d+)?\s*(?:%|％|倍|万|亿|GB|MB|KB|TB|ms|s\b|秒|分钟|"
               r"小时|天|percent|x\b|times)", re.IGNORECASE),
    re.compile(r"(according to|据\s|来源[:：]|source[:：]|参考[:：]|"
               r"research (?:by|from|shows)|study|survey|报告|调查|数据显示|"
               r"官方文档|benchmark)", re.IGNORECASE),
]


class Article:
    def __init__(self, path, text):
        self.path = path
        self.fm, body, self.fm_kind = parse_frontmatter(text)
        self.raw_body = body
        # Strip code fences for text analysis (keep a copy with them).
        self.body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
        self.body = re.sub(r"~~~.*?~~~", "", self.body, flags=re.DOTALL)
        self.headings = [(len(m.group(1)), m.group(2).strip())
                         for m in re.finditer(r"^(#{1,6})\s+(.+)$",
                                              self.body, re.MULTILINE)]
        self.md_images = re.findall(r"!\[([^\]]*)\]\(([^)\s]+)[^)]*\)", self.body)
        self.html_images = [(m.group(1) or "", "")
                            for m in re.finditer(
                                r"<img\b(?:[^>]*?alt=[\"']([^\"']*)[\"'])?[^>]*>",
                                self.body)]
        links = re.findall(r"(?<!\!)\[([^\]]+)\]\(([^)\s]+)[^)]*\)", self.body)
        self.internal_links = [(t, u) for t, u in links
                               if not re.match(r"^[a-z]+://", u)
                               and not u.startswith("#")]
        self.external_links = [(t, u) for t, u in links
                               if re.match(r"^https?://", u)]
        self.title = fm_get(self.fm, "title") or next(
            (t for lvl, t in self.headings if lvl == 1), None)
        self.description = fm_get(self.fm, "description", "summary",
                                  "excerpt", "desc", "subtitle")
        self.words = word_count(self.body)
        self.is_cjk = is_cjk_text(self.body)

    def first_chunk(self):
        """Body text before the first H2+ heading (minus an H1 line)."""
        m = re.search(r"^#{2,6}\s", self.body, re.MULTILINE)
        chunk = self.body[:m.start()] if m else self.body
        chunk = re.sub(r"^#\s+.+$", "", chunk, flags=re.MULTILINE)
        return chunk.strip()

# ------------------------------------------------------------------- checks

class Result:
    def __init__(self, cid, status, message, suggestion="", weight=1.0):
        self.id, self.status, self.message = cid, status, message
        self.suggestion, self.weight = suggestion, weight

    def as_dict(self):
        d = {"id": self.id, "status": self.status, "message": self.message}
        if self.suggestion:
            d["suggestion"] = self.suggestion
        return d


def check_article(art, keyword=None):
    R = []
    add = lambda *a, **k: R.append(Result(*a, **k))
    cjk = art.is_cjk

    # --- title
    if not art.title:
        add("title-present", "fail", "No title (frontmatter or H1)",
            "Add a frontmatter title front-loading the primary query", 2)
    else:
        add("title-present", "pass", f"Title: {art.title!r}", weight=2)
        w = display_width(art.title)
        lim = "≈30 CJK chars" if cjk else "60 chars"
        if w > 75:
            add("title-width", "fail",
                f"Title width {w} units — will truncate badly (limit ~60 / {lim})",
                "Shorten; keep the primary query in the front", 1.5)
        elif w > 60:
            add("title-width", "warn",
                f"Title width {w} units — tail will truncate in SERPs (~60 / {lim})",
                "Trim decorations; front-load the key phrase", 1.5)
        elif w < 15:
            add("title-width", "warn",
                f"Title width {w} units — too generic/short to differentiate",
                "Add a concrete differentiator: number, year, outcome", 1.5)
        else:
            add("title-width", "pass", f"Title width {w} units", weight=1.5)

    # --- description
    if not art.description:
        add("desc-present", "fail", "No meta description in frontmatter",
            "Add description: what the reader gets + why this page "
            "(120–160 chars, ≈60–80 CJK)", 2)
    else:
        w = display_width(str(art.description))
        add("desc-present", "pass", "Description present", weight=2)
        if w < 100:
            add("desc-width", "warn",
                f"Description width {w} units — slot underused (target 110–165)",
                "Expand with the concrete outcome/data inside the post", 1)
        elif w > 175:
            add("desc-width", "warn",
                f"Description width {w} units — will truncate (target 110–165)",
                "Tighten to one or two crisp sentences", 1)
        else:
            add("desc-width", "pass", f"Description width {w} units", weight=1)

    # --- slug
    slug = fm_get(art.fm, "slug", "permalink")
    base = os.path.splitext(os.path.basename(art.path))[0]
    eff = str(slug) if slug else base
    if re.search(r"[^\x00-\x7f]", eff):
        add("slug-ascii", "warn", f"Slug/filename {eff!r} is non-ASCII",
            "Set an explicit short hyphenated ASCII slug "
            "(CJK URLs become unreadable percent-encoding)", 1)
    elif re.search(r"[\s_A-Z]", eff):
        add("slug-ascii", "warn", f"Slug {eff!r} has spaces/underscores/uppercase",
            "Use lowercase-hyphenated form", 0.5)
    else:
        add("slug-ascii", "pass", f"Slug OK: {eff!r}", weight=1)

    # --- headings
    h1s = [t for lvl, t in art.headings if lvl == 1]
    fm_title = fm_get(art.fm, "title")
    if fm_title and h1s:
        add("h1-single", "warn",
            "Frontmatter title AND in-body H1 — most themes render both (duplicate H1)",
            "Drop the in-body '# ...' line or demote to H2", 1)
    elif len(h1s) > 1:
        add("h1-single", "fail", f"{len(h1s)} H1 headings",
            "Exactly one H1; demote the rest", 1)
    elif not fm_title and not h1s:
        add("h1-single", "warn", "No H1 anywhere", "Add one", 1)
    else:
        add("h1-single", "pass", "Single H1", weight=1)

    lvls = [lvl for lvl, _ in art.headings if lvl >= 2]
    skips = [f"H{a}->H{b}" for a, b in zip(lvls, lvls[1:]) if b - a > 1]
    if any(b - a > 1 for a, b in zip(lvls, lvls[1:])):
        add("heading-hierarchy", "warn",
            f"Heading level skips: {', '.join(skips[:3])}",
            "Don't skip levels (H2 → H3 → H4)", 0.5)
    else:
        add("heading-hierarchy", "pass", "No heading level skips", weight=0.5)

    subheads = [t for lvl, t in art.headings if lvl >= 2]
    needed = 3 if art.words >= 1000 else 2 if art.words >= 500 else 0
    if len(subheads) < needed:
        add("headings-density", "warn",
            f"{art.words} words but only {len(subheads)} subheadings",
            "Add an H2 per subtopic (2–6 per 1000 words) — walls of text "
            "can't be retrieved as chunks", 1)
    else:
        add("headings-density", "pass",
            f"{len(subheads)} subheadings / {art.words} words", weight=1)

    nq = sum(1 for t in subheads if QUESTION_HEAD.search(t.strip()))
    add("question-headings", "pass" if nq else "warn",
        f"{nq} question-form headings",
        "" if nq else "Phrase 1–3 H2s as the questions people actually ask "
        "(AEO: each maps to a People-Also-Ask style query)", 0.5)

    # --- intro
    chunk = art.first_chunk()
    cw = word_count(chunk)
    if cw > 250:
        add("answer-first", "warn",
            f"{cw} words before the first H2 — long unstructured intro",
            "Open with a 2–4 sentence direct answer, then break into sections", 1)
    elif cw == 0:
        add("answer-first", "warn", "No intro text before the first heading",
            "Add an answer-first opening paragraph — it's what snippets and "
            "AI answers extract", 1)
    else:
        add("answer-first", "pass", f"Intro is {cw} words", weight=1)
    first_line = next((l for l in chunk.splitlines() if l.strip()), "")
    if FLUFF_PATTERNS.search(first_line.strip()):
        add("intro-fluff", "warn",
            f"Intro starts with boilerplate: {first_line.strip()[:40]!r}...",
            "Delete throat-clearing; answer the query in sentence one", 1)
    else:
        add("intro-fluff", "pass", "Intro starts directly", weight=1)

    # --- images
    images = art.md_images + art.html_images
    if images:
        noalt = sum(1 for alt, _ in images if not alt.strip())
        if noalt:
            add("images-alt", "fail",
                f"{noalt}/{len(images)} images missing alt text",
                "Describe what each image shows, in the article's language", 1.5)
        else:
            add("images-alt", "pass",
                f"All {len(images)} images have alt text", weight=1.5)
    else:
        add("images-alt", "pass", "No images (nothing to check)", weight=0)
    if fm_get(art.fm, "cover", "image", "banner", "og_image", "feature",
              "thumbnail", "featured_image", "featureimage"):
        add("cover-image", "pass", "Cover/OG image set", weight=1)
    else:
        add("cover-image", "warn", "No cover/OG image in frontmatter",
            "Set one (1200×630) — it's the card shown on every share", 1)

    # --- links
    ni, ne = len(art.internal_links), len(art.external_links)
    if ni >= 2:
        add("internal-links", "pass", f"{ni} internal links", weight=1.5)
    else:
        add("internal-links", "warn", f"Only {ni} internal link(s)",
            "Link 2–5 related posts with descriptive anchors; ask the author "
            "for targets if the site isn't available", 1.5)
    add("external-links", "pass" if ne else "warn",
        f"{ne} external links",
        "" if ne else "Cite 1–3 authoritative sources (official docs, "
        "studies) — outbound citations are a trust signal", 0.5)

    # --- body volume
    if art.words < 300:
        add("word-count", "fail", f"Only {art.words} words — thin content",
            "Expand with real substance or merge into a stronger post", 1.5)
    elif art.words < 600:
        add("word-count", "warn", f"{art.words} words — on the thin side",
            "Consider adding examples, data, or an FAQ", 1.5)
    else:
        add("word-count", "pass", f"{art.words} words", weight=1.5)

    # --- FAQ
    if any(FAQ_HEAD.search(t) for _, t in art.headings):
        add("faq-present", "pass", "FAQ section present", weight=1)
    else:
        add("faq-present", "warn", "No FAQ section",
            "Add 3–5 real adjacent questions, 40–60 word standalone answers "
            "(targets People-Also-Ask and chat-style queries)", 1)

    # --- evidence density (GEO)
    ev = sum(len(rx.findall(art.body)) for rx in EVIDENCE_RES)
    ev += len(re.findall(r"^>\s+", art.body, re.MULTILINE)) // 2
    if ev >= 5:
        add("evidence-density", "pass", f"Evidence signals: {ev} "
            "(numbers/units, attributions, quotes)", weight=1.5)
    elif ev >= 1:
        add("evidence-density", "warn", f"Evidence signals: only {ev}",
            "Surface the article's own numbers and attribute claims "
            "('according to …'). NEVER invent data — flag TODO(author) "
            "if data is missing", 1.5)
    else:
        add("evidence-density", "warn", "No quantified/attributed evidence found",
            "The strongest GEO lever: real numbers, benchmarks, cited sources", 1.5)

    # --- dates & tags
    add("date-present", "pass" if fm_get(art.fm, "date", "publishdate",
        "published", "created") else "warn",
        "Publish date present" if fm_get(art.fm, "date", "publishdate",
        "published", "created") else "No publish date in frontmatter",
        "", 0.5)
    if fm_get(art.fm, "lastmod", "updated", "modified", "last_modified_at"):
        add("lastmod-present", "pass", "lastmod/updated present", weight=0.5)
    else:
        add("lastmod-present", "warn", "No lastmod/updated field",
            "Feeds sitemap <lastmod>; set it on real updates", 0.5)
    tags = fm_get(art.fm, "tags", "keywords")
    if tags and isinstance(tags, (list, str)):
        n = len(tags) if isinstance(tags, list) else len(str(tags).split(","))
        if n > 8:
            add("tags-present", "warn", f"{n} tags — tag spam dilutes",
                "3–6 tags from the site's existing vocabulary", 0.5)
        else:
            add("tags-present", "pass", f"{n} tag(s)", weight=0.5)
    else:
        add("tags-present", "warn", "No tags/keywords",
            "Add 3–6 from the site's existing tag vocabulary", 0.5)

    # --- keyword placement
    if keyword:
        key = keyword.lower()
        spots = {
            "title": (art.title or "").lower(),
            "description": str(art.description or "").lower(),
            "intro": chunk.lower()[:600],
            "headings": " ".join(t.lower() for t in subheads),
        }
        missing = [k for k, v in spots.items() if key not in v]
        if not missing:
            add("keyword-placement", "pass",
                f"Keyword {keyword!r} present in title/description/intro/headings",
                weight=1.5)
        else:
            add("keyword-placement", "warn",
                f"Keyword {keyword!r} missing from: {', '.join(missing)}",
                "Place it once, naturally, in each location", 1.5)

    return R


def score(results):
    total = sum(r.weight for r in results if r.weight > 0)
    if not total:
        return 100
    got = sum(r.weight if r.status == "pass" else
              r.weight * 0.5 if r.status == "warn" else 0
              for r in results if r.weight > 0)
    return round(100 * got / total)

# ----------------------------------------------------------------- html mode

def html_to_pseudo_md(text):
    """Rough HTML → analyzable pseudo-article (best effort)."""
    fm = {}
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    if m:
        fm["title"] = re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content='
                  r'["\']([^"\']*)["\']', text, re.I)
    if m:
        fm["description"] = m.group(1)
    body = text
    for lvl in range(1, 7):
        body = re.sub(r"<h%d[^>]*>(.*?)</h%d>" % (lvl, lvl),
                      lambda mm, l=lvl: "\n" + "#" * l + " " +
                      re.sub(r"<[^>]+>", "", mm.group(1)).strip() + "\n",
                      body, flags=re.I | re.S)
    body = re.sub(r"<a\s[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
                  lambda mm: "[%s](%s)" % (
                      re.sub(r"<[^>]+>", "", mm.group(2)).strip() or "link",
                      mm.group(1)), body, flags=re.I | re.S)
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", body,
                  flags=re.I | re.S)
    kept_imgs = re.findall(r"<img[^>]*>", body, flags=re.I)
    body = re.sub(r"<(?!img)[^>]+>", " ", body)
    lines = ["---"] + ["%s: %s" % (k, v.replace("\n", " ")) for k, v in fm.items()] + ["---", body]
    return "\n".join(lines) + "\n" + "\n".join(kept_imgs)

# ---------------------------------------------------------------------- main

MARKS = {"pass": "✓", "warn": "⚠", "fail": "✗"}


def analyze_file(path, keyword=None):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    if path.lower().endswith((".html", ".htm")):
        text = html_to_pseudo_md(text)
    art = Article(path, text)
    results = check_article(art, keyword)
    return {
        "path": path,
        "title": art.title,
        "score": score(results),
        "words": art.words,
        "cjk": art.is_cjk,
        "internal_links": [u for _, u in art.internal_links],
        "checks": [r.as_dict() for r in results],
    }


def collect_files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith((".", "node_modules"))]
                out += [os.path.join(root, f) for f in sorted(files)
                        if f.lower().endswith((".md", ".mdx", ".markdown"))]
        elif os.path.isfile(p):
            out.append(p)
        else:
            print(f"seo_check: not found: {p}", file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", help="article file(s) or content dir")
    ap.add_argument("--keyword", help="primary query to verify placement of")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--min-score", type=int, default=None,
                    help="exit 1 if any file scores below this")
    args = ap.parse_args()

    files = collect_files(args.paths)
    if not files:
        print("seo_check: no markdown files found", file=sys.stderr)
        sys.exit(2)

    reports = []
    for f in files:
        try:
            reports.append(analyze_file(f, args.keyword))
        except Exception as e:  # never die mid-batch
            reports.append({"path": f, "score": 0, "error": str(e), "checks": []})

    if args.as_json:
        avg = round(sum(r["score"] for r in reports) / len(reports))
        print(json.dumps({"files": reports, "summary": {
            "count": len(reports), "avg_score": avg}},
            ensure_ascii=False, indent=2))
    elif len(reports) == 1:
        r = reports[0]
        print(f"\n=== {r['path']} — score {r['score']}/100 ===\n")
        for c in r["checks"]:
            print(f" {MARKS.get(c['status'], '?')} [{c['status']:4}] {c['message']}")
            if c.get("suggestion"):
                print(f"      → {c['suggestion']}")
        print(f"\n Score: {r['score']}/100  "
              "(pass=full, warn=half, fail=0 credit, weighted)")
    else:
        print(f"\n{'score':>5}  {'fails':>5}  {'warns':>5}  path / top issues")
        for r in sorted(reports, key=lambda x: x["score"]):
            fails = [c for c in r["checks"] if c["status"] == "fail"]
            warns = [c for c in r["checks"] if c["status"] == "warn"]
            print(f"{r['score']:>5}  {len(fails):>5}  {len(warns):>5}  {r['path']}")
            for c in (fails + warns)[:3]:
                print(f"{'':19}- {c['message']}")
        avg = round(sum(r["score"] for r in reports) / len(reports))
        print(f"\n {len(reports)} files, average score {avg}/100")

    if args.min_score is not None and any(
            r["score"] < args.min_score for r in reports):
        sys.exit(1)


if __name__ == "__main__":
    main()
