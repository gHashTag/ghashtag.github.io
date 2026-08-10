#!/usr/bin/env python3
"""Rasterise the og-*.svg cards to 1200x630 PNG, because no social platform
renders SVG previews -- every share link currently comes through with no card.

qlmanage is the rasteriser (headless Chrome hangs on the second invocation in a
session, reproducibly). It renders into a square canvas, top-aligned and
vertically stretched, on a white ground. A centred crop is therefore WRONG: the
first attempt silently ate the T27.AI eyebrow and the accent bar off the top of
every card, and it only showed up on looking at the result.

So: find the card by its own pixels, crop to exactly that, and resize the box to
1200x630. That is correct whatever scale qlmanage chose, because the source
viewBox is 1200x630 and the whole box maps back onto it.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

W, H = 1200, 630
REPO = Path(__file__).resolve().parent
TMP = Path("/tmp/ogbuild2")


def card_box(im: Image.Image):
    """Bounding box of everything that is not the white padding."""
    rgb = im.convert("RGB")
    px = rgb.load()
    w, h = rgb.size
    def row_is_pad(y):
        return all(px[x, y] > (245, 245, 245) for x in range(0, w, 7))
    def col_is_pad(x):
        return all(px[x, y] > (245, 245, 245) for y in range(0, h, 7))
    top = next((y for y in range(h) if not row_is_pad(y)), None)
    if top is None:
        return None
    bottom = next(y for y in range(h - 1, -1, -1) if not row_is_pad(y))
    left = next(x for x in range(w) if not col_is_pad(x))
    right = next(x for x in range(w - 1, -1, -1) if not col_is_pad(x))
    return left, top, right + 1, bottom + 1


def main():
    TMP.mkdir(exist_ok=True)
    svgs = sorted(REPO.glob("og-*.svg"))
    if not svgs:
        sys.exit("no og-*.svg found")
    bad = 0
    for svg in svgs:
        for stale in TMP.glob("*.png"):
            stale.unlink()
        subprocess.run(["qlmanage", "-t", "-s", "1200", "-o", str(TMP), str(svg)],
                       capture_output=True)
        raw = TMP / f"{svg.name}.png"
        if not raw.exists():
            print(f"  {svg.name}: RASTERISE FAILED")
            bad += 1
            continue
        im = Image.open(raw)
        box = card_box(im)
        if box is None:
            print(f"  {svg.name}: no card found in render")
            bad += 1
            continue
        card = im.convert("RGB").crop(box).resize((W, H), Image.LANCZOS)
        out = REPO / f"{svg.stem}.png"
        card.save(out, "PNG", optimize=True)
        bw, bh = box[2] - box[0], box[3] - box[1]
        print(f"  {svg.name:<22} box {bw}x{bh} -> {out.name} "
              f"({out.stat().st_size // 1024} kB)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
