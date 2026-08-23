#!/usr/bin/env python3
"""Would copying this build over the deployed one drop a post?

`verify-site.sh` asks whether the DEPLOYED app and the static `blog/` tree agree.
That is the right question after a publish and the wrong one before it: it
compares two things that are both already here, and says nothing about the build
sitting in a worktree waiting to be copied in.

The question this asks is the other one. A build is about to overwrite
`assets/`; does every slug the live bundle serves still exist in the new one?

Written after a publish where the answer was not obvious. The blog index in the
source tree listed 19 entries and the deployed bundle served 36, so the source
looked as though it had lost seventeen posts. It had not -- the bundle carries
posts the index file alone does not account for -- but the only way to know was
to count slugs in both bundles and compare the sets. Doing that by hand, once,
before an irreversible copy, is not a procedure. This is.

Direction matters and is not symmetric. Slugs the new build ADDS are the point
of publishing. Slugs it DROPS are the damage, and dropping is silent: the copy
succeeds, the site keeps serving, and the posts are reachable only as 404s from
the feed and sitemap that still list them.

Usage:
  check-deploy-loses-nothing.py <path-to-dist>     gate
  check-deploy-loses-nothing.py --history          replay past deploys
  check-deploy-loses-nothing.py --self-check       negative control

Exits non-zero if any deployed slug is absent from the candidate build.
"""
import glob
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent

# Two shapes, because the bundler emits both: `slug:"..."` in the index the app
# renders from, and `"...":{body:` in the map from slug to article body. Reading
# only one of them would undercount, and an undercount here reads as a LOSS --
# the gate would fail a publish that drops nothing, which is the failure mode
# that gets a gate switched off.
SLUG_PATTERNS = (r'slug:"([a-z0-9][a-z0-9\-]{7,})"', r'"([a-z0-9][a-z0-9\-]{11,})":\{body:')


def slugs_in(paths):
    text = "".join(
        pathlib.Path(p).read_text(errors="replace") for p in paths
    )
    out = set()
    for pat in SLUG_PATTERNS:
        out |= set(re.findall(pat, text))
    return out


def blog_chunks(root):
    """Blog-*.js chunks the page can actually REACH, walking from index.html.

    The first version took every chunk on disk, and today that happens to give
    the same answer: 16 chunks in the apex, one reachable, and the reachable one
    carries all 48 slugs. By luck, not by construction.

    The luck runs out in exactly the shape this gate exists to catch. rsync is
    additive, so a deploy leaves the previous chunk beside the new one; a slug
    dropped from the new chunk still SITS on disk in the old one, and a
    disk-wide read reports it as live while the site 404s it. The orphan prune
    that follows a deploy then deletes the old chunk and the slug is gone for
    good -- which is how eleven posts left this site on 2026-08-21.

    So: reachability, not presence. Falling back to every chunk when there is no
    index.html is deliberate and narrow -- a dist without one is not a site, and
    reporting nothing at all there would be a silent pass.
    """
    root = str(root)
    index = os.path.join(root, "index.html")
    every = sorted(glob.glob(os.path.join(root, "assets", "Blog-*.js")))
    if not os.path.exists(index):
        return every

    seen, queue = set(), re.findall(
        r"assets/index-[A-Za-z0-9_-]+\.js",
        pathlib.Path(index).read_text(errors="replace"))
    while queue:
        rel = queue.pop()
        if rel in seen:
            continue
        seen.add(rel)
        f = pathlib.Path(root) / rel
        if not f.exists():
            continue
        for ref in re.findall(r"[\"'(]\./([A-Za-z0-9_.-]+\.js)[\"')]",
                              f.read_text(errors="replace")):
            queue.append("assets/" + ref)
    return sorted(os.path.join(root, s) for s in seen if re.search(r"Blog-.*\.js$", s))


def compare(deployed_root, candidate_dist):
    live = slugs_in(blog_chunks(deployed_root))
    new = slugs_in(blog_chunks(candidate_dist))
    return live, new, sorted(live - new), sorted(new - live)


