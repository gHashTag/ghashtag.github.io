`npm run check:queen-viewport` against a clean build of origin/main (7e1c0d2be, fresh worktree) fails 30 of 36 size/view combinations. Not one failure is new — each is a gate assertion drifting away from the shell it guards, landing view change by view change without the contract being told. PR #1155 (the WARS tab) hit all of them on arrival and cannot honestly re-lay out tabs it did not touch, so that PR scopes the gate to the view it adds (plus the two shell-level repairs below, which fire on every view); this issue is the rest, for whoever owns the HUD's next word.

The rots, each with main's own numbers:

1. **`STATUS SLOT MISSING: alerts`** — every size, every view. The app moved the alert count into the Queen's own panel (the comment at the status row in `Queen.tsx` says so); `#stat-alerts` is not drawn any more. The contract still lists `alerts` as required and keeps `#stat-alerts` in `ZERO_SEL`. Answered in #1155 (the requirement is dropped, not the slot re-added).

2. **`COUNT commands=12 (the rail draws 9 of 17 views)`** — every size, every view. The rail stopped drawing one button per view twice over: families fold (the contract reads this part correctly), and the `tri` door opens into one button per screen (`TRI_BUTTONS` in `src/lib/triScreens.ts`). The contract counts `RAIL_VIEW_COUNT` (9); the rail draws 9 − 1 door + 4 screens = 12. Answered in #1155 (the expectation now reads `TRI_BUTTONS` from the same file the app does).

3. **`NOT EXACTLY ONE VIEW RENDERED 0` on comb** — every size. The comb renders as `.queen27-comb.is-embedded` nine DOM levels below `.queen27-hud-vp-body` (inside the catalog layer); the probe searches only direct children and one level of `:scope >`. A rendered board is reported as a board that did not render.

4. **`UNDECLARED SCROLLER .queen27-hud-vp-head / .queen27-hud-vp-tools`** — the head at 1019px in an 804px shell on comb at 1440x900; 862px in 644px on comb and 679px in 644px on every other view at 1280x700/600. The head's texts truncate; its buttons cannot. #1155 gives `.queen27-hud-vp-tools` the ladder's own answer (scroll sideways, hide the bar) and declares it, which heals the 679/862 rows; comb's 1019px head carries a world-selector row of its own and may need its own word.

5. **`UNDECLARED SCROLLER .queen-hive-display-content[…]`** — the comb's status hive, every size: its columns are cut by their own 21–35px boxes, with `small` labels a few pixels wider than the cells they sit in. Whatever the hive display is meant to do at 40px wide, it currently does it by overflowing.

6. **`UNDECLARED SCROLLER .queen27-board-stack[362x470 in 358x470]`** on map/factory at 390x844 — a 4px seam.

7. **`UNDECLARED SCROLLER small[…]`** at 1280x600 — status-tile labels a few pixels over their tiles (VERDICTS needed 55px in a 51px cell). #1155 gives the tile label the ellipsis its own value and sub-line have carried since P1-18.

Reproduce:

```
git worktree add /tmp/main-vp origin/main && cd /tmp/main-vp/apps/website
npm ci && npx vite build
CHROME_PATH=<any Chrome> npm run check:queen-viewport -- --no-build
```

Full matrix log from that origin/main build:

<details><summary>the 30 FAIL lines</summary>

