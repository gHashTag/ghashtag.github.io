#!/usr/bin/env python3
"""Render one blog post as a standalone page, the way the other 30 are.

This site publishes each post TWICE: once inside the SPA bundle, and once as a
self-contained HTML page under blog/<slug>/ (and ru/blog/<slug>/). The second
one is what a link preview, a search crawler and a reader with no JavaScript
actually get, so a post that exists only in the SPA is half published.

Source of truth is the trinity repository's blog data -- index.ts for the
metadata and bodies/<slug>.ts for the blocks -- so the two lineages cannot
drift on wording.

    tools/make_post_page.py --trinity <path> --slug <slug> [--out .]

INLINE MARKUP is rendered here, not shown. The published pages leaked
`**bold**` and `` `code` `` to readers on 13 of 30 pages; the SPA had the same
defect and was fixed in trinity#864. A `code` BLOCK keeps its delimiters,
because one post quotes tool output that literally contains asterisks.
"""
import argparse
import html
import json
import pathlib
import re
import sys

INLINE = re.compile(r"\*\*([^*]+)\*\*|`([^`]+)`")


def inline(text: str) -> str:
    """Escape, then render the two markup forms the corpus actually uses.

    Bold RECURSES. One Russian paragraph reads
    `**нет ни одного воркфлоу, который запускает `zig build`**` -- a code span
    inside a bold span. A flat pass matches the bold first, `[^*]+` swallows
    the backticks, and the reader gets `<strong>... `zig build`</strong>` with
    the delimiters showing. Found on 1 page of 62, and only because the sweep
    covered both locales; an English-only sweep reports clean.
    """
    out, last = [], 0
    for m in INLINE.finditer(text):
        out.append(html.escape(text[last:m.start()], quote=False))
        if m.group(1) is not None:
            out.append(f"<strong>{inline(m.group(1))}</strong>")
        else:
            out.append(f"<code>{html.escape(m.group(2), quote=False)}</code>")
        last = m.end()
    out.append(html.escape(text[last:], quote=False))
    return "".join(out)


def load_blocks(trinity: pathlib.Path, slug: str, ru: bool):
    """The `body` / `ruBody` array out of bodies/<slug>.ts, as data."""
    p = trinity / "apps/website/src/data/blog/bodies" / f"{slug}.ts"
    src = p.read_text()
    name = "ruBody" if ru else "body"
    m = re.search(rf"export const {name}: Block\[\] = (\[)", src)
    if not m:
        raise SystemExit(f"{name} not found in {p}")
    i = m.start(1)
    depth, j = 0, i
    while j < len(src):
        if src[j] == "[":
            depth += 1
        elif src[j] == "]":
            depth -= 1
            if depth == 0:
                break
        j += 1
    raw = src[i:j + 1]
    # TypeScript permits a trailing comma before the closing bracket; JSON does
    # not, and one body in this corpus has one. Strip it rather than hand the
    # decoder a string it will reject.
    raw = re.sub(r",(\s*[\]\}])", r"\1", raw)
    return json.loads(raw)


