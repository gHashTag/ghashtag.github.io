#!/usr/bin/env python3
"""Static blog pages, because the blog was invisible.

`/blog` returned HTTP 404 and the SPA shim; the sitemap held zero blog URLs. The
posts are real content -- one of them carries the scale-field result -- and a
crawler that does not run JavaScript saw none of it.

These pages carry the whole article, not a summary linking into the app. A
summary would rank for nothing; the point is that the text itself is indexable.
The app keeps the interactive version and every page links to it.

The data comes from trinity's `apps/website/src/data/blog/posts.ts`, extracted
by transpiling the real module rather than parsing it with regexes:

    npx esbuild src/data/blog/posts.ts --format=esm --platform=node --outfile=posts.mjs
    node -e "import('./posts.mjs').then(m=>console.log(JSON.stringify(m.publishedPosts(),null,1)))" > blog-posts.json

Note `publishedPosts` is a function, not an array -- `JSON.stringify` on the
binding itself yields `undefined` and writes a broken file without erroring.

    python3 build-blog.py
"""
import html
import json
import os

SITE = "https://t27.ai"
EMAIL = "admin@t27.ai"
DATA = "blog-posts.json"

NAV = [
    ("gft", "Format"), ("verification", "Verification"), ("proof", "Proof"),
    ("ip", "IP"), ("course", "Course"), ("cases", "Cases"), ("about", "About"),
]

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#05070a;color:#e8efec;font:16px/1.65 Inter,-apple-system,Segoe UI,Helvetica,Arial,sans-serif}
a{color:#00ff88;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:820px;margin:0 auto;padding:2rem 1.25rem 4rem}
header.top{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between;margin-bottom:3rem}
.brand{font-weight:700;letter-spacing:3px;color:#00ff88}
nav.top{display:flex;flex-wrap:wrap;gap:1rem;font-size:.9rem}
nav.top a{color:#9fb3ab}
.eyebrow{color:#00ff88;letter-spacing:3px;text-transform:uppercase;font-size:.75rem;margin:0 0 .75rem}
h1{font-size:clamp(1.9rem,5.5vw,2.8rem);line-height:1.15;margin:0 0 1rem}
h2{font-size:clamp(1.25rem,3.4vw,1.6rem);line-height:1.25;margin:2.5rem 0 .75rem}
h3{font-size:1.05rem;margin:1.75rem 0 .5rem;color:#00ff88}
.meta{color:#7d928b;font-size:.9rem;margin:0 0 2rem}
.lede{font-size:1.1rem;color:#c7d6d0;margin:0 0 2rem}
p{margin:0 0 1rem}
ul,ol{margin:0 0 1rem;padding-left:1.3rem}li{margin:.35rem 0}
blockquote{margin:1.5rem 0;padding:.4rem 0 .4rem 1.1rem;border-left:3px solid #1d4b3a;color:#a9bdb5;font-style:italic}
pre{background:#0a1014;border:1px solid #16241f;border-radius:6px;padding:1rem;overflow-x:auto;font-size:.85rem}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.tw{overflow-x:auto;margin:0 0 1.25rem}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid #1d2b2a;padding:.5rem .7rem;text-align:left}
th{color:#00ff88;font-weight:600}
.box{border:1px solid #1d2b2a;border-radius:8px;padding:1.1rem 1.25rem;margin:2rem 0;background:#070c10}
.box h2{margin-top:0;font-size:1.1rem}
.tags{display:flex;flex-wrap:wrap;gap:.5rem;margin:0 0 2rem}
.tag{border:1px solid #1d2b2a;border-radius:99px;padding:.15rem .7rem;font-size:.78rem;color:#9fb3ab}
.cta{border-top:1px solid #1d2b2a;margin-top:3rem;padding-top:1.5rem}
.btns{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem}
.btn{border:1px solid #00ff88;border-radius:6px;padding:.55rem 1rem;font-size:.9rem}
.btn.sec{border-color:#1d2b2a;color:#c7d6d0}
footer{margin-top:3rem;padding-top:1.5rem;border-top:1px solid #1d2b2a;color:#7d928b;font-size:.85rem}
.posts{list-style:none;padding:0;margin:0}
.posts li{border-top:1px solid #1d2b2a;padding:1.5rem 0}
.posts h2{margin:0 0 .4rem;font-size:1.2rem}
"""


def esc(s):
    return html.escape(str(s))


def block_html(b):
    k = b.get("kind")
    if k == "p":
        return f"<p>{esc(b['text'])}</p>"
    if k == "h":
        return f"<h2>{esc(b['text'])}</h2>"
    if k == "ul":
        return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in b["items"]) + "</ul>"
    if k == "ol":
        return "<ol>" + "".join(f"<li>{esc(i)}</li>" for i in b["items"]) + "</ol>"
    if k == "quote":
        return f"<blockquote>{esc(b['text'])}</blockquote>"
    if k == "code":
        return f"<pre><code>{esc(b['text'])}</code></pre>"
    if k == "table":
        head = "".join(f"<th>{esc(c)}</th>" for c in b["head"])
        rows = "".join(
            "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>"
            for r in b["rows"]
        )
        # Wide tables scroll inside their own box; the page body must not.
        return f'<div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
    raise SystemExit(f"build-blog: unknown block kind {k!r} -- add it rather than dropping it")


def nav_html():
    return "".join(f'<a href="/{s}/">{esc(l)}</a>' for s, l in NAV)


def shell(*, url, title, desc, og, body, lang="en"):
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)} · TRINITY</title>
<meta name="description" content="{esc(desc)}" />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="TRINITY" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="{SITE}/{og}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<link rel="icon" href="/favicon.svg" />
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="brand" href="/">T27.AI</a>
  <nav class="top">{nav_html()}</nav>
</header>
{body}
<footer>
  Dmitrii Vasilev — hardware-AI and FPGA/RTL engineer.
  <a href="https://github.com/gHashTag">GitHub</a> ·
  <a href="https://linkedin.com/in/neurocoder">LinkedIn</a> ·
  <a href="{SITE}/cv.pdf">CV</a> ·
  <a href="https://arxiv.org/abs/2606.05017">arXiv:2606.05017</a> ·
  <a href="https://arxiv.org/abs/2606.09686">arXiv:2606.09686</a>
</footer>
</div>
</body>
</html>
"""


def post_page(p):
    slug = p["slug"]
    url = f"{SITE}/blog/{slug}/"
    parts = [
        '<p class="eyebrow">Blog</p>',
        f"<h1>{esc(p['title'])}</h1>",
        f'<p class="meta">{esc(p["date"])} · {esc(p["readingMinutes"])} min read</p>',
        f'<p class="lede">{esc(p["summary"])}</p>',
    ]
    if p.get("tags"):
        parts.append('<div class="tags">' + "".join(f'<span class="tag">{esc(t)}</span>' for t in p["tags"]) + "</div>")
    parts += [block_html(b) for b in p["body"]]

    if p.get("openQuestions"):
        parts.append(
            '<div class="box"><h2>What this does not settle</h2><ul>'
            + "".join(f"<li>{esc(q)}</li>" for q in p["openQuestions"])
            + "</ul></div>"
        )
    if p.get("receipts"):
        parts.append(
            '<div class="box"><h2>Receipts</h2><ul>'
            + "".join(f'<li><a href="{esc(r["href"])}">{esc(r["label"])}</a></li>' for r in p["receipts"])
            + "</ul></div>"
        )

    ru_link = (
        f'<a class="btn sec" href="/?lang=ru#/blog/{slug}" hreflang="ru" lang="ru">Читать по-русски</a>'
        if p.get("ru") else ""
    )
    parts.append(
        '<div class="cta"><p>Every figure above is measured, and the limits are named with it.</p>'
        f'<div class="btns"><a class="btn" href="/#/blog/{slug}">Open the interactive version</a>'
        f'{ru_link}'
        f'<a class="btn sec" href="mailto:{EMAIL}?subject={esc(p["title"])}">{EMAIL}</a>'
        '<a class="btn sec" href="/blog/">All posts</a></div></div>'
    )
    return shell(url=url, title=p["title"], desc=p["summary"],
                 og=f"og-blog-{slug}.png", body="\n".join(parts))


def index_page(posts):
    items = "".join(
        f'<li><h2><a href="/blog/{esc(p["slug"])}/">{esc(p["title"])}</a></h2>'
        f'<p class="meta">{esc(p["date"])} · {esc(p["readingMinutes"])} min read</p>'
        f'<p>{esc(p["summary"])}</p></li>'
        for p in posts
    )
    body = (
        '<p class="eyebrow">Blog</p><h1>Written here first.</h1>'
        '<p class="lede">Every article is published on this domain before anywhere else, '
        'with its receipts and with what it does not settle stated in the text.</p>'
        f'<ul class="posts">{items}</ul>'
    )
    return shell(url=f"{SITE}/blog/", title="Blog",
                 desc="Measured results from ternary hardware and low-precision numeric formats, published here first with receipts and open questions.",
                 og="og-image.png", body=body)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    posts = json.load(open(DATA, encoding="utf-8"))
    if not posts:
        raise SystemExit("build-blog: no posts in " + DATA)
    posts.sort(key=lambda p: p["date"], reverse=True)

    os.makedirs("blog", exist_ok=True)
    for p in posts:
        d = os.path.join("blog", p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(post_page(p))
        print(f"wrote blog/{p['slug']}/index.html")
    with open("blog/index.html", "w", encoding="utf-8") as fh:
        fh.write(index_page(posts))
    print("wrote blog/index.html")


if __name__ == "__main__":
    main()
