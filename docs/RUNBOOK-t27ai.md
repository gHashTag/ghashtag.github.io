# t27.ai — Custom Domain Runbook

**Canonical custom domain:** `t27.ai`
**Source repo:** `gHashTag/ghashtag.github.io`
**Branch:** `main`
**Pages source:** `/ (root)`

## Defense layers

This domain is protected by **four independent layers**:

1. **CNAME guard workflow** — `.github/workflows/cname-guard.yml`
   Refuses any push/PR that removes the `CNAME` file or changes its content from `t27.ai`.

2. **Pages domain guard workflow** — `.github/workflows/pages-domain-guard.yml`
   Runs after every push and hourly via cron. Verifies the GitHub Pages API
   still has `t27.ai` bound and that `https://t27.ai/` returns HTTP 200.
   Fails loudly with remediation steps if the binding is lost.

3. **Uptime monitor** — Perplexity scheduled task (cron)
   Pings `https://t27.ai/` hourly. Sends a push notification on any non-200
   response so the operator hears about it within the hour.

4. **This runbook** — durable recovery instructions for any human or agent.

## Failure mode #1 — site returns 404

**Symptom:** `curl -sI https://t27.ai/` returns `HTTP/2 404` from `server: GitHub.com`.

**Root cause:** GitHub Pages "lost" the custom domain binding. This is a known
intermittent GitHub bug — the `CNAME` file in the repo is correct, but the
Pages API has `cname: null`. It usually happens when another repo in the same
account claims `t27.ai` (e.g. an old experimental branch with `t27.ai` in its
own `CNAME` triggers a Pages deploy that grabs the domain).

**Diagnosis (one command):**
```bash
gh api repos/gHashTag/ghashtag.github.io/pages | jq '{cname, status}'
```

If `cname` is `null` or anything other than `"t27.ai"`, the binding is gone.

**Find which repo stole the domain:**
```bash
gh api search/code -f q="t27.ai filename:CNAME user:gHashTag" \
  | jq -r '.items[] | "\(.repository.full_name) / \(.path)"'
```

For each repo returned, check whether it's actually bound in Pages:
```bash
gh api repos/gHashTag/<repo>/pages | jq '.cname'
```

The one that returns `"t27.ai"` is the thief.

**Fix:**
```bash
# 1. Release the domain from the conflicting repo (Pages keeps working
#    at https://gHashTag.github.io/<repo>/, only the custom domain is dropped):
gh api -X PUT repos/gHashTag/<conflicting-repo>/pages -f cname=''

# 2. Re-bind to ghashtag.github.io:
gh api -X PUT repos/gHashTag/ghashtag.github.io/pages -f cname=t27.ai

# 3. Verify:
sleep 5
gh api repos/gHashTag/ghashtag.github.io/pages | jq '{cname, status}'
# Expected: { "cname": "t27.ai", "status": "built" }

# 4. Wait ~60s for CDN, then test:
curl -sI https://t27.ai/ | head -3
# Expected: HTTP/2 200
```

## Failure mode #2 — CNAME file was deleted from the repo

**Symptom:** Pages deploy succeeds but custom domain is silently dropped on
the next push (because Pages re-reads CNAME on every deploy).

**Prevention:** the `cname-guard` workflow blocks the merge.

**Manual fix:**
```bash
echo 't27.ai' > CNAME
git add CNAME
git commit -m "fix: restore CNAME for t27.ai custom domain"
git push origin main
```

## Failure mode #3 — DNS broken

**Symptom:** `dig t27.ai` returns nothing or wrong A records.

**Required DNS records** (set at the domain registrar, NOT in GitHub):

```
Type    Name    Value
A       @       185.199.108.153
A       @       185.199.109.153
A       @       185.199.110.153
A       @       185.199.111.153
AAAA    @       2606:50c0:8000::153
AAAA    @       2606:50c0:8001::153
AAAA    @       2606:50c0:8002::153
AAAA    @       2606:50c0:8003::153
CNAME   www     gHashTag.github.io.
```

These point to GitHub's edge CDN. If they drift, Pages cannot route traffic.

**Verification:**
```bash
dig +short t27.ai A
# Should return all four 185.199.10[8-9].153 / 11[0-1].153 IPs.
```

## Forbidden actions

- ❌ **Never delete the `CNAME` file** (cname-guard will block).
- ❌ **Never change CNAME content from `t27.ai`** (cname-guard will block).
- ❌ **Never put `t27.ai` in another repo's CNAME under this account** — it will
  steal the domain on next Pages deploy. If you need `t27.ai` content elsewhere,
  use a subdomain (e.g. `lab.t27.ai`).
- ❌ **Never `git push --force` to main** — the workflow history is part of the defense.

## Last incident

- **2026-05-10** — `t27.ai` returned 404. Root cause: `gHashTag/trinity` repo
  had `t27.ai` in its CNAME and held the Pages domain binding (status:
  `errored`). Resolved by clearing trinity's binding and re-assigning to
  `gHashTag/ghashtag.github.io`. Defense layers added in commit after this
  incident.