def load_meta(trinity: pathlib.Path, slug: str):
    """The index.ts entry for this slug, as data.

    index.ts is TypeScript, not JSON: keys are bare and strings may be single
    quoted. Rather than write a TS parser, the entry is isolated by brace
    matching and normalised field by field with explicit patterns -- if a field
    is missing the generator fails loudly instead of emitting a page with a
    blank title.
    """
    src = (trinity / "apps/website/src/data/blog/index.ts").read_text()
    # index.ts uses BOTH quote styles. A first version matched only the single
    # quoted form, found 1 of the 10 slugs it was given, and failed loudly on
    # the rest -- the same narrower-than-stated scope this project audits its
    # gates for. Failing loudly is why it cost minutes instead of a wrong page.
    m = re.search(rf"[\"']?slug[\"']?:\s*['\"]{re.escape(slug)}['\"]", src)
    if not m:
        raise SystemExit(f"{slug} is not in index.ts")
    at = m.start()
    start = src.rindex("{", 0, at)
    depth, j = 0, start
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    entry = src[start:j + 1]

    def one(field, required=True):
        m = re.search(rf"[\"']?\b{field}\b[\"']?:\s*(['\"])(.*?)(?<!\\)\1", entry, re.S)
        if not m:
            if required:
                raise SystemExit(f"field {field} missing for {slug}")
            return ""
        return m.group(2).replace("\\'", "'").replace('\\"', '"')

    def num(field):
        m = re.search(rf"[\"']?\b{field}\b[\"']?:\s*(\d+)", entry)
        return int(m.group(1)) if m else 0

    def arr(field):
        m = re.search(rf"[\"']?\b{field}\b[\"']?:\s*\[(.*?)\]", entry, re.S)
        if not m:
            return []
        return [s.replace("\\'", "'") for s in re.findall(r"(['\"])(.*?)(?<!\\)\1", m.group(1), re.S) and
                [g[1] for g in re.findall(r"(['\"])(.*?)(?<!\\)\1", m.group(1), re.S)]]

    receipts = [
        {"label": lbl.replace("\\'", "'"), "href": href}
        for lbl, href in re.findall(
            r"\{\s*[\"']?label[\"']?:\s*['\"](.*?)(?<!\\)['\"],\s*[\"']?href[\"']?:\s*['\"](.*?)['\"]\s*\}", entry, re.S
        )
    ]

    ru_block = ""
    rm = re.search(r"[\"']?\bru\b[\"']?:\s*\{", entry)
    if rm:
        d, k = 0, rm.end() - 1
        while k < len(entry):
            if entry[k] == "{":
                d += 1
            elif entry[k] == "}":
                d -= 1
                if d == 0:
                    break
            k += 1
        ru_block = entry[rm.end() - 1:k + 1]

    def ru_one(field):
        m = re.search(rf"[\"']?\b{field}\b[\"']?:\s*(['\"])(.*?)(?<!\\)\1", ru_block, re.S)
        return m.group(2).replace("\\'", "'") if m else ""

    def ru_open():
        m = re.search(r"[\"']?\bopenQuestions\b[\"']?:\s*\[(.*?)\]", ru_block, re.S)
        if not m:
            return []
        return [g[1].replace("\\'", "'") for g in re.findall(r"(['\"])(.*?)(?<!\\)\1", m.group(1), re.S)]

    # openQuestions of the ENGLISH entry: take the array that is not inside ru:
    en_entry = entry.replace(ru_block, "") if ru_block else entry
    m = re.search(r"[\"']?\bopenQuestions\b[\"']?:\s*\[(.*?)\]", en_entry, re.S)
    open_en = [g[1].replace("\\'", "'") for g in re.findall(r"(['\"])(.*?)(?<!\\)\1", m.group(1), re.S)] if m else []

    return {
        "slug": slug,
        "title": one("title"),
        "summary": one("summary"),
        "date": one("date"),
        "minutes": num("readingMinutes"),
        "tags": arr("tags"),
        "receipts": receipts,
        "openQuestions": open_en,
        "ruTitle": ru_one("title"),
        "ruSummary": ru_one("summary"),
        "ruOpenQuestions": ru_open(),
    }


