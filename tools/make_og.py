#!/usr/bin/env python3
"""Generate a post cover (1200x630 PNG) matching the 30 already published.

The covers live in this repository rather than in the app build, because the
app degrades gracefully when one is missing -- which means a post without a
cover ships silently and only looks wrong. Thirty posts had one and the
thirty-first did not, so this makes the step repeatable instead of manual.

    tools/make_og.py --slug <slug> --title "..." --minutes 8 \
        --receipts 5 --questions 3 [--ru] [--out DIR]

Renders SVG and rasterises with rsvg-convert. The typeface is whatever the
host resolves from the stack below; the published set was made on a machine
whose stack resolved to a bold grotesque, and a different host will differ
slightly. That is a cosmetic difference, stated rather than hidden.
"""
import argparse
import hashlib
import pathlib
import subprocess
import sys

W, H = 1200, 630
BG = "#05070a"
GREEN = "#00ff88"
DIM = "#7d928b"
RULE = "#1d2b2a"
FONTS = "Archivo, Inter, Helvetica Neue, Helvetica, Arial, sans-serif"


def stars(seed: str, n: int = 90):
    """A deterministic star field: the same slug always yields the same sky."""
    h = hashlib.sha256(seed.encode()).digest()
    out = []
    for i in range(n):
        a, b, c = h[(i * 3) % 32], h[(i * 3 + 1) % 32], h[(i * 3 + 2) % 32]
        x = (a * 7 + i * 53) % W
        y = (b * 5 + i * 31) % H
        r = 0.6 + (c % 5) * 0.22
        o = 0.10 + (c % 7) * 0.035
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.2f}" fill="#cfe8dd" opacity="{o:.2f}"/>')
    return "\n".join(out)


def wrap(title: str, per_line: int):
    """Greedy wrap. The published covers run to three lines at most."""
    words, lines, cur = title.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > per_line and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines[:3]


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def build(title, minutes, receipts, questions, slug, ru):
    eyebrow = "T27.AI · BLOG" if not ru else "T27.AI · БЛОГ"
    if ru:
        foot = f"{minutes} мин чтения · {receipts} квитанц. · {questions} откр. вопр."
    else:
        rl = "receipt" if receipts == 1 else "receipts"
        ql = "question" if questions == 1 else "questions"
        foot = f"{minutes} minute read · {receipts} linked {rl} · {questions} open {ql}"

    # Longer scripts need a smaller box; Cyrillic runs wider per character.
    per_line = 21 if ru else 26
    lines = wrap(title, per_line)
    size = 76 if len(lines) >= 3 else (86 if len(lines) == 2 else 96)
    top = 250 if len(lines) >= 3 else (300 if len(lines) == 2 else 350)

    tspans = "\n".join(
        f'<text x="80" y="{top + i * int(size * 1.16)}" font-family="{FONTS}" '
        f'font-size="{size}" font-weight="800" fill="#ffffff" '
        f'letter-spacing="-1.5">{esc(ln)}</text>'
        for i, ln in enumerate(lines)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{BG}"/>
{stars(slug + ("-ru" if ru else ""))}
<rect x="0" y="0" width="{W}" height="6" fill="{GREEN}"/>
<text x="1130" y="245" font-family="{FONTS}" font-size="86" font-weight="700"
      fill="{GREEN}" opacity="0.11" text-anchor="middle">&#8722;</text>
<text x="1130" y="345" font-family="{FONTS}" font-size="86" font-weight="700"
      fill="{GREEN}" opacity="0.11" text-anchor="middle">0</text>
<text x="1130" y="445" font-family="{FONTS}" font-size="86" font-weight="700"
      fill="{GREEN}" opacity="0.11" text-anchor="middle">+</text>
<rect x="80" y="106" width="14" height="14" fill="{GREEN}"/>
<text x="110" y="120" font-family="{FONTS}" font-size="22" font-weight="700"
      fill="{GREEN}" letter-spacing="6">{esc(eyebrow)}</text>
{tspans}
<rect x="80" y="522" width="1040" height="1" fill="{RULE}"/>
<text x="80" y="572" font-family="{FONTS}" font-size="21" fill="{DIM}">{esc(foot)}</text>
<text x="1120" y="572" font-family="{FONTS}" font-size="21" fill="{DIM}"
      text-anchor="end">Dmitrii Vasilev · t27.ai</text>
</svg>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--minutes", type=int, required=True)
    ap.add_argument("--receipts", type=int, required=True)
    ap.add_argument("--questions", type=int, required=True)
    ap.add_argument("--ru", action="store_true")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()

    svg = build(a.title, a.minutes, a.receipts, a.questions, a.slug, a.ru)
    out = pathlib.Path(a.out) / f"og-blog-{a.slug}{'-ru' if a.ru else ''}.png"
    tmp = pathlib.Path(f"/tmp/og-{a.slug}{'-ru' if a.ru else ''}.svg")
    tmp.write_text(svg)
    r = subprocess.run(
        ["rsvg-convert", "-w", str(W), "-h", str(H), str(tmp), "-o", str(out)]
    )
    if r.returncode != 0:
        print("rsvg-convert failed", file=sys.stderr)
        return 1
    print(f"{out}  ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
