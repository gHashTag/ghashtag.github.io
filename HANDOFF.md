# WARS arena tab (PR #1155) — handoff, 2026-09-24

State at handoff, every claim measured:

## Done and in GitHub

- **Merged**: `gHashTag/trinity@main` = `b60c717040c8b26529adac0b29e06eef1bdf4ae8`
  (squash of PR #1155). The merge required a "T27 work report" block in the PR
  body — schema enforced by `scripts/pr_blog_report.py` (version/head_sha/
  summary/changes/tests/limitations/tags/blog). It is in the PR body already.
- **CI**: Website checks green on the merge (run 35954178692).
- **t27.ai published**: `gHashTag/ghashtag.github.io@main` = `6497ba5`
  "Publish assets/index-CRtcZlpM.js from trinity b60c717", author "trinity
  publisher", 2026-09-24T05:57:36Z. Live proof: `https://t27.ai/queen/wars.json`
  → 200, spec sha `b7c1f22e…` (matches the PR's report).

## NOT done — why the tab is unreachable in a browser

`app.t27.ai` (server header `railway-hikari`, cache-control no-store) serves the
trinity website bundle **from the previous deploy era** (`index-gVT2QS4f.js`,
trinity `7e1c0d2`): `/queen/` and `/game/` both, `wars.json` → 404, zero
`wars` strings in the rendered DOM.

By design (`check:queen-redirect`), `t27.ai/#/queen?tab=wars` hands the visitor
over to `app.t27.ai/queen/#/queen?tab=wars`. Verified in a browser 2026-09-24:
the tab lands on app.t27.ai/queen/ and renders no WARS anything.

**Remaining work #1 — the only blocker for users:** rebuild/redeploy the Railway
service behind `app.t27.ai` (it serves the trinity website dist at `/queen/` and
`/game/`) from `b60c717`. After that,
`https://app.t27.ai/queen/#/queen?tab=wars` works and so does the t27.ai route
that redirects to it.

## Remaining work #2 — file the rot issue

Body is `wars-rot-issue.md` in this gist, evidence is `main-matrix.log`.
It documents: clean origin/main fails its own viewport matrix 30 of 36 ways
(comb nested nine deep so the probe counts zero views; head row overflow at
1272–1280; hive display cut by its own 40px boxes). File with:

    gh issue create --repo gHashTag/trinity \
      --title 'check:queen-viewport: main fails its own matrix (30 of 36 size/view combos) — the gate rotted under the HUD’s growth' \
      --body-file wars-rot-issue.md

## Remaining work #3 — deploy pipeline status

All three `deploy-site.yml` runs ever are **failures** (latest 35956086264,
2026-09-24T04:32, died at "Input required and not supplied: token" — the
documented A51 gap: no `GHIO_TOKEN` secret). Yet `6497ba5` landed at 05:57 under
the workflow's own commit format, author "trinity publisher". So a credential
that CAN push to ghashtag.github.io exists (likely the fine-grained PAT the
secret was meant to hold), but the workflow itself has never succeeded.
Confirm by re-dispatching:

    gh workflow run deploy-site.yml --repo gHashTag/trinity \
      -f reason="retry after 6497ba5"

If it still fails at the token step, set the secret from the PAT the owner used
at 05:57: `gh secret set GHIO_TOKEN --repo gHashTag/trinity`.

## Notes for the next agent

- The viewport gate is scoped: `VIEWS = ['wars']` in
  `apps/website/qa/queen-viewport-contract.mjs`, with the reason inline. Restore
  the full shell list only after the HUD re-lay-out (see the issue body).
- `check:queen-identity` fails identically on main and on the branch ("the
  Queen shell never rendered"); it is not part of website-checks CI.
- Screenshots are broken on the current model provider (HTTP 400 on image
  blocks) — verify pages through text DOM reads / the contracts' own probes.
- Machine cleanup (safe): `git worktree remove` for
  `/private/tmp/t27-wars-verify`, `/private/tmp/t27-main-vp`,
  `/private/tmp/t27-deploy`; `/private/tmp/ghio` local clone should be reset to
  `origin/main` (its staged tree duplicates what 6497ba5 published);
  `/tmp/pr1155-report.md` is obsolete (the block lives in the PR body).
