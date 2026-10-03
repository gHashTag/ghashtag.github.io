#!/usr/bin/env python3
"""Tell search engines which pages a publish changed (IndexNow).

The key file has been served at the site root for a while
(/<32 hex>.txt, its content equal to its name), and nothing ever sent a URL:
a page published here waited for a crawler to come back on its own schedule,
which for a small site is days. IndexNow is one POST that Bing, Yandex, Seznam,
Naver and Yep share; a URL sent to one is passed to the others.

Which URLs: the pages the publish commit touched, and only those the sitemap
lists. The sitemap is the list of URLs this site wants indexed (verify-site.sh
holds every one of them to a self-canonical, indexable page), so a file that
changed but is not on it -- an asset, a feed, a redirect stub -- is not sent.

    python3 indexnow.py --self-test          checks, no network
    python3 indexnow.py --dry-run            print what would be sent
    python3 indexnow.py                      send the pages HEAD changed
    python3 indexnow.py --since <rev>        send the pages changed since <rev>
    python3 indexnow.py --all                send every sitemap URL (once, by hand)

Exit 0 when the engines accepted the list or there was nothing to send, 1 when
the request failed. The publisher runs this after the push and reports a failure
as a warning: the pages are already live, and a missed ping only means they are
found at the crawler's own pace, as before.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOST = "t27.ai"
SITE = f"https://{HOST}/"
ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10_000  # the protocol's limit per request
KEY_NAME = re.compile(r"^[0-9a-f]{32}\.txt$")


def find_key(root: Path) -> str:
    """The one key file at the root whose content is its own name."""
    keys = [p.stem for p in sorted(root.iterdir())
            if KEY_NAME.match(p.name) and p.read_text(encoding="utf-8").strip() == p.stem]
    if len(keys) != 1:
        raise SystemExit(f"expected one IndexNow key file at the root, found {len(keys)}: {keys}")
    return keys[0]


def sitemap_urls(text: str) -> list[str]:
    return re.findall(r"<loc>([^<]*)</loc>", text)


def url_of(path: str) -> str | None:
    """The page URL a changed file is, or None if it is not a page."""
    if path == "index.html":
        return SITE
    if path.endswith("/index.html"):
        return SITE + path[: -len("index.html")]
    return None


def changed_pages(changed: list[str], listed: list[str]) -> list[str]:
    wanted = set(listed)
    urls = {url_of(p) for p in changed}
    return sorted(u for u in urls if u in wanted)


def git_changed(since: str) -> list[str]:
    out = subprocess.run(["git", "diff", "--name-only", since, "HEAD"],
                         cwd=REPO, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def payload(key: str, urls: list[str]) -> dict:
    return {"host": HOST, "key": key, "keyLocation": f"{SITE}{key}.txt", "urlList": urls[:MAX_URLS]}


def send(body: dict) -> int:
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"IndexNow: no answer from {ENDPOINT}: {e}")
        return 1
    # 200 accepted, 202 accepted and the key is still being checked.
    if status in (200, 202):
        print(f"IndexNow: {len(body['urlList'])} URL(s) accepted ({status})")
        return 0
    print(f"IndexNow: refused with HTTP {status} for {len(body['urlList'])} URL(s)")
    return 1


def self_test() -> int:
    import tempfile
    listed = [SITE, f"{SITE}blog/", f"{SITE}blog/a-post/", f"{SITE}ru/"]
    assert url_of("index.html") == SITE
    assert url_of("blog/a-post/index.html") == f"{SITE}blog/a-post/"
    assert url_of("assets/index-abc.js") is None
    assert url_of("blog/feed.xml") is None
    got = changed_pages(["index.html", "blog/a-post/index.html", "assets/x.js",
                         "leela/classic/index.html", "og-blog.png"], listed)
    assert got == [SITE, f"{SITE}blog/a-post/"], got
    assert changed_pages(["sitemap.xml", "og-image.png"], listed) == [], "no page changed, nothing sent"
    body = payload("0" * 32, [f"{SITE}{i}/" for i in range(MAX_URLS + 5)])
    assert len(body["urlList"]) == MAX_URLS and body["keyLocation"] == f"{SITE}{'0' * 32}.txt"
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        good = "a" * 32
        (root / f"{good}.txt").write_text(good + "\n")
        assert find_key(root) == good
        (root / f"{'b' * 32}.txt").write_text("not the name")  # a stray file is not a key
        assert find_key(root) == good
        (root / f"{'c' * 32}.txt").write_text("c" * 32)
        try:
            find_key(root)
        except SystemExit as e:
            assert "found 2" in str(e)
        else:
            raise AssertionError("two keys must stop the send: which one the engines checked is a guess")
    assert find_key(REPO), "this repository serves exactly one key"
    print("indexnow self-test: ok")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    key = find_key(REPO)
    listed = sitemap_urls((REPO / "sitemap.xml").read_text(encoding="utf-8"))
    if "--all" in argv:
        urls = listed
    else:
        since = argv[argv.index("--since") + 1] if "--since" in argv else "HEAD~1"
        urls = changed_pages(git_changed(since), listed)
    if not urls:
        print("IndexNow: no sitemap page changed, nothing to send")
        return 0
    body = payload(key, urls)
    if "--dry-run" in argv:
        print(json.dumps(body, indent=1))
        return 0
    return send(body)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