def replay_history(limit=None):
    """Walk this repo's own deploys and report every one that dropped a slug.

    The gate above answers for a build in hand. This answers for the ones
    already pushed, and it is how the gate first went red on real data: three
    transitions in 160 commits dropped slugs, two recovered on the next deploy,
    and one did not -- eleven posts absent from the live site for two days.

    Slugs are read from every Blog-*.js at each commit, not the newest, because
    orphaned chunks from earlier deploys sit beside the current one and picking
    by name would compare against whichever sorted first.
    """
    def sh(*a):
        return subprocess.run(a, cwd=str(HERE), capture_output=True, text=True).stdout

    rows = sh("git", "log", "--format=%H|%cd|%s", "--date=short", "--", "assets/")
    commits = list(reversed(rows.strip().splitlines()))
    if limit:
        commits = commits[-limit:]

    def slugs_at(sha):
        names = [n for n in sh("git", "ls-tree", "-r", "--name-only", sha).splitlines()
                 if re.match(r"assets/Blog-.*\.js$", n)]
        if not names:
            return None
        text = "".join(sh("git", "show", f"{sha}:{n}") for n in names)
        out = set()
        for pat in SLUG_PATTERNS:
            out |= set(re.findall(pat, text))
        return out

    prev = prev_meta = None
    drops = []
    seen = 0
    for row in commits:
        sha, date, subj = row.split("|", 2)
        s = slugs_at(sha)
        if s is None:
            continue
        seen += 1
        if prev is not None and (prev - s):
            drops.append((prev_meta, (sha[:7], date, subj), sorted(prev - s)))
        prev, prev_meta = s, (sha[:7], date, subj)

    live = slugs_in(blog_chunks(HERE))
    print(f"replayed {seen} deploy(s) carrying a bundle, of {len(commits)} commits touching assets/")
    if not drops:
        print("OK: no deploy in this history dropped a slug")
        return 0
    print(f"\n{len(drops)} deploy(s) dropped at least one slug:\n")
    unrecovered = 0
    for before, after, lost in drops:
        still = [s for s in lost if s not in live]
        unrecovered += bool(still)
        print(f"  {after[1]}  {after[0]}  {after[2][:64]}")
        print(f"      dropped {len(lost)}: {', '.join(lost[:4])}{' ...' if len(lost) > 4 else ''}")
        print(f"      still missing today: {len(still)}"
              + (f"  <-- LIVE LOSS" if still else "  (recovered by a later deploy)"))
    # A drop that a later deploy healed is history; one that did not is damage
    # sitting on the site right now, and only the second is worth an exit code.
    return 1 if unrecovered else 0


