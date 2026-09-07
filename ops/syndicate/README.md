# Blog syndication pipeline (t27.ai → external channels)

Publishes every new post from `blog-posts.json` to Telegram / dev.to /
Hashnode / Medium, once per post per channel. State: `~/.config/t27-syndicate/state.json`.

## Setup

    mkdir -p ~/.config/t27-syndicate
    cp config.example.json ~/.config/t27-syndicate/config.json
    # fill in the tokens for the channels you want; empty channels are skipped

### Token runbook (dev.to / Hashnode / Medium)

An agent with a working in-app browser session can create these keys itself:

- **dev.to** — https://dev.to/settings/extensions → "DEV Community API Keys" →
  describe as `t27 syndication` → Generate → copy into `channels.devto.api_key`.
- **Hashnode** — https://hashnode.com/settings/developer → "Personal Access
  Tokens" → Generate (needs a blog; create one at hashnode.com/blog/new first
  if the account has none) → copy into `channels.hashnode.token`.
- **Medium** — https://medium.com/me/settings/security → "Integration
  tokens" → create (integration tokens can only create **drafts**) → copy into
  `channels.medium.token`.

If the account is not signed in inside the browser, this needs the user.

Run:

    .venv/bin/python syndicate.py --dry-run   # preview
    .venv/bin/python syndicate.py             # post
    .venv/bin/python syndicate.py --status    # what went where
    .venv/bin/python syndicate.py --slug phi-is-a-scale-not-information --channel telegram --dry-run
    .venv/bin/python syndicate.py --slug phi-is-a-scale-not-information --channel telegram
    .venv/bin/python syndicate.py --update-profile  # refresh Latest posts
                                                 # in gHashTag/gHashTag README

The repo checkout must be current (`git pull`) before running — posts are read
from `blog/` on disk. dev.to / Hashnode / Medium receive **drafts** by default
(platform policy + review); Telegram posts immediately.

`--slug` requires an exact match in `blog-posts.json` dated today or earlier.
`--channel` selects just one channel and fails if that channel is not configured.
Omitting both keeps the existing backlog workflow. Use both selectors for a
scheduled slot: `--limit 1` alone can choose a newer article instead.

Live runs hold `state.json.lock` before reading state and atomically save each
successful post/channel result before dispatching the next one. The lock file
stays on disk; the OS releases its lock when the process exits. `--dry-run` and
`--status` never create state or lock files. The existing slug → channel → string
receipt format is unchanged. Channel failures return exit code 1; invalid CLI
selectors return 2. A state-write failure stops further dispatch.

An API timeout, or a crash after remote publication but before the receipt is
saved, can still leave an uncertain result. Check the remote channel before
retrying; the lock and local receipt file cannot guarantee exactly-once delivery
across a remote API.

Isolated checks (all adapters mocked; no real config, state or network):

    .venv/bin/python -m unittest discover -s . -p 'test_syndicate.py' -v

## Design decisions

- **Canonical URL + UTM.** Every cross-post opens with "Originally published at
  <t27.ai link?utm_source=…>" and sets `canonical_url` in the APIs where
  supported, so t27.ai keeps the SEO weight and analytics attribute traffic per
  channel.
- **One visual style.** Each post already ships original generated article art
  (`og-art/<slug>.jpg`, 1200×630). The same file is reused as the channel cover
  image everywhere — Telegram photo, dev.to `main_image`, Hashnode
  `coverImage`. No new art.
- **Confirmed receipts.** State records post × channel, and re-running skips
  those pairs. A channel failing does not stop the others; failed channels are
  not recorded. Reconcile uncertain remote results before retrying them.
- **Safety.** All outbound requests are https-only to an allow-listed API host
  with resolved-IP checks (no localhost/private/metadata endpoints — SSRF
  guard); the hashnode `endpoint` override is host-checked at load too.
