#!/usr/bin/env python3
"""Emit a public result page and a badge endpoint for every checked repository.

Why a page per repo rather than one gallery:

Coveralls and Codecov both put the result at a guessable, login-free URL —
coveralls.io/github/OWNER/REPO renders for anyone, and Codecov even labels the
anonymous view. The URL is the account. That is the one structural pattern from
those products a static site can copy in full, and it turns each run from a row
in somebody's gallery into a link the author can send to a reviewer.

The badge is the second half. Shields renders it from a JSON endpoint, so we
serve static JSON and they do the drawing: the badge then lives in the author's
README, on their traffic, pointing back here.

Reads apps/website/src/data/runs.json from the trinity checkout — the same file
the site imports, so a result cannot say one thing on the gallery and another on
its own page.

    python3 build-results.py            # writes r/<owner>/<repo>/index.html + badge.json
"""

import html
import json
import os
import sys
from pathlib import Path

SITE = "https://t27.ai"
HERE = Path(__file__).resolve().parent
RUNS_JSON = Path(
    os.environ.get(
        "RUNS_JSON",
        HERE.parent / "trinity" / "apps" / "website" / "src" / "data" / "runs.json",
    )
)

CSS = """*,*::before,*::after{box-sizing:border-box}
:root{--bg:#05070a;--card:#0b1014;--ink:#e9f1ee;--muted:#8fa79f;--accent:#00ff88;--rule:#1b2724}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:820px;margin:0 auto;padding:40px 20px 72px}
a{color:var(--accent)}
nav.top{font-size:14px;margin-bottom:28px}
nav.top a{margin-right:14px;color:var(--muted);text-decoration:none}
h1{font-size:clamp(1.6rem,4.5vw,2.2rem);line-height:1.2;margin:0 0 8px}
.sub{color:var(--muted);margin:0 0 4px}
.stamp{color:var(--muted);font-size:12px;margin:16px 0 28px;padding-top:12px;border-top:1px solid var(--rule)}
.check{border-top:1px solid var(--rule);padding:14px 0}
.pass{color:var(--accent);font-weight:700;font-size:12px;letter-spacing:.08em}
.fail{color:#ff6b6b;font-weight:700;font-size:12px;letter-spacing:.08em}
.check p{margin:6px 0 6px;font-size:14px}
code{font-size:12px;color:var(--muted);display:block;overflow-x:auto;white-space:pre}
.card{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:20px;margin:20px 0}
.badge{font-size:13px}
.badge pre{background:#0d1418;border:1px solid var(--rule);border-radius:8px;padding:10px;overflow-x:auto}
.limits li{font-size:14px;color:var(--muted);margin-bottom:6px}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--rule);color:var(--muted);font-size:13px}
@media(prefers-color-scheme:light){:root{--bg:#fbfdfc;--card:#fff;--ink:#101a17;--muted:#5b6f68;--accent:#0a7a4c;--rule:#dde7e3}}
"""

LIMITS = [
    "A pass is not a proof of correctness. These checks say the design elaborates, infers no latches, synthesises and contains clocked logic. None of them compares it against a specification.",
    "Generic yosys cells are not silicon area. Only the real ASIC flow settles whether a design fits its tiles.",
    "No frequency is claimed. Counting flip-flops says a frequency is a meaningful question, not what the answer is.",
    "Nothing here ran on hardware. These are simulation and synthesis results.",
]


def slug(run):
    """The path under /r/. Comes from runs.json, which computes it once.

    It must identify the DESIGN, not the repository: five of these chips live in
    two monorepos, and keying on owner/repo alone silently overwrote three of
    them — the generator reported five pages written and left two on disk.
    """
    s = run.get("slug")
    if not s:
        return None
    return s.strip("/")


