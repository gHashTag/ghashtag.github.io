#!/usr/bin/env python3
"""t27.ai blog syndication pipeline.

Cross-posts every new post from blog-posts.json to the channels configured in
~/.config/t27-syndicate/config.json. State lives in
~/.config/t27-syndicate/state.json; confirmed post/channel pairs are skipped.
Live runs are locked and each confirmed result is saved atomically. An ambiguous
API response still needs reconciliation before retrying.

Best practices baked in (SEO / traffic):
  - canonical link + "originally published at" line at the top of every
    cross-post, so t27.ai stays the canonical source in search engines;
  - UTM-tagged links to attribute traffic and conversions per channel;
  - the site's original article art is reused as the channel cover where the
    API allows; posts without a bespoke og-art JPG use their generated OG card;
  - tags are mapped per channel (dev.to: max 4 tags, lowercase).

Channels (enable by filling their token in the config; missing tokens are
skipped unless that channel was explicitly selected):
  telegram  — Telegram channel via bot (sendPhoto + caption + link)
  devto     — dev.to API (draft by default, review then flip)
  hashnode  — Hashnode GraphQL API (draft by default)
  medium    — Medium API (draft by default; Medium has no image upload)

Usage:
  syndicate.py                 # syndicate all unposted posts
  syndicate.py --dry-run       # show what would be posted, touch nothing
  syndicate.py --limit 1       # only the newest unposted post
  syndicate.py --slug example --channel telegram  # one exact article/channel
  syndicate.py --status        # print state table
"""
import argparse
from contextlib import contextmanager
import fcntl
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path

import requests

SITE = "https://t27.ai"
REPO = Path(__file__).resolve().parents[2]  # ghashtag.github.io checkout
CONFIG_PATH = Path.home() / ".config/t27-syndicate/config.json"
STATE_PATH = Path.home() / ".config/t27-syndicate/state.json"

VALID_CHANNELS = ("telegram", "devto", "hashnode", "medium", "indexnow")

# Outbound requests may only hit these hosts over https.
ALLOWED_HOSTS = {
    "api.telegram.org",
    "dev.to",
    "gql.hashnode.com",
    "api.medium.com",
    "api.indexnow.org",
}


def _assert_safe_url(url):
    """Only https to an allow-listed public host; block SSRF targets."""
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or not p.hostname:
        raise ValueError(f"blocked url (scheme/host): {url}")
    host = p.hostname.lower()
    if host not in ALLOWED_HOSTS:
        raise ValueError(f"blocked url (host not allow-listed): {host}")
    for fam, _, _, _, sa in socket.getaddrinfo(host, 443):
        ip = sa[0]
        if fam == socket.AF_INET6:
            ip = ip.split("%")[0]
        addr = ipaddress.ip_address(ip)
        if not addr.is_global:
            raise ValueError(f"blocked url (non-global address): {host} -> {ip}")


def http_get(url, **kw):
    _assert_safe_url(url)
    return requests.get(url, timeout=30, **kw)


def http_post(url, **kw):
    _assert_safe_url(url)
    return requests.post(url, timeout=30, **kw)


def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


class StateLockError(RuntimeError):
    pass


@contextmanager
def state_lock(path):
    """Hold one stable lock inode from state read through the last save."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    with lock_path.open("a") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise StateLockError("another syndication run holds the state lock") from exc
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    # Do not unlink: a waiter may still have the old inode open.


def save_state(path, state):
    """Replace the legacy JSON map only after the entire new file is flushed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_config():
    cfg = load_json(CONFIG_PATH, {})
    channels = cfg.get("channels", {})
    unknown = set(channels) - set(VALID_CHANNELS)
    if unknown:
        sys.exit(f"config error: unknown channel(s) {sorted(unknown)}; valid: {VALID_CHANNELS}")
    ep = channels.get("hashnode", {}).get("endpoint")
    if ep and urllib.parse.urlsplit(ep).hostname not in ALLOWED_HOSTS:
        sys.exit(f"config error: hashnode endpoint host not allow-listed: {ep}")
    return cfg