def self_check():
    """Plant a build that drops a post; prove this says so. Then one that adds."""
    ok = True

    def case(label, live_slugs, new_slugs, want_rc, want_text, absent):
        nonlocal ok
        with tempfile.TemporaryDirectory() as td:
            t = pathlib.Path(td)
            for name, slugs in (("deployed", live_slugs), ("dist", new_slugs)):
                (t / name / "assets").mkdir(parents=True)
                body = "".join('slug:"%s",' % s for s in slugs)
                (t / name / "assets" / "Blog-planted.js").write_text(body)
                # A real index.html and a real entry chunk, so the cases run the
                # reachability walk rather than the no-index fallback. Planting
                # only the chunk would test the fallback and call it the gate.
                (t / name / "assets" / "index-planted.js").write_text(
                    'import "./Blog-planted.js";')
                (t / name / "index.html").write_text(
                    '<script src="assets/index-planted.js"></script>')
            r = subprocess.run(
                [sys.executable, str(pathlib.Path(__file__).resolve()),
                 str(t / "dist"), "--deployed", str(t / "deployed")],
                capture_output=True, text=True,
            )
        said = want_text in r.stdout
        leaked = [a for a in absent if a in r.stdout]
        good = r.returncode == want_rc and said and not leaked
        print("  %-34s %s" % (label, "exit %d, says it" % want_rc if good else "CONTROL FAILED"))
        if not good:
            ok = False
            print("       exit %r (want %r); %r present: %s" % (r.returncode, want_rc, want_text, said))
            if leaked:
                print("       neighbouring marker leaked: %r" % (leaked,))
            print("       said   %r" % (r.stdout[:300],))

    # The damage. One slug served today, absent from the build about to land.
    case("a dropped post is caught",
         ["kept-post-one", "dropped-post-two"], ["kept-post-one"],
         1, "1 slug(s) the live site serves are NOT in this build",
         ("no post is lost",))

    # The normal case, and it must be silent about loss or the gate is noise.
    case("an added post is not a loss",
         ["kept-post-one"], ["kept-post-one", "brand-new-post-here"],
         0, "no post is lost", ("NOT in this build",))

    # Equal sets: a rebuild with no content change must also pass.
    case("an unchanged set passes",
         ["kept-post-one"], ["kept-post-one"],
         0, "no post is lost", ("NOT in this build",))

    # T108: the orphan. rsync is additive, so yesterday's chunk sits beside
    # today's; a slug dropped from the reachable chunk is still ON DISK in the
    # unreachable one. Reading every chunk reports it live while the site 404s
    # it -- and the prune that follows a deploy then deletes the orphan and the
    # post is gone. That is the exact shape of the 2026-08-21 loss, so it gets a
    # case rather than a sentence.
    def orphan_case():
        nonlocal ok
        with tempfile.TemporaryDirectory() as td:
            t = pathlib.Path(td)
            for name in ("deployed", "dist"):
                (t / name / "assets").mkdir(parents=True)
                (t / name / "assets" / "Blog-current.js").write_text('slug:"kept-post-one",')
                (t / name / "assets" / "index-planted.js").write_text('import "./Blog-current.js";')
                (t / name / "index.html").write_text(
                    '<script src="assets/index-planted.js"></script>')
            # Only the deployed side carries the orphan, and nothing links it.
            (t / "deployed" / "assets" / "Blog-orphan.js").write_text('slug:"orphaned-post-two",')
            r = subprocess.run(
                [sys.executable, str(pathlib.Path(__file__).resolve()),
                 str(t / "dist"), "--deployed", str(t / "deployed")],
                capture_output=True, text=True)
        # The orphaned slug is NOT served, so its absence from the build is not
        # a loss. Counting it would red every publish after any prune-less
        # deploy, and a gate that cries wolf is a gate nobody runs.
        good = r.returncode == 0 and "no post is lost" in r.stdout \
            and "orphaned-post-two" not in r.stdout
        print("  %-34s %s" % ("an unreachable chunk is not live",
                              "exit 0, ignores it" if good else "CONTROL FAILED"))
        if not good:
            ok = False
            print("       exit %r; said %r" % (r.returncode, r.stdout[:300]))
    orphan_case()

    # --history has its own two directions, and it needs them more than the
    # cases above: when it first ran on real data it printed "still missing
    # today: 0" for all three drops -- correct, because the loss had just been
    # repaired -- and a mode whose only observed output is green has not been
    # shown to go red. Planted as a real git repository, because the replay
    # reads `git log` and `git ls-tree` and a stub would test the stub.
    def history_case(label, deploys, worktree, want_rc, want_text, absent):
        nonlocal ok
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / "assets").mkdir(parents=True)
            me = root / pathlib.Path(__file__).name
            me.write_text(pathlib.Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
            env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
            subprocess.run(["git", "init", "-q"], cwd=root, capture_output=True)
            for i, slugs in enumerate(deploys):
                (root / "assets" / "Blog-planted.js").write_text(
                    "".join('slug:"%s",' % s for s in slugs))
                subprocess.run(["git", "add", "-A", "-f"], cwd=root, capture_output=True)
                subprocess.run(["git", "commit", "-q", "-m", f"deploy {i}"],
                               cwd=root, capture_output=True, env=env)
            # The working tree decides "still missing today", so it is set last
            # and independently of the final commit.
            (root / "assets" / "Blog-planted.js").write_text(
                "".join('slug:"%s",' % s for s in worktree))
            r = subprocess.run([sys.executable, str(me), "--history"],
                               capture_output=True, text=True)
        said = want_text in r.stdout
        leaked = [a for a in absent if a in r.stdout]
        good = r.returncode == want_rc and said and not leaked
        print("  %-34s %s" % (label, "exit %d, says it" % want_rc if good else "CONTROL FAILED"))
        if not good:
            ok = False
            print("       exit %r (want %r); %r present: %s" % (r.returncode, want_rc, want_text, said))
            if leaked:
                print("       neighbouring marker leaked: %r" % (leaked,))
            print("       said   %r" % (r.stdout[:400],))

    # A drop still absent from the working tree: damage sitting on the site.
    history_case("history: an unhealed drop is red",
                 [["kept-post-one", "dropped-post-two"], ["kept-post-one"]],
                 ["kept-post-one"],
                 1, "<-- LIVE LOSS", ("no deploy in this history dropped",))

    # The same drop, healed by a later deploy. History, not damage -- and the
    # exit code must say so, or every past incident reds the gate forever.
    history_case("history: a healed drop is green",
                 [["kept-post-one", "dropped-post-two"], ["kept-post-one"],
                  ["kept-post-one", "dropped-post-two"]],
                 ["kept-post-one", "dropped-post-two"],
                 0, "(recovered by a later deploy)", ("<-- LIVE LOSS",))

    # And a history with no drop at all must not invent one.
    history_case("history: a clean history is silent",
                 [["kept-post-one"], ["kept-post-one", "brand-new-post-here"]],
                 ["kept-post-one", "brand-new-post-here"],
                 0, "no deploy in this history dropped a slug", ("LIVE LOSS", "dropped 1"))

    # A build with NO chunks at all reads as dropping everything, and that is
    # the correct answer rather than an error: a dist that lost its Blog chunk
    # is exactly the copy that must not happen. Asserted because the empty case
    # is the one a set-difference silently gets right or silently gets wrong.
    case("an empty build drops everything",
         ["kept-post-one", "dropped-post-two"], [],
         1, "2 slug(s) the live site serves are NOT in this build",
         ("no post is lost",))
    return 0 if ok else 1


def main(argv):
    if "--self-check" in argv:
        return self_check()
    if "--history" in argv:
        return replay_history()
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__.strip().splitlines()[-4])
        return 2
    candidate = pathlib.Path(args[0])
    deployed = pathlib.Path(argv[argv.index("--deployed") + 1]) if "--deployed" in argv else HERE

    if not blog_chunks(candidate):
        # Not an error on its own -- see the empty-build case in the control.
        print(f"note: no Blog-*.js under {candidate}/assets")

    live, new, lost, added = compare(deployed, candidate)
    if lost:
        print(f"FAIL: {len(lost)} slug(s) the live site serves are NOT in this build\n")
        for s in lost:
            print(f"  {s}")
        print("\n  Copying this build over assets/ would leave these reachable only")
        print("  as 404s from the feed and sitemap that still list them. Rebuild")
        print("  from a source tree that still carries them before publishing.")
        return 1
    print(f"OK: no post is lost — live serves {len(live)}, this build carries "
          f"{len(new)}, {len(added)} new")
    for s in added:
        print(f"  + {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
