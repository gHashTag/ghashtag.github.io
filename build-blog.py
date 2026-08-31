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
import re
from urllib.parse import quote

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
a{color:#d8bc7a;text-decoration:none}a:hover{color:#f0d79a;text-decoration:underline}
.wrap{max-width:820px;margin:0 auto;padding:2rem 1.25rem 4rem}
header.top{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between;margin-bottom:3rem}
.brand{font-weight:700;letter-spacing:3px;color:#d8bc7a}
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
figure{margin:0 0 1.8rem;overflow-x:auto}
figure svg{max-width:100%;height:auto}
figcaption{font-size:.86rem;opacity:.75;margin-top:.6rem;line-height:1.5}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid #1d2b2a;padding:.5rem .7rem;text-align:left}
th{color:#00ff88;font-weight:600}
.box{border:1px solid #1d2b2a;border-radius:8px;padding:1.1rem 1.25rem;margin:2rem 0;background:#070c10}
.box h2{margin-top:0;font-size:1.1rem}
.tags{display:flex;flex-wrap:wrap;gap:.5rem;margin:0 0 2rem}
.tag{border:1px solid #5f5238;border-radius:99px;padding:.15rem .7rem;font-size:.78rem;color:#d8bc7a}
.cta{border-top:1px solid #1d2b2a;margin-top:3rem;padding-top:1.5rem}
.btns{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem}
.btn{border:1px solid #8f7a50;border-radius:6px;padding:.55rem 1rem;font-size:.9rem;color:#d8bc7a}
.btn.sec{border-color:#1d2b2a;color:#c7d6d0}
.work-cta{border:1px solid #1d2b2a;border-left:3px solid #00ff88;border-radius:10px;margin-top:3rem;padding:1.35rem 1.5rem;background:#070c10}
.work-cta h2{margin:.35rem 0 .7rem;font-size:1.45rem}
.work-cta .eyebrow{margin:0;color:#00ff88}
.work-cta p{color:#c7d6d0}
.work-links{display:flex;flex-wrap:wrap;gap:.45rem 1rem;margin-top:1.1rem;font-size:.9rem;color:#7d928b}
footer{margin-top:3rem;padding-top:1.5rem;border-top:1px solid #1d2b2a;color:#7d928b;font-size:.85rem}
.posts{list-style:none;padding:0;margin:0}
.posts li{border-top:1px solid #1d2b2a;padding:1.5rem 0}
.posts h2{margin:0 0 .4rem;font-size:1.2rem}
"""


# Page chrome per locale. The Russian overlay in posts.ts covers title, summary,
# body and openQuestions but not receipts — those are links to pull requests and
# commits, so they stay in the language their targets are written in.
UI = {
    "en": {
        "eyebrow": "Blog", "read": "min read",
        "notSettled": "What this does not settle", "receipts": "Receipts",
        "indexH1": "Written here first.",
        "indexLede": "Every article is published on this domain before anywhere else, "
                     "with its receipts and with what it does not settle stated in the text.",
        "indexDesc": "Measured results from ternary hardware and low-precision numeric formats, "
                     "published here first with receipts and open questions.",
        "openApp": "Open the interactive version", "all": "All posts",
        "other": "Читать по-русски", "otherLang": "ru",
        "workEyebrow": "Work with me", "workPrimary": "Discuss your project",
        "servicesLabel": "Services",
        "services": [
            ("Verification", "/verification/"), ("IP licensing", "/ip/"),
            ("Courses and workshops", "/course/"), ("Contract work", "/about/"),
        ],
        "workTracks": {
            "verification": (
                "Want this kind of check on your own design?",
                "I audit RTL and build independent, bit-exact models, then take the result through synthesis and, when useful, onto an Artix-7 board. The first conformance module is free.",
                "See the verification service", "/verification/",
            ),
            "arithmetic": (
                "Need arithmetic built for your constraints?",
                "I design low-precision and ternary formats, synthesizable RTL, independent reference models and bit-exact vectors. Existing measured cores can also be licensed.",
                "See IP and custom arithmetic", "/ip/",
            ),
            "engineering": (
                "Need an FPGA/RTL problem taken to measured hardware?",
                "I work contract and part-time on hardware-AI, FPGA/RTL and ML systems — from specification and open toolchains to reproducible measurements.",
                "See how I work", "/about/",
            ),
            "training": (
                "Want your team to build and verify this themselves?",
                "I run a self-paced FPGA course, a four-week cohort and two-day team workshops built around a problem your engineers actually have.",
                "See courses and workshops", "/course/",
            ),
        },
    },
    "ru": {
        "eyebrow": "Блог", "read": "мин чтения",
        "notSettled": "Чего это не решает", "receipts": "Пруфы",
        "indexH1": "Публикуется сначала здесь.",
        "indexLede": "Каждая статья выходит на этом домене раньше, чем где-либо ещё — "
                     "вместе с пруфами и с прямо названным в тексте тем, чего она не решает.",
        "indexDesc": "Измеренные результаты по тернарному железу и форматам низкой разрядности — "
                     "публикуются здесь первыми, с пруфами и открытыми вопросами.",
        "openApp": "Открыть интерактивную версию", "all": "Все статьи",
        "other": "Read in English", "otherLang": "en",
        "workEyebrow": "Поработаем вместе", "workPrimary": "Обсудить задачу",
        "servicesLabel": "Услуги",
        "services": [
            ("Верификация", "/ru/verification/"), ("Лицензирование IP", "/ru/ip/"),
            ("Курсы и воркшопы", "/ru/course/"), ("Контрактная работа", "/ru/about/"),
        ],
        "workTracks": {
            "verification": (
                "Хотите так же проверить собственный дизайн?",
                "Я аудирую RTL и строю независимые побитово точные модели, затем провожу результат через синтез и, когда это полезно, проверяю на плате Artix-7. Первый модуль проверки — бесплатно.",
                "Услуга верификации", "/ru/verification/",
            ),
            "arithmetic": (
                "Нужна арифметика под ваши ограничения?",
                "Я проектирую форматы низкой разрядности и троичную арифметику, синтезируемый RTL, независимые референсные модели и побитовые тест-векторы. Готовые измеренные ядра можно лицензировать.",
                "IP и заказная арифметика", "/ru/ip/",
            ),
            "engineering": (
                "Нужно довести FPGA/RTL-задачу до замеров на железе?",
                "Работаю по контракту и part-time с hardware-AI, FPGA/RTL и ML-системами — от спецификации и открытого тулчейна до воспроизводимых измерений.",
                "Как я работаю", "/ru/about/",
            ),
            "training": (
                "Хотите, чтобы команда умела строить и проверять это сама?",
                "Провожу самостоятельный FPGA-курс, четырёхнедельный поток и двухдневные воркшопы вокруг реальной задачи вашей команды.",
                "Курсы и воркшопы", "/ru/course/",
            ),
        },
    },
}

# English at /blog/<slug>/, Russian at /ru/blog/<slug>/. English keeps the bare
# path because it is the default and already carries the links people have.
def base(lang):
    return "/blog" if lang == "en" else "/ru/blog"


def localise(p, lang):
    """The post as one locale sees it, falling back per field rather than wholesale.

    An all-or-nothing overlay would drop the receipts, which the Russian text
    does not translate, and a reader would lose the links entirely.
    """
    if lang == "en":
        return p
    ru = p.get("ru") or {}
    out = dict(p)
    for k in ("title", "summary", "body", "openQuestions"):
        if ru.get(k):
            out[k] = ru[k]
    return out


def esc(s):
    return html.escape(str(s))


def hashtag(tag):
    """Render taxonomy labels as compact social hashtags."""
    words = re.findall(r"[^\W_]+", str(tag).lstrip("#"), flags=re.UNICODE)
    if not words:
        raise SystemExit(f"build-blog: invalid empty tag {tag!r}")
    if len(words) == 1:
        return f"#{words[0]}"
    return "#" + "".join(
        word if word.isupper() else word[:1].upper() + word[1:]
        for word in words
    )


INLINE = re.compile(r"\*\*([^*]+)\*\*|`([^`]+)`")


def rich(text):
    """Escape, then RENDER the inline markup instead of showing it.

    Readers were getting the source. `**Executed**` and `` `zig build` ``
    reached t27.ai with their delimiters intact on 18 of 62 pages, because this
    file escaped and stopped. The app had the same defect (trinity#864, #865).

    Two forms, because the corpus was measured before the fix was chosen: 31
    bold spans, 123 code spans, zero markdown links. A markdown dependency
    would be more machinery than the data needs.

    Bold RECURSES. One Russian paragraph is a code span inside a bold span; a
    flat pass matches the bold first, `[^*]+` swallows the backticks, and the
    reader sees them. That one was found only because the sweep covered BOTH
    locales -- an English-only sweep over a bilingual corpus reads clean while
    checking half the pages.

    A `code` BLOCK never comes here: one post quotes tool output that literally
    contains `- **NOTE** purely combinational`, where the asterisks are data.
    """
    out, last = [], 0
    for m in INLINE.finditer(str(text)):
        out.append(esc(str(text)[last:m.start()]))
        if m.group(1) is not None:
            out.append(f"<strong>{rich(m.group(1))}</strong>")
        else:
            out.append(f"<code>{esc(m.group(2))}</code>")
        last = m.end()
    out.append(esc(str(text)[last:]))
    return "".join(out)


def block_html(b):
    k = b.get("kind")
    if k == "p":
        return f"<p>{rich(b['text'])}</p>"
    if k == "h":
        return f"<h2>{rich(b['text'])}</h2>"
    if k == "ul":
        return "<ul>" + "".join(f"<li>{rich(i)}</li>" for i in b["items"]) + "</ul>"
    if k == "ol":
        return "<ol>" + "".join(f"<li>{rich(i)}</li>" for i in b["items"]) + "</ol>"
    if k == "quote":
        return f"<blockquote>{rich(b['text'])}</blockquote>"
    if k == "code":
        return f"<pre><code>{esc(b['text'])}</code></pre>"
    if k == "table":
        head = "".join(f"<th>{rich(c)}</th>" for c in b["head"])
        rows = "".join(
            "<tr>" + "".join(f"<td>{rich(c)}</td>" for c in r) + "</tr>"
            for r in b["rows"]
        )
        # Wide tables scroll inside their own box; the page body must not.
        return f'<div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
    if k == "figure":
        # The SVG is authored in trinity's own data files and reaches here through
        # blog-posts.json unchanged -- no reader supplies it -- so it is inlined as
        # markup, exactly as the app does. The caption is prose and is escaped.
        return f"<figure>{b['svg']}<figcaption>{esc(b['caption'])}</figcaption></figure>"
    raise SystemExit(f"build-blog: unknown block kind {k!r} -- add it rather than dropping it")


def nav_html():
    return "".join(f'<a href="/{s}/">{esc(l)}</a>' for s, l in NAV)


def article_ld(*, url, title, desc, og, date, lang, tags):
    """Article structured data.

    Only the homepage carried JSON-LD; every landing and every post had none.
    A post is the case where it pays most — it has a real publication date, an
    author and a subject, and none of that is inferable from the prose. Only
    fields the data actually contains are emitted: inventing a dateModified or a
    publisher logo to fill the schema would be describing a site that does not
    exist.
    """
    import json as _json
    doc = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": desc,
        "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "image": f"{SITE}/{og}",
        "datePublished": date,
        "inLanguage": lang,
        "author": {
            "@type": "Person",
            "name": "Dmitrii Vasilev",
            "url": "https://github.com/gHashTag",
        },
        "publisher": {"@type": "Person", "name": "Dmitrii Vasilev"},
    }
    if tags:
        doc["keywords"] = ", ".join(tags)
    return ('<script type="application/ld+json">'
            + _json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def shell(*, url, title, desc, og, body, lang="en", alt=None, ld=""):
    # Both language versions point at each other and at an x-default, so neither
    # is filed as a duplicate of the other. Each is canonical for itself.
    hreflang = ""
    if alt:
        en_url, ru_url = alt
        hreflang = (
            f'\n<link rel="alternate" hreflang="en" href="{en_url}" />'
            f'\n<link rel="alternate" hreflang="ru" href="{ru_url}" />'
            f'\n<link rel="alternate" hreflang="x-default" href="{en_url}" />'
        )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)} · TRINITY</title>
<meta name="description" content="{esc(desc)}" />
<link rel="canonical" href="{url}" />{hreflang}
<link rel="alternate" type="application/atom+xml" title="{esc(UI[lang]['eyebrow'])} · TRINITY" href="https://t27.ai{base(lang)}/feed.xml" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="TRINITY" />
<meta property="og:locale" content="{'ru_RU' if lang == 'ru' else 'en_US'}" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="{SITE}/{og}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<link rel="icon" href="/favicon.svg" />
{ld}
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


VERIFICATION_TAGS = {
    "audit", "ci", "conformance", "formal", "methodology", "mutation testing",
    "reproducibility", "static analysis", "test design", "testing", "verification",
}
ARITHMETIC_TAGS = {
    "4-bit", "accuracy", "arithmetic", "attention", "golden ratio", "mxfp4",
    "number formats", "numeric formats", "quantisation", "quantization", "scaling",
    "ternary", "transformers",
}
ENGINEERING_TAGS = {
    "artix-7", "ethernet", "fpga", "hardware", "litex", "nextpnr", "open source",
    "openxc7", "place and route", "rgmii", "timing", "tooling", "yosys", "zynq",
}


def work_track(p):
    tags = {str(tag).lower() for tag in p.get("tags", [])}
    if "training" in tags:
        return "training"
    if tags & VERIFICATION_TAGS:
        return "verification"
    if tags & ARITHMETIC_TAGS:
        return "arithmetic"
    if tags & ENGINEERING_TAGS:
        return "engineering"
    return "engineering"


def work_offer(p, d, lang):
    """One contextual commercial action after the article, with honest scope.

    The button is deliberately email, not a generic service landing: a reader
    who reached the end has already supplied the context. The article URL and
    title travel in the draft, while the relevant service page explains terms
    before the reader sends anything. The other services remain small links so
    four equal calls to action do not compete with the one useful next step.
    """
    u = UI[lang]
    title, body, detail, href = u["workTracks"][work_track(p)]
    article_url = f"{SITE}{base(lang)}/{p['slug']}/"
    if lang == "ru":
        subject = f"Задача для T27 — {d['title']}"
        message = (f"Здравствуйте, Дмитрий! Я прочитал(а) статью «{d['title']}»: "
                   f"{article_url}\n\nНаша задача:")
    else:
        subject = f"Project for T27 — {d['title']}"
        message = f"Hi Dmitrii, I read “{d['title']}”: {article_url}\n\nOur project:"
    mailto = (f"mailto:{EMAIL}?subject={quote(subject, safe='')}"
              f"&body={quote(message, safe='')}")
    services = "".join(
        f'<a href="{esc(service_href)}">{esc(label)}</a>'
        for label, service_href in u["services"]
    )
    return (
        f'<section class="work-cta" aria-labelledby="blog-work-offer-title">'
        f'<p class="eyebrow">{esc(u["workEyebrow"])}</p>'
        f'<h2 id="blog-work-offer-title">{esc(title)}</h2>'
        f'<p>{esc(body)}</p>'
        f'<div class="btns"><a class="btn" href="{esc(mailto)}">{esc(u["workPrimary"])}</a>'
        f'<a class="btn sec" href="{esc(href)}">{esc(detail)}</a></div>'
        f'<nav class="work-links" aria-label="{esc(u["servicesLabel"])}">'
        f'<span>{esc(u["servicesLabel"])}:</span>{services}</nav></section>'
    )


def post_page(p, lang="en"):
    u = UI[lang]
    slug = p["slug"]
    d = localise(p, lang)
    url = f"{SITE}{base(lang)}/{slug}/"
    alt = (f"{SITE}/blog/{slug}/", f"{SITE}/ru/blog/{slug}/") if p.get("ru") else None
    parts = [
        f'<p class="eyebrow">{esc(u["eyebrow"])}</p>',
        f"<h1>{esc(d['title'])}</h1>",
        f'<p class="meta">{esc(p["date"])} · {esc(p["readingMinutes"])} {esc(u["read"])}</p>',
        f'<p class="lede">{esc(d["summary"])}</p>',
    ]
    if not p.get("tags"):
        raise SystemExit(f"build-blog: post {slug} has no mandatory tags")
    parts.append('<div class="tags">' + "".join(f'<span class="tag">{esc(hashtag(t))}</span>' for t in p["tags"]) + "</div>")
    parts += [block_html(b) for b in d["body"]]

    if d.get("openQuestions"):
        parts.append(
            f'<div class="box"><h2>{esc(u["notSettled"])}</h2><ul>'
            + "".join(f"<li>{rich(q)}</li>" for q in d["openQuestions"])
            + "</ul></div>"
        )
    if d.get("receipts"):
        parts.append(
            f'<div class="box"><h2>{esc(u["receipts"])}</h2><ul>'
            + "".join(f'<li><a href="{esc(r["href"])}">{esc(r["label"])}</a></li>' for r in d["receipts"])
            + "</ul></div>"
        )

    other = ""
    if p.get("ru"):
        o = u["otherLang"]
        other = (f'<a class="btn sec" href="{base(o)}/{slug}/" hreflang="{o}" lang="{o}">'
                 f'{esc(u["other"])}</a>')
    app = f"/#/blog/{slug}" if lang == "en" else f"/?lang=ru#/blog/{slug}"
    parts.append(
        f'<div class="cta"><div class="btns">'
        f'<a class="btn sec" href="{app}">{esc(u["openApp"])}</a>'
        f'{other}'
        f'<a class="btn sec" href="{base(lang)}/">{esc(u["all"])}</a></div></div>'
    )
    parts.append(work_offer(p, d, lang))
    og = f"og-blog-{slug}.png" if lang == "en" else f"og-blog-{slug}-ru.png"
    ld = article_ld(url=url, title=d["title"], desc=d["summary"], og=og,
                    date=p["date"], lang=lang, tags=p.get("tags"))
    return shell(url=url, title=d["title"], desc=d["summary"],
                 og=og, body="\n".join(parts), lang=lang, alt=alt, ld=ld)


def index_page(posts, lang="en"):
    u = UI[lang]
    items = []
    for p in posts:
        d = localise(p, lang)
        items.append(
            f'<li><h2><a href="{base(lang)}/{esc(p["slug"])}/">{esc(d["title"])}</a></h2>'
            f'<p class="meta">{esc(p["date"])} · {esc(p["readingMinutes"])} {esc(u["read"])}</p>'
            f'<p>{esc(d["summary"])}</p></li>'
        )
    o = u["otherLang"]
    body = (
        f'<p class="eyebrow">{esc(u["eyebrow"])}</p><h1>{esc(u["indexH1"])}</h1>'
        f'<p class="lede">{esc(u["indexLede"])}</p>'
        f'<ul class="posts">{"".join(items)}</ul>'
        f'<div class="cta"><div class="btns">'
        f'<a class="btn sec" href="{base(o)}/" hreflang="{o}" lang="{o}">{esc(u["other"])}</a>'
        f'</div></div>'
    )
    return shell(url=f"{SITE}{base(lang)}/", title=u["eyebrow"], desc=u["indexDesc"],
                 og="og-image.png", body=body, lang=lang,
                 alt=(f"{SITE}/blog/", f"{SITE}/ru/blog/"))


def feed_xml(posts, lang):
    """An Atom feed per language.

    The blog's own lede says everything is published here first and every other
    platform links back. Without a feed the only way to honour that is to visit
    the page and remember what was already read, which is a thing nobody does --
    so the claim was true and unusable at the same time.

    One feed per language, not one feed with both. A reader who wants the
    Russian text does not want half the entries in English, and Atom has no way
    to say "skip this one" that a reader would see before opening it.
    """
    site = "https://t27.ai"
    root = base(lang)
    self_url = f"{site}{root}/feed.xml"
    updated = max(p["date"] for p in posts) if posts else "1970-01-01"
    t = UI[lang]

    def entry(p):
        url = f"{site}{root}/{p['slug']}/"
        q = localise(p, lang)
        # The summary only. A full-text feed would have to serialise every block
        # kind, and a feed that silently drops the kinds it cannot render is
        # worse than one that says "the post is over there".
        return (
            "<entry>"
            f"<title>{esc(q['title'])}</title>"
            f"<link rel=\"alternate\" type=\"text/html\" href=\"{esc(url)}\"/>"
            f"<id>{esc(url)}</id>"
            f"<updated>{esc(p['date'])}T00:00:00Z</updated>"
            f"<published>{esc(p['date'])}T00:00:00Z</published>"
            f"<summary type=\"text\">{esc(q.get('summary', ''))}</summary>"
            + "".join(f"<category term=\"{esc(tag)}\"/>" for tag in p.get("tags", []))
            + "</entry>"
        )

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{lang}">'
        f"<title>{esc(t['eyebrow'])} · TRINITY</title>"
        f"<subtitle>{esc(t['indexLede'])}</subtitle>"
        f'<link rel="self" type="application/atom+xml" href="{esc(self_url)}"/>'
        f'<link rel="alternate" type="text/html" href="{esc(site + root)}/"/>'
        f"<id>{esc(site + root)}/</id>"
        f"<updated>{esc(updated)}T00:00:00Z</updated>"
        "<author><name>Dmitrii Vasilev</name><email>admin@t27.ai</email></author>"
        + "".join(entry(p) for p in posts)
        + "</feed>\n"
    )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    posts = json.load(open(DATA, encoding="utf-8"))
    if not posts:
        raise SystemExit("build-blog: no posts in " + DATA)
    posts.sort(key=lambda p: p["date"], reverse=True)

    for lang in ("en", "ru"):
        root = base(lang).lstrip("/")
        os.makedirs(root, exist_ok=True)
        for p in posts:
            # A post with no Russian overlay would otherwise ship an English body
            # under a ru URL, which is worse than not having the page.
            if lang == "ru" and not p.get("ru"):
                print(f"skipped ru/blog/{p['slug']}/ — no Russian overlay")
                continue
            d = os.path.join(root, p["slug"])
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(post_page(p, lang))
            print(f"wrote {root}/{p['slug']}/index.html")
        listed = [p for p in posts if lang == "en" or p.get("ru")]
        with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(index_page(listed, lang))
        print(f"wrote {root}/index.html")

        xml = feed_xml(listed, lang)
        # A feed missing a post is silent: the reader simply never learns the
        # post exists, and nothing on either side reports it. So the count is
        # asserted rather than assumed.
        if xml.count("<entry>") != len(listed):
            raise SystemExit(
                f"build-blog: {root}/feed.xml has {xml.count('<entry>')} entries "
                f"for {len(listed)} listed posts"
            )
        with open(os.path.join(root, "feed.xml"), "w", encoding="utf-8") as fh:
            fh.write(xml)
        print(f"wrote {root}/feed.xml ({len(listed)} entries)")


if __name__ == "__main__":
    main()
