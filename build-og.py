#!/usr/bin/env python3
"""Собрать все OG-карточки сайта единым воспроизводимым способом.

SVG остаются читаемыми исходниками карточек, а PNG — их обязательным
растровым представлением для социальных сетей.  Раньше PNG, сделанные вручную
на macOS через qlmanage, и PNG для новых постов, нарисованные Pillow на Linux,
использовали разные шрифты.  Этот скрипт нормализует SVG на Inter и рендерит
все карточки через librsvg с локальным fontconfig, поэтому результат не
зависит от шрифтов образа CI.

    python3 build-og.py
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

W, H = 1200, 630
REPO = Path(__file__).resolve().parent
FONT = REPO / "fonts" / "Inter-Variable.ttf"


def ensure_blog_index_source() -> Path:
    """Создать исходник карточки индекса блога, у которого раньше был только PNG."""
    path = REPO / "og-image.svg"
    path.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="T27.AI blog">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#05070a"/><stop offset="100%" stop-color="#0b1418"/>
    </linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00ff88" stop-opacity="0.9"/><stop offset="100%" stop-color="#00ff88" stop-opacity="0.1"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect x="0" y="0" width="{W}" height="5" fill="url(#glow)"/>
  <text x="80" y="132" font-family="Inter,Helvetica,Arial,sans-serif" font-size="22" letter-spacing="6" fill="#00ff88" opacity="0.85">T27.AI · BLOG</text>
  <text x="80" y="248" font-family="Inter,Helvetica,Arial,sans-serif" font-size="62" font-weight="700" fill="#f2f6f4">Published here.</text>
  <text x="80" y="306" font-family="Inter,Helvetica,Arial,sans-serif" font-size="28" fill="#9fb3ab">Measured results, receipts and open questions.</text>
  <line x1="80" y1="372" x2="1120" y2="372" stroke="#1d2b2a" stroke-width="2"/>
  <text x="80" y="452" font-family="Inter,Helvetica,Arial,sans-serif" font-size="46" font-weight="700" fill="#00ff88">Static HTML</text>
  <text x="80" y="490" font-family="Inter,Helvetica,Arial,sans-serif" font-size="21" fill="#8fa79f">readable without JavaScript</text>
  <text x="80" y="566" font-family="Inter,Helvetica,Arial,sans-serif" font-size="22" fill="#7d928b">Dmitrii Vasilev · admin@t27.ai</text>
</svg>
""",
        encoding="utf-8",
    )
    return path


def normalise_svg(path: Path) -> None:
    """Явно закрепить Inter у старых карточек вместо системных семейств."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'font-family="[^"]+"', 'font-family="Inter,Helvetica,Arial,sans-serif"', text)
    path.write_text(text, encoding="utf-8")


def fontconfig_file(tmp: Path) -> Path:
    config = tmp / "fonts.conf"
    config.write_text(
        """<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>""" + str(REPO / "fonts") + """</dir>
  <cachedir>""" + str(tmp / "fontcache") + """</cachedir>
  <alias>
    <family>Inter</family>
    <default><family>Inter</family></default>
  </alias>
</fontconfig>
""",
        encoding="utf-8",
    )
    return config


def render(svg: Path, png: Path, env: dict[str, str]) -> None:
    result = subprocess.run(
        ["rsvg-convert", "--width", str(W), "--height", str(H), "--output", str(png), str(svg)],
        text=True,
        capture_output=True,
        env=env,
    )
    if result.returncode:
        raise RuntimeError(f"{svg.name}: librsvg завершился с {result.returncode}: {result.stderr.strip()}")
    with Image.open(png) as image:
        if image.size != (W, H):
            raise RuntimeError(f"{svg.name}: получен размер {image.size}, ожидался {(W, H)}")


def main() -> int:
    if not FONT.is_file():
        raise SystemExit(f"Нет {FONT.relative_to(REPO)}: добавить Inter вместе с лицензией нельзя пропускать")
    if not shutil.which("rsvg-convert"):
        raise SystemExit("Нет rsvg-convert: установить librsvg2-bin, затем повторить сборку карточек")

    ensure_blog_index_source()
    svgs = sorted(REPO.glob("og-*.svg"))
    if not svgs:
        raise SystemExit("Не найдены исходники og-*.svg")

    with tempfile.TemporaryDirectory(prefix="t27-og-") as tmp_name:
        tmp = Path(tmp_name)
        env = os.environ.copy()
        env["FONTCONFIG_FILE"] = str(fontconfig_file(tmp))
        env["FONTCONFIG_PATH"] = str(tmp)
        for svg in svgs:
            normalise_svg(svg)
            png = svg.with_suffix(".png")
            render(svg, png, env)
            print(f"  {svg.name:<56} -> {png.name}")

    expected = {svg.stem for svg in svgs}
    actual = {png.stem for png in REPO.glob("og-*.png")}
    if expected != actual:
        raise SystemExit(f"Наборы SVG и PNG расходятся: только SVG={sorted(expected-actual)}, только PNG={sorted(actual-expected)}")
    print(f"Готово: {len(svgs)} карточек Inter размером {W}×{H}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
