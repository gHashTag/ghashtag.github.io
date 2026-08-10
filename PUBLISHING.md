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
