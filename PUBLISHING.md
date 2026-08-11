# How this domain gets published, and the two ways it goes wrong

`t27.ai` is served from this repository (`CNAME`), built from `gHashTag/trinity`
at `apps/website`. A publish is: build there, copy `index.html`, `manifest.json`
and `assets/*` here, run `verify-site.sh`, commit, push. GitHub Pages serves
`index.html` with `max-age=600` and gives no custom headers.

## The publish race

More than one session publishes this site. Between the moment you build and the
moment you copy, another session can push a newer build made from a newer
`trinity` commit. Copying your build over theirs then silently reverts their
work — your `index.html` wins, and their source changes are simply gone from the
served bundle even though their commit is still in `trinity`.

This happened on 2026-08-11 and was caught only because `verify-site.sh` reported
a live bundle hash that matched neither generation on disk.

**Before copying anything:**

    git fetch origin && git rev-list --count HEAD..@{u}     # must be 0

If it is not 0, do not merge your build in. Pull, read the publish commit
message — it names the `trinity` commit it was built from — rebase your source
change onto that commit in `trinity`, rebuild, and only then copy. The published
bundle must descend from every source change already published, not just yours.

## Publishes are additive, so assets grow without bound

Each publish writes a new generation of content-hashed files and deletes none.
By 2026-08-11 `assets/` held 332 files of which 38 were reachable — 88 % dead
weight, 7.48 MB. It had been cleaned once before, at 150 files, and grew back.

Reachability is the transitive closure of the filename references in every HTML
file plus the JS those pull in. The check that the instrument is right: the
closure must return exactly the file count the current `dist/assets` emits. If
it returns fewer, the regex missed a reference form and deleting would break the
site.

**Keep the previous generation as well.** `index.html` is cached for 600 s, so a
visitor who loaded it just before the deploy will still request the old chunks.
Deleting only what is unreachable from *both* the current and the previous
`index.html` costs a few files and removes that window.

After deleting, `verify-site.sh` passing on disk is not the proof — push, wait
for Pages, and probe the lazy chunks the entry bundle names. The gate checks
routes and preview images, not the code-split chunks.

## The positioning audit

The gate checks that the site *works*. Nothing checks that it says the right
thing. Both failures found on 2026-08-11 were of that second kind, and one grep
found both:

    grep -rl "<headline number>" assets/*.js *.html

Take the headline figure of each strong result in `trinity-fpga/research/` and
ask whether the built site contains it. That is a proper instrument because it
reads the shipped bundles rather than the source, so it also catches a result
that exists in a component nothing routes to.

It found that `21.3545` — the perplexity behind a strict domination over MXFP4,
the strongest measured claim the project holds — appeared in **zero** built
files, while the hero led on a range comparison against tekum16, a format most
readers deciding between formats have never heard of. The strongest claim was
absent and a weaker one was over-stated.

**A claim ships with its limit or it does not ship.** The scale result went up
with the element-axis loss beside it, in the section for limits, because a block
format has two fields and we win one. A page that lists only the won field is
not describing the format.

## The routes audit

The positioning audit asks whether the site says the right thing. This one asks
whether a crawler can see it said at all. List the SPA's routes and subtract the
static landings:

    grep -oE 'path:"[^"]+"' assets/index-*.js | sed 's/path://;s/"//g' | sort -u

On 2026-08-11 that left `/blog` with no landing, and `/blog` answered **HTTP
404** — GitHub Pages served the SPA shim, the hash router picked the article up
in the browser, and every check anyone had run was a browser check. The sitemap
held zero blog URLs. Two real articles, one carrying the scale-field result,
were invisible to anything that does not execute JavaScript.

A landing that only summarises and links into the app does not fix this: it
ranks for nothing. `build-blog.py` puts the whole article in the HTML — 1,259
and 3,085 words — and the gate now fails any post under 400 words for exactly
that reason.

**Extract data by running the module, not by reading it.** The posts live in
TypeScript in another repo. Transpiling with the project's own esbuild and
importing the result is the only version that cannot drift from what ships. It
also surfaced a trap a regex would have sailed past: `publishedPosts` is a
*function*, not an array, and `JSON.stringify` of the binding returns
`undefined` — `writeFileSync` then throws, but a slightly different script would
have written `"undefined"` into the data file and generated an empty blog with
no error anywhere.

**A new gate check must be shown to fail.** After extending `verify-site.sh`,
remove the card and delete the sitemap line, confirm exit 1 each time, and put
them back. A check that has never failed is not evidence.

## Translations are URLs, not links

Both blog posts carried a complete Russian translation in the data — the same 20
and 60 blocks as the English — and it reached readers only as a "Читать
по-русски" button into the app. A translation behind a fragment URL is invisible
to search in the same way the whole blog was: there is no Russian page to rank,
so the work earned nothing.

Russian now lives at `/ru/blog/<slug>/` as real HTML. Three things that decide
whether that is worth anything:

- **Reciprocal `hreflang`, or it counts as duplicate content.** Each page is
  canonical for *itself*, and both name each other plus an `x-default`. A
  one-way alternate is the common way to get this wrong, so the gate checks both
  directions.
- **`<html lang="ru">`.** Cheap, and the thing that tells a crawler which
  audience the page is for.
- **Its own preview card.** A Russian reader shares a Russian link; an English
  card on it looks like a mistake. Cyrillic rasterises fine through the existing
  `build-og.py` path.

**Skip rather than half-translate.** A post with no Russian overlay is not
written to `/ru/`, because an English body under a `ru` URL is worse than no page
— it tells a reader the language is available and then breaks the promise.

### Translated copy needs a structural check, not review

The eight landings are translated in `landing-ru.json`, deliberately not in a
second dict beside the English one: two dicts in one file get edited past each
other, and nothing complains. `build-landing.py` refuses to render a page whose
Russian section and item counts differ from the English, and names the counts:

    landing-ru.json: gft section 0 has 1 items, English has 2

That catches the failure that matters — a translation quietly losing a section
ships a page half the length of its twin while `hreflang` asserts the two are
the same document. It cannot catch a bad translation, and does not pretend to.

**Generate translated cards from the originals, not from scratch.** The Russian
preview cards are the English SVGs with their text nodes substituted through a
lookup. Anything absent from the lookup is reported rather than passed through,
so a forgotten string is impossible to ship silently — the opposite of drawing
eight new cards and hoping none was missed. Russian runs roughly 20 % longer, so
the headline font is eased; check one long card by eye afterwards regardless.

### A language directory needs a root

`/ru/gft/` and its seven siblings worked while `/ru/` itself answered **404**.
Trimming a URL back to its parent is something readers and crawlers both do, and
it landed on an error page. Any time a directory of pages is added, give the
directory itself a page.

**Watch the empty slug.** `/ru/` is rendered by the same function as the
landings, with an empty slug — and the naive path build then produces
`href="//"`, which a browser reads as *protocol-relative* and follows to a
different host entirely, plus a canonical of `/ru//` and a card named
`og--ru.png`. The repair asserts its own success and raises if any of the four
shapes survives, because this is exactly the class of bug that looks fine in a
diff and is only visible in the artefact.

### Half of a reciprocal pair can live in another repository

`/ru/` is generated here; the homepage's matching `hreflang` is in the SPA's
`index.html`, which is generated in **trinity**. That half disappears on any
rebuild from a source that lacks it, and nothing local would notice — the
Russian pages would still be perfect and still be filed as duplicates. The gate
checks both directions and names where the missing half comes from.