def page(run, prov):
    sl = slug(run)
    url = f"{SITE}/r/{sl}/"
    owner_repo = "/".join(sl.split("/")[:2])
    passed = sum(1 for c in run["checks"] if c["status"] == "PASS")
    total = len(run["checks"])
    commit = prov["commits"].get(run.get("origin", ""), "")
    stamp = " · ".join(
        x for x in [
            owner_repo + (f" @ {commit}" if commit else ""),
            run.get("date", ""), prov["yosys"], prov["iverilog"],
        ] if x
    )
    checks = "\n".join(
        f'<div class="check"><span class="{"pass" if c["status"]=="PASS" else "fail"}">{c["status"]}</span> '
        f'<strong>{html.escape(c["name"])}</strong><p>{html.escape(c["detail"])}</p>'
        f'<code>{html.escape(c["command"])}</code></div>'
        for c in run["checks"]
    )
    found = (
        f'<div class="card"><strong>What it surfaced</strong><p>{html.escape(run["found"])}</p></div>'
        if run.get("found") else ""
    )
    badge_md = (
        f"[![t27.ai](https://img.shields.io/endpoint?url={SITE}/r/{sl}/badge.json)]({url})"
    )
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{html.escape(run['design'])} — verification result · TRINITY</title>
<meta name="description" content="{passed} of {total} structural checks passed for {html.escape(run['repo'])}, with the command that produced each one." />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="website" /><meta property="og:url" content="{url}" />
<meta property="og:title" content="{html.escape(run['design'])} — {passed}/{total} checks" />
<meta property="og:description" content="Structural verification of {html.escape(run['repo'])}, reproducible from the commands on this page." />
<meta property="og:image" content="{SITE}/og-verification.png" />
<meta name="twitter:card" content="summary_large_image" />
<style>{CSS}</style></head><body><div class="wrap">
<nav class="top"><a href="/">T27.AI</a><a href="/verification/">Verification</a><a href="/cases/">Case studies</a></nav>
<h1>{html.escape(run['design'])}</h1>
<p class="sub">{html.escape(run['what'])}</p>
<p class="sub"><a href="{run['repoUrl']}">{html.escape(run['repo'])}</a> · top <code style="display:inline">{html.escape(run['top'])}</code> · {passed} of {total} checks passed</p>
<p class="stamp">{html.escape(stamp)}</p>
{checks}
{found}
<div class="card badge"><strong>Badge</strong>
<p>Shields renders it from a static JSON file served here, so it stays current without anything running.</p>
<pre>{html.escape(badge_md)}</pre></div>
<div class="card"><strong>What this does not establish</strong>
<ul class="limits">{''.join(f'<li>{html.escape(l)}</li>' for l in LIMITS)}</ul></div>
<footer>Checked with the open flow — Yosys and Icarus Verilog, no vendor licence.
Re-run any line above yourself. <a href="{SITE}/verification/">How this works</a> ·
<a href="https://github.com/gHashTag/trinity/issues/new?template=verification-request.yml">Run your own repo</a></footer>
</div></body></html>
"""


def badge(run):
    passed = sum(1 for c in run["checks"] if c["status"] == "PASS")
    total = len(run["checks"])
    ok = passed == total
    return {
        "schemaVersion": 1,
        "label": "t27.ai",
        "message": f"{passed}/{total} checks",
        "color": "brightgreen" if ok else "orange",
    }


def main():
    if not RUNS_JSON.is_file():
        sys.exit(f"runs.json not found at {RUNS_JSON}; set RUNS_JSON to point at it")
    data = json.loads(RUNS_JSON.read_text(encoding="utf-8"))
    prov, runs = data["provenance"], data["runs"]
    written, seen = [], set()
    required = ("design", "repo", "repoUrl", "top", "what", "date", "checks")
    for run in runs:
        gaps = [k for k in required if k not in run]
        if gaps:
            sys.exit(f"  {run.get('id','?')}: runs.json is missing {gaps} — fix the source, do not paper over it")
        s = slug(run)
        if not s:
            print(f"  skipped {run['id']}: no slug")
            continue
        seen_before = s in seen
        seen.add(s)
        if seen_before:
            sys.exit(f"  two runs claim /r/{s}/ — a design would be silently overwritten")
        d = HERE / "r" / Path(s)
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(run, prov), encoding="utf-8")
        (d / "badge.json").write_text(json.dumps(badge(run)), encoding="utf-8")
        written.append(f"r/{s}/")
        print(f"  wrote r/{s}/  ({run['design']})")
    if not written:
        sys.exit("  nothing written — treat that as a failure, not a pass")
    print(f"  {len(written)} result page(s) + badge endpoint(s)")
    return written


if __name__ == "__main__":
    main()