def utm(url, channel):
    q = urllib.parse.urlencode({
        "utm_source": channel, "utm_medium": "crosspost", "utm_campaign": "t27-blog",
    })
    return f"{url}?{q}"


def canonical_block(post, channel):
    """First lines of every cross-post: canonical source + CTA back to the site."""
    url = utm(f"{SITE}/blog/{post['slug']}/", channel)
    return (
        f"*{post['title']}*\n\n{post['summary']}\n\n"
        f"Originally published at {url} — measured results on the ternary "
        f"datapath, every post names what is not proven."
    )


def hashtag(tag):
    """Convert a taxonomy label to the same hashtag shown on t27.ai."""
    words = re.findall(r"[^\W_]+", str(tag).lstrip("#"), flags=re.UNICODE)
    if not words:
        raise ValueError(f"invalid empty tag: {tag!r}")
    if len(words) == 1:
        return f"#{words[0]}"
    return "#" + "".join(
        word if word.isupper() else word[:1].upper() + word[1:]
        for word in words
    )


def social_hashtags(post, limit=3):
    tags = post.get("tags") or []
    if not tags:
        raise ValueError(f"post {post.get('slug', '?')} has no mandatory tags")
    return " ".join(hashtag(tag) for tag in tags[:limit])


def extract_markdown(post):
    """Article body HTML -> markdown, using the page the site actually serves."""
    html = (REPO / "blog" / post["slug"] / "index.html").read_text()
    m = re.search(r"<article[^>]*>(.*?)</article>", html, re.S)
    body = m.group(1) if m else html
    import html2text
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_images = False
    return h.handle(body)


def cover_url(post):
    slug = post["slug"]
    if (REPO / "og-art" / f"{slug}.jpg").is_file():
        return f"{SITE}/og-art/{slug}.jpg"
    generated = REPO / f"og-blog-{slug}.png"
    if not generated.is_file():
        raise FileNotFoundError(f"no syndication cover for {slug}")
    return f"{SITE}/og-blog-{slug}.png"


# --- channels ---------------------------------------------------------------

def tg_escape(text):
    """Escape legacy-Markdown specials so a stray * _ ` [ in a post cannot
    break the whole sendPhoto request."""
    return re.sub(r"([_*`\[])", r"\\\1", text)


def ru_meta(post):
    """RU title/summary from the ru page the site ships; None if absent."""
    path = REPO / "ru" / "blog" / post["slug"] / "index.html"
    try:
        html = path.read_text()
    except FileNotFoundError:
        return None
    title = re.search(r'property="og:title" content="([^"]*)"', html)
    desc = re.search(r'property="og:description" content="([^"]*)"', html)
    if not title or not desc:
        return None
    import html as htmlmod
    return (htmlmod.unescape(title.group(1)), htmlmod.unescape(desc.group(1)))


def post_telegram(post, ch, dry):
    """@t27_lang is a Russian-language channel with a '[измерено]' house style;
    post the RU version when the site ships one, English otherwise."""
    token, chat = ch["bot_token"], ch["chat_id"]
    ru = ru_meta(post)
    title, summary, tail = tg_escape(post["title"]), tg_escape(post["summary"]), ""
    if ru:
        title, summary = tg_escape(ru[0]), tg_escape(ru[1])
        tail = " — измеренные результаты по троичному тракту данных; в каждом посте названо, что не доказано."
        link = utm(f"{SITE}/ru/blog/{post['slug']}/", "telegram")
    else:
        link = utm(f"{SITE}/blog/{post['slug']}/", "telegram")
    tag_suffix = f"\n\n{social_hashtags(post)}"
    if dry:
        return {"ok": True, "dry": True, "id": None, "lang": "ru" if ru else "en"}
    body = f"*[измерено] {title}*\n\n{summary}\n\n[Читать]({link}){tail}"
    caption = body[:1024 - len(tag_suffix)].rstrip() + tag_suffix
    r = http_post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        json={"chat_id": chat, "photo": cover_url(post),
              "caption": caption, "parse_mode": "Markdown"},
    )
    if not r.ok:
        raise RuntimeError(f"telegram HTTP {r.status_code}: "
                           f"{r.json().get('description', r.text[:150])}")
    return {"ok": True, "id": r.json()["result"]["message_id"]}
    r = http_post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        json={"chat_id": chat, "photo": cover_url(post),
              "caption": caption, "parse_mode": "Markdown"},
    )
    if not r.ok:
        raise RuntimeError(f"telegram HTTP {r.status_code}: "
                           f"{r.json().get('description', r.text[:150])}")
    return {"ok": True, "id": r.json()["result"]["message_id"]}