```
    1920x1080 comb     FAIL  NOT EXACTLY ONE VIEW RENDERED 0 ; UNDECLARED SCROLLER .queen-hive-display-content[40x98 in 40x35] | .queen-hive-display-content[40x82 in 40x35] | .queen-hive-display-content[40x82 in 40x35] | .queen-hive-display-content[40x67 in 40x35] | .queen-hive-display-content[40x97 in 40x35] | .queen-hive-display-content[40x82 in 40x35] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views) ; COUNT views=0
    1920x1080 kanban   FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1920x1080 map      FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1920x1080 factory  FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1920x1080 research FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1920x1080 address  PASS  a hash set from outside moved the shell to kanban
    1440x900 comb     FAIL  NOT EXACTLY ONE VIEW RENDERED 0 ; UNDECLARED SCROLLER .queen27-hud-vp-head[1019x39 in 804x39] | .queen27-hud-vp-tools[574x26 in 359x26] | .queen-hive-display-content[33x128 in 33x28] | .queen-hive-display-content[33x82 in 33x28] | .queen-hive-display-content[33x97 in 33x28] | .queen-hive-display-content[33x97 in 33x28] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views) ; COUNT views=0
    1440x900 kanban   FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1440x900 map      FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1440x900 factory  FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1440x900 research FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1440x900 address  PASS  a hash set from outside moved the shell to kanban
    1272x806 comb     FAIL  NOT EXACTLY ONE VIEW RENDERED 0 ; UNDECLARED SCROLLER .queen27-hud-vp-head[862x39 in 712x39] | .queen27-hud-vp-tools[483x26 in 333x26] | .queen-hive-display-content[29x128 in 29x25] | .queen-hive-display-content[29x82 in 29x25] | .queen-hive-display-content[29x97 in 29x25] | .queen-hive-display-content[29x97 in 29x25] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views) ; COUNT views=0
    1272x806 kanban   FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1272x806 map      FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1272x806 factory  FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1272x806 research FAIL  STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1272x806 address  PASS  a hash set from outside moved the shell to kanban
    1280x700 comb     FAIL  NOT EXACTLY ONE VIEW RENDERED 0 ; UNDECLARED SCROLLER .queen27-hud-vp-head[862x39 in 644x39] | .queen27-hud-vp-tools[483x26 in 265x26] | .queen-hive-display-content[27x143 in 25x21] | small[27x29 in 25x29] | small[27x29 in 25x29] | .queen-hive-display-content[27x82 in 25x21] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views) ; COUNT views=0
    1280x700 kanban   FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x700 map      FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x700 factory  FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x700 research FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x700 address  PASS  a hash set from outside moved the shell to kanban
    1280x600 comb     FAIL  NOT EXACTLY ONE VIEW RENDERED 0 ; UNDECLARED SCROLLER .queen27-hud-vp-head[862x39 in 644x39] | .queen27-hud-vp-tools[483x26 in 265x26] | .queen-hive-display-content[27x143 in 20x17] | small[27x29 in 20x29] | small[27x29 in 20x29] | .queen-hive-display-content[27x82 in 20x17] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views) ; COUNT views=0
    1280x600 kanban   FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x600 map      FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x600 factory  FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x600 research FAIL  UNDECLARED SCROLLER .queen27-hud-vp-head[679x39 in 644x39] | .queen27-hud-vp-tools[300x26 in 265x26] ; STATUS SLOT MISSING: alerts ; COUNT commands=12 (the rail draws 9 of 17 views)
    1280x600 address  PASS  a hash set from outside moved the shell to kanban
    390x844 comb     FAIL  NOT EXACTLY ONE VIEW RENDERED 0 ; UNDECLARED SCROLLER .queen-hive-display-content[23x183 in 10x8] | small[23x25 in 10x25] | small[23x25 in 10x25] | .queen-hive-display-content[23x83 in 10x8] | small[23x25 in 10x25] | small[23x25 in 10x25] ; COUNT commands=12 (the rail draws 9 of 17 views) ; COUNT views=0
    390x844 kanban   FAIL  COUNT commands=12 (the rail draws 9 of 17 views)
    390x844 map      FAIL  UNDECLARED SCROLLER .queen27-board-stack[362x470 in 358x470] ; COUNT commands=12 (the rail draws 9 of 17 views)
    390x844 factory  FAIL  UNDECLARED SCROLLER .queen27-board-stack[362x470 in 358x470] ; COUNT commands=12 (the rail draws 9 of 17 views)
    390x844 research FAIL  COUNT commands=12 (the rail draws 9 of 17 views)
    390x844 address  PASS  a hash set from outside moved the shell to kanban
  
    Queen viewport contract: FAIL (30 size/view combination(s))
```
</details>
