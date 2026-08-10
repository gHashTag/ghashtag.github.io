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


def square_wrapper(svg_text: str) -> str:
    """Nest the 1200x630 card inside a 1200x1200 artboard.

    qlmanage fits a render to the taller axis and then crops the wider one, so
    handing it the card directly produced a 1.563x magnification with everything
    past x~768 simply gone. That is not a subtle failure: it silently removed the
    third statistic from every card -- "147 MHz pipelined on Artix-7",
    "SKY130 taped out", "2 arXiv papers" -- and the result still looked like a
    finished card, which is why it shipped.

    A square source has nothing to crop, so the whole width survives and the card
    lands at a known offset instead of a detected one.
    """
    inner = svg_text.replace("<svg ", '<svg x="0" y="285" ', 1)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" '
        'viewBox="0 0 1200 1200">'
        '<rect width="1200" height="1200" fill="#05070a"/>'
        f"{inner}</svg>"
    )


def main():
    TMP.mkdir(exist_ok=True)
    svgs = sorted(REPO.glob("og-*.svg"))
    if not svgs:
        sys.exit("no og-*.svg found")
    bad = 0
    for svg in svgs:
        for stale in TMP.glob("*.png"):
            stale.unlink()
        square = TMP / f"{svg.stem}.square.svg"
        square.write_text(square_wrapper(svg.read_text(encoding="utf-8")), encoding="utf-8")
        subprocess.run(["qlmanage", "-t", "-s", "1200", "-o", str(TMP), str(square)],
                       capture_output=True)
        raw = TMP / f"{square.name}.png"
        if not raw.exists():
            print(f"  {svg.name}: RASTERISE FAILED")
            bad += 1
            continue
        im = Image.open(raw).convert("RGB")
        if im.size != (1200, 1200):
            print(f"  {svg.name}: expected a 1200x1200 render, got {im.size}")
            bad += 1
            continue
        # The card sits at a known offset in a square artboard, so this is a
        # fixed crop rather than a guess about where the artwork begins.
        card = im.crop((0, 285, 1200, 915))
        if card.size != (W, H):
            card = card.resize((W, H), Image.LANCZOS)
        out = REPO / f"{svg.stem}.png"
        card.save(out, "PNG", optimize=True)
        print(f"  {svg.name:<22} -> {out.name} ({out.stat().st_size // 1024} kB)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
