#!/usr/bin/env python3
"""t27.ai blog syndication pipeline.

Cross-posts every new post from blog-posts.json to the channels configured in
~/.config/t27-syndicate/config.json. State lives in
~/.config/t27-syndicate/state.json so each post is published to each channel
exactly once. Re-running is always safe: already-syndicated slugs are skipped.

Best practices baked in (SEO / traffic):
  - canonical link + "originally published at" line at the top of every
    cross-post, so t27.ai stays the canonical source in search engines;
  - UTM-tagged links to attribute traffic and conversions per channel;
  - the site's existing OG cover image (og-blog-<slug>.png, one visual style
    for the whole blog) is reused as the channel cover where the API allows;
  - tags are mapped per channel (dev.to: max 4 tags, lowercase).

Channels (enable by filling their token in the config; missing tokens are
skipped with a warning, never an error):
  telegram  — Telegram channel via bot (sendPhoto + caption + link)
  devto     — dev.to API (draft by default, review then flip)
  hashnode  — Hashnode GraphQL API (draft by default)
  medium    — Medium API (draft by default; Medium has no image upload)

Usage:
  syndicate.py                 # syndicate all unposted posts
  syndicate.py --dry-run       # show what would be posted, touch nothing
  syndicate.py --limit 1       # only the newest unposted post
  syndicate.py --status        # print state table
"""
import argparse
import ipaddress
import json
import re
import socket
import subprocess
import sys
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
    return f"{SITE}/og-blog-{post['slug']}.png"


# --- channels ---------------------------------------------------------------

def tg_escape(text):
    """Escape legacy-Markdown specials so a stray * _ ` [ in a post cannot
    break the whole sendPhoto request."""
    return re.sub(r"([_*`\[])", r"\\\1", text)


def post_telegram(post, ch, dry):
    token, chat = ch["bot_token"], ch["chat_id"]
    if dry:
        return {"ok": True, "dry": True, "id": None}
    title = tg_escape(post["title"])
    summary = tg_escape(post["summary"])
    link = utm(f"{SITE}/blog/{post['slug']}/", "telegram")
    # the URL must sit inside (...): the utm params contain _, which legacy
    # Markdown would otherwise read as an italic entity and fail the send
    caption = (f"*{title}*\n\n{summary}\n\n"
               f"[Read the post]({link})\n"
               f"Measured results on the ternary datapath — every post names "
               f"what is not proven.")[:1024]
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--update-profile", action="store_true",
                    help="refresh the Latest posts block in the GitHub profile README")
    args = ap.parse_args()

    posts = json.loads((REPO / "blog-posts.json").read_text())
    posts.sort(key=lambda p: p["date"])

    if args.update_profile:
        update_profile(posts, args.dry_run)
        return

    cfg = load_config()
    state = load_json(STATE_PATH, {})

    if args.status:
        for name in VALID_CHANNELS:
            ch = cfg.get("channels", {}).get(name, {})
            print(f"{name:10} {'enabled' if channel_enabled(name, ch) else 'no token (skipped)'}")
        for slug, done in state.items():
            print(f"{slug[:60]:60} -> {', '.join(f'{k}:{v}' for k, v in done.items()) or '-'}")
        return

    # only posts dated today or earlier; a future-dated post waits for its date
    todo = [p for p in posts
            if p["date"] <= time.strftime("%Y-%m-%d")
            and set(state.get(p["slug"], {})) != set(POSTERS)]
    if args.limit:
        todo = todo[-args.limit:]

    if not todo:
        print("nothing to syndicate")
        return

    for post in todo:
        slug = post["slug"]
        for name, poster in POSTERS.items():
            if name in state.get(slug, {}):
                continue
            ch = cfg.get("channels", {}).get(name, {})
            if not channel_enabled(name, ch):
                # not recorded in state: once a token is added, past posts retry
                print(f"[{slug}] {name}: skipped (no token)")
                continue
            try:
                res = poster(post, ch, args.dry_run)
                state.setdefault(slug, {})[name] = (
                    "dry-run" if res.get("dry") else str(res.get("id") or res.get("url") or "ok"))
                print(f"[{slug}] {name}: {'dry-run ok' if res.get('dry') else res}")
            except Exception as e:  # noqa: BLE001 — one channel failing must not stop others
                msg = re.sub(r"bot\d+:[\w-]+", "bot***", str(e))  # never leak tokens
                print(f"[{slug}] {name}: FAILED {msg}")
        print()

    if not args.dry_run:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
        print(f"state saved to {STATE_PATH}")


if __name__ == "__main__":
    main()
