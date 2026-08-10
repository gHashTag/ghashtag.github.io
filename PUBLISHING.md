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