def render_blocks(blocks):
    out = []
    for b in blocks:
        k = b.get("kind")
        if k == "p":
            out.append(f"<p>{inline(b['text'])}</p>")
        elif k == "h":
            out.append(f"<h2>{inline(b['text'])}</h2>")
        elif k == "ul":
            items = "".join(f"<li>{inline(i)}</li>" for i in b["items"])
            out.append(f"<ul>{items}</ul>")
        elif k == "ol":
            items = "".join(f"<li>{inline(i)}</li>" for i in b["items"])
            out.append(f"<ol>{items}</ol>")
        elif k == "quote":
            out.append(f"<blockquote>{inline(b['text'])}</blockquote>")
        elif k == "code":
            # Delimiters inside a code block are DATA. Escape only.
            out.append(f"<pre><code>{html.escape(b['text'], quote=False)}</code></pre>")
        elif k == "table":
            head = "".join(f"<th>{inline(h)}</th>" for h in b.get("headers", []))
            rows = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                for r in b.get("rows", [])
            )
            out.append(f'<div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif k == "figure":
            # Inline SVG, emitted verbatim: it is authored markup, not user
            # text, and the page CSS already sizes `figure svg`.
            out.append(
                f'<figure>{b["svg"]}<figcaption>{inline(b.get("caption", ""))}</figcaption></figure>'
            )
        else:
            raise SystemExit(f"unhandled block kind {k!r} -- refusing to drop content")
    return "\n".join(out)


STYLE = None  # filled from an existing page so the two lineages cannot drift


def page(meta, blocks, ru, style, template_nav, template_footer):
    slug = meta["slug"]
    title = meta["ruTitle"] if ru else meta["title"]
    summary = meta["ruSummary"] if ru else meta["summary"]
    questions = meta["ruOpenQuestions"] if ru else meta["openQuestions"]
    lang = "ru" if ru else "en"
    base = f"https://t27.ai/{'ru/' if ru else ''}blog/{slug}/"
    og = f"https://t27.ai/og-blog-{slug}{'-ru' if ru else ''}.png"
    e = lambda s: html.escape(s, quote=True)

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": title, "description": summary, "url": base,
        "mainEntityOfPage": {"@type": "WebPage", "@id": base},
        "image": og, "datePublished": meta["date"], "inLanguage": lang,
        "author": {"@type": "Person", "name": "Dmitrii Vasilev", "url": "https://github.com/gHashTag"},
        "publisher": {"@type": "Person", "name": "Dmitrii Vasilev"},
        "keywords": ", ".join(meta["tags"]),
    }, ensure_ascii=False)

    read = f"{meta['minutes']} мин чтения" if ru else f"{meta['minutes']} min read"
    open_label = "Что это не решает" if ru else "What this does not settle"
    receipts_label = "Квитанции" if ru else "Receipts"
    cta = ("Каждая цифра выше измерена, и рядом с ней названы её пределы."
           if ru else "Every figure above is measured, and the limits are named with it.")
    b_inter = "Открыть интерактивную версию" if ru else "Open the interactive version"
    b_other = ("Read in English" if ru else "Читать по-русски")
    other_href = (f"/blog/{slug}/" if ru else f"/ru/blog/{slug}/")
    all_posts = "Все посты" if ru else "All posts"
    inter_href = (f"/?lang=ru#/blog/{slug}" if ru else f"/#/blog/{slug}")

    qs = "".join(f"<li>{inline(q)}</li>" for q in questions)
    rs = "".join(
        f'<li><a href="{e(r["href"])}">{inline(r["label"])}</a></li>' for r in meta["receipts"]
    )
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in meta["tags"])

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(title)} · TRINITY</title>
<meta name="description" content="{e(summary)}" />
<link rel="canonical" href="{base}" />
<link rel="alternate" hreflang="en" href="https://t27.ai/blog/{slug}/" />
<link rel="alternate" hreflang="ru" href="https://t27.ai/ru/blog/{slug}/" />
<link rel="alternate" hreflang="x-default" href="https://t27.ai/blog/{slug}/" />
<link rel="alternate" type="application/atom+xml" title="{'Блог' if ru else 'Blog'} · TRINITY" href="https://t27.ai/{'ru/' if ru else ''}blog/feed.xml" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="TRINITY" />
<meta property="og:locale" content="{'ru_RU' if ru else 'en_US'}" />
<meta property="og:url" content="{base}" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(summary)}" />
<meta property="og:image" content="{og}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{e(title)}" />
<meta name="twitter:description" content="{e(summary)}" />
<link rel="icon" href="/favicon.svg" />
<script type="application/ld+json">{ld}</script>
<style>
{style}
</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="brand" href="/">T27.AI</a>
  {template_nav}
</header>
<p class="eyebrow">{'Блог' if ru else 'Blog'}</p>
<h1>{e(title)}</h1>
<p class="meta">{meta['date']} · {read}</p>
<p class="lede">{e(summary)}</p>
<div class="tags">{tags}</div>
{render_blocks(blocks)}
<div class="box"><h2>{open_label}</h2><ul>{qs}</ul></div>
<div class="box"><h2>{receipts_label}</h2><ul>{rs}</ul></div>
<div class="cta"><p>{cta}</p><div class="btns"><a class="btn" href="{inter_href}">{b_inter}</a><a class="btn sec" href="{other_href}" hreflang="{'en' if ru else 'ru'}" lang="{'en' if ru else 'ru'}">{b_other}</a><a class="btn sec" href="mailto:admin@t27.ai?subject={e(title)}">admin@t27.ai</a><a class="btn sec" href="/{'ru/' if ru else ''}blog/">{all_posts}</a></div></div>
{template_footer}
</div>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trinity", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--template", default="blog/four-hundred-and-twelve-tests-that-were-sentences/index.html")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()

    trinity = pathlib.Path(a.trinity)
    out = pathlib.Path(a.out)

    # Reuse the CSS, nav and footer of an already published page verbatim, so a
    # new page cannot diverge in styling from the thirty beside it.
    tpl = (out / a.template).read_text()
    style = re.search(r"<style>\n(.*?)\n</style>", tpl, re.S).group(1)
    nav = re.search(r'(<nav class="top">.*?</nav>)', tpl, re.S).group(1)
    footer = re.search(r"(<footer>.*?</footer>)", tpl, re.S).group(1)

    meta = load_meta(trinity, a.slug)
    for ru in (False, True):
        blocks = load_blocks(trinity, a.slug, ru)
        d = out / ("ru/blog" if ru else "blog") / a.slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(meta, blocks, ru, style, nav, footer))
        print(f"{d}/index.html  ({len(blocks)} blocks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