def post_devto(post, ch, dry):
    tags = [t.lower().replace(" ", "")[:30] for t in post.get("tags", [])][:4]
    md = canonical_block(post, "devto") + "\n\n---\n\n" + extract_markdown(post)
    body = {"article": {"title": post["title"], "published": ch.get("publish", False),
                        "body_markdown": md, "main_image": cover_url(post),
                        "tags": tags, "canonical_url": f"{SITE}/blog/{post['slug']}/"}}
    if dry:
        return {"ok": True, "dry": True, "id": None}
    r = http_post("https://dev.to/api/articles", json=body,
                  headers={"api-key": ch["api_key"]})
    r.raise_for_status()
    return {"ok": True, "id": r.json()["id"], "url": r.json().get("url")}


def post_hashnode(post, ch, dry):
    tags = [{"slug": re.sub(r"[^a-z0-9-]", "", t.lower().replace(" ", "-")), "name": t}
            for t in post.get("tags", [])[:5]]
    tags = [t for t in tags if t["slug"]]
    if not tags:
        tags = [{"slug": "engineering", "name": "Engineering"}]
    md = canonical_block(post, "hashnode") + "\n\n---\n\n" + extract_markdown(post)
    query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) { draft { id slug } }
    }"""
    variables = {"input": {
        "title": post["title"], "subtitle": post["summary"][:250],
        "contentMarkdown": md, "tags": tags,
        "canonicalUrl": f"{SITE}/blog/{post['slug']}/",
        "coverImage": {"url": cover_url(post)},
    }}
    if dry:
        return {"ok": True, "dry": True, "id": None}
    r = http_post(ch.get("endpoint", "https://gql.hashnode.com"),
                  json={"query": query, "variables": variables},
                  headers={"Authorization": ch["token"]})
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"hashnode: {data['errors']}")
    return {"ok": True, "id": data["data"]["createDraft"]["draft"]["id"]}


def ping_indexnow(post, ch, dry):
    """Tell participating search engines (Bing, Yandex, ...) about the new URLs.

    The key file <key>.txt lives at the site root; IndexNow verifies it at
    https://t27.ai/<key>.txt before accepting submissions.
    """
    key = ch["key"]
    urls = [f"{SITE}/blog/{post['slug']}/", f"{SITE}/ru/blog/{post['slug']}/",
            f"{SITE}/rss.xml"]
    if dry:
        return {"ok": True, "dry": True, "urls": urls}
    r = http_post("https://api.indexnow.org/indexnow",
                  json={"host": "t27.ai", "key": key, "keyLocation":
                        f"{SITE}/{key}.txt", "urlList": urls})
    # 202 = accepted, 400 = bad key/urls, 422 = key file not verifiable yet
    if r.status_code not in (200, 202):
        raise RuntimeError(f"indexnow HTTP {r.status_code}: {r.text[:200]}")
    return {"ok": True, "urls": urls}


def post_medium(post, ch, dry):
    md = canonical_block(post, "medium") + "\n\n---\n\n" + extract_markdown(post)
    if dry:
        return {"ok": True, "dry": True, "id": None}
    me = http_get("https://api.medium.com/v1/me",
                  headers={"Authorization": f"Bearer {ch['token']}"})
    me.raise_for_status()
    uid = me.json()["data"]["id"]
    r = http_post(
        f"https://api.medium.com/v1/users/{uid}/posts",
        json={"title": post["title"], "contentFormat": "markdown", "content": md,
              "canonicalUrl": f"{SITE}/blog/{post['slug']}/",
              "publishStatus": "draft", "tags": [t.lower() for t in post.get("tags", [])][:5]},
        headers={"Authorization": f"Bearer {ch['token']}"},
    )
    r.raise_for_status()
    return {"ok": True, "id": r.json()["data"]["id"]}


REQUIRED = {"telegram": ["bot_token", "chat_id"], "devto": ["api_key"],
            "hashnode": ["token"], "medium": ["token"], "indexnow": ["key"]}
POSTERS = {"telegram": post_telegram, "devto": post_devto,
           "hashnode": post_hashnode, "medium": post_medium,
           "indexnow": ping_indexnow}


def channel_enabled(name, ch):
    return all(ch.get(k) for k in REQUIRED[name])


PROFILE_REPO = "gHashTag/gHashTag"
PROFILE_START = "<!-- t27-latest-posts:start -->"
PROFILE_END = "<!-- t27-latest-posts:end -->"
PROFILE_ANCHOR = "## 📄 Papers"


def update_profile(posts, dry):
    """Keep a 'Latest posts' block in the GitHub profile README in sync.

    The block is delimited by HTML comment markers; content between them is
    regenerated from the 3 newest blog posts. Updated via the GitHub contents
    API using the local gh CLI auth. No-op when content is unchanged.
    """
    top = sorted(posts, key=lambda p: p["date"], reverse=True)[:3]
    lines = [PROFILE_START, "",
             "## 📝 Latest posts — [t27.ai/blog](https://t27.ai/#/blog)", ""]
    for p in top:
        link = utm(f"{SITE}/blog/{p['slug']}/", "github-profile")
        s = p["summary"][:180]
        s = s[:s.rfind(" ")] if len(p["summary"]) > 180 else s
        lines.append(f"- **[{p['title']}]({link})** ({p['date']}) — {s}…")
    lines += ["", PROFILE_END]
    section = "\n".join(lines)

    cur = subprocess.run(
        ["gh", "api", f"repos/{PROFILE_REPO}/contents/README.md", "-q", ".content"],
        capture_output=True, text=True, check=True).stdout
    import base64
    readme = base64.b64decode(cur).decode()

    if PROFILE_START in readme:
        new = re.sub(re.escape(PROFILE_START) + r".*?" + re.escape(PROFILE_END),
                     section, readme, flags=re.S)
    elif PROFILE_ANCHOR in readme:
        new = readme.replace(PROFILE_ANCHOR, section + "\n---\n\n" + PROFILE_ANCHOR, 1)
    else:
        new = readme + "\n\n" + section + "\n"
    if new == readme:
        print("profile README already up to date")
        return

    if dry:
        print("profile README would be updated with:\n" + section)
        return
    sha = subprocess.run(
        ["gh", "api", f"repos/{PROFILE_REPO}/contents/README.md", "-q", ".sha"],
        capture_output=True, text=True, check=True).stdout.strip()
    import base64 as b64
    subprocess.run(
        ["gh", "api", "--method", "PUT", f"repos/{PROFILE_REPO}/contents/README.md",
         "-f", f"message=chore: refresh latest blog posts (auto)",
         "-f", f"sha={sha}",
         "-f", f"content={b64.b64encode(new.encode()).decode()}"],
        capture_output=True, text=True, check=True)
    print(f"profile README updated ({PROFILE_REPO})")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--slug", help="exact slug of one already-published article")
    ap.add_argument("--channel", choices=VALID_CHANNELS,
                    help="send only to this channel (all configured channels by default)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--update-profile", action="store_true",
                    help="refresh the Latest posts block in the GitHub profile README")
    args = ap.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        ap.error("--limit must be positive")
    if args.update_profile and (args.slug is not None or args.channel is not None):
        ap.error("--slug/--channel cannot be combined with --update-profile")

    posts = json.loads((REPO / "blog-posts.json").read_text())
    posts.sort(key=lambda p: p["date"])
    if args.slug is not None:
        posts = [p for p in posts if p["slug"] == args.slug
                 and p["date"] <= time.strftime("%Y-%m-%d")]
        if len(posts) != 1:
            ap.error(f"--slug must match exactly one published article: {args.slug!r}")

    if args.update_profile:
        update_profile(posts, args.dry_run)
        return 0

    cfg = load_config()
    posters = {args.channel: POSTERS[args.channel]} if args.channel else POSTERS
    if args.channel and not channel_enabled(
        args.channel, cfg.get("channels", {}).get(args.channel, {})
    ):
        ap.error(f"channel {args.channel!r} is not configured")

    if args.status:
        state = load_json(STATE_PATH, {})
        for name in posters:
            ch = cfg.get("channels", {}).get(name, {})
            print(f"{name:10} {'enabled' if channel_enabled(name, ch) else 'no token (skipped)'}")
        for slug, done in state.items():
            if args.slug is not None and slug != args.slug:
                continue
            done = {k: v for k, v in done.items() if k in posters}
            print(f"{slug[:60]:60} -> {', '.join(f'{k}:{v}' for k, v in done.items()) or '-'}")
        return 0

    if args.dry_run:
        return syndicate(posts, posters, cfg, load_json(STATE_PATH, {}), args)
    try:
        with state_lock(STATE_PATH):
            # Read after acquiring the lock, never before another writer finishes.
            return syndicate(posts, posters, cfg, load_json(STATE_PATH, {}), args)
    except (StateLockError, OSError) as exc:
        print(f"syndication stopped: {exc}", file=sys.stderr)
        return 1


def syndicate(posts, posters, cfg, state, args):

    # only posts dated today or earlier; a future-dated post waits for its date
    todo = [p for p in posts
            if p["date"] <= time.strftime("%Y-%m-%d")
            and any(name not in state.get(p["slug"], {}) for name in posters)]
    # drip order: posts not yet in the Telegram channel come first (newest of
    # them first), so --limit advances the backlog instead of re-picking posts
    # that only lack optional token channels
    fresh = sorted((p for p in todo if "telegram" not in state.get(p["slug"], {})),
                   key=lambda p: p["date"], reverse=True)
    rest = [p for p in todo if p not in fresh]
    todo = fresh + rest
    if args.limit:
        todo = todo[:args.limit]

    if not todo:
        print("nothing to syndicate")
        return 0

    failed = False
    for post in todo:
        slug = post["slug"]
        for name, poster in posters.items():
            if name in state.get(slug, {}):
                continue
            ch = cfg.get("channels", {}).get(name, {})
            if not channel_enabled(name, ch):
                # not recorded in state: once a token is added, past posts retry
                print(f"[{slug}] {name}: skipped (no token)")
                continue
            try:
                res = poster(post, ch, args.dry_run)
                if not res.get("ok"):
                    raise RuntimeError("channel did not confirm success")
            except Exception as e:  # noqa: BLE001 — one channel failing must not stop others
                failed = True
                msg = re.sub(r"bot\d+:[\w-]+", "bot***", str(e))  # never leak tokens
                print(f"[{slug}] {name}: FAILED {msg}")
                continue
            if not args.dry_run:
                state.setdefault(slug, {})[name] = str(res.get("id") or res.get("url") or "ok")
                # A persistence failure must stop dispatch, not silently continue.
                save_state(STATE_PATH, state)
            print(f"[{slug}] {name}: {'dry-run ok' if args.dry_run else res}")
        print()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
