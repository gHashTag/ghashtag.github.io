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
    """Every Blog-*.js under root/assets.

    All of them, not the newest. Earlier deploys leave orphaned chunks behind,
    and picking one by mtime would compare against whichever the filesystem
    happened to order first.
    """
    return sorted(glob.glob(os.path.join(str(root), "assets", "Blog-*.js")))


def compare(deployed_root, candidate_dist):
    live = slugs_in(blog_chunks(deployed_root))
    new = slugs_in(blog_chunks(candidate_dist))
    return live, new, sorted(live - new), sorted(new - live)


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
