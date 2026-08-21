---
name: t27-deck
description: Build a Trinity / t27.ai-styled slide deck as a reproducible PDF — pitch decks, investor decks, accelerator applications, one-pagers. Enforces the t27.ai design system (black, mint #00FF88, φ-scaled type and spacing) and the origin-label discipline (measured / proved / derived / retracted). Use whenever a Trinity deck or presentation is created, translated, or restyled.
---

# t27-deck — decks in the Trinity house style

A deck here is **generated code, never a hand-placed file**. The generator is the
artefact that gets reviewed and committed; the PDF is its output. That is what makes a
deck reproducible, diffable, and correctable after it has already been sent.

Reference implementations, both reproducible from source:

| | |
|---|---|
| `business/hub71/build_deck.py` | English, Hub71 application |
| `business/hub71/build_deck_ru.py` | Russian, same content, t27.ai design system |

---

## 1. Never invent the styling. Pull it from the live site.

The design system is published. Take it, do not approximate it:

```bash
curl -s https://t27.ai/ -o /tmp/t27.html
curl -s "https://t27.ai/$(grep -oE 'assets/index-[A-Za-z0-9_-]+\.css' /tmp/t27.html | head -1)" -o /tmp/t27.css
grep -oE '\-\-[a-z0-9-]+:\s*[^;]+' /tmp/t27.css | sort -u
```

As of 2026-08-21 that yields:

```
--bg #000000   --text #FFFFFF   --muted #888888
--accent #00FF88   --accent-dark #00CC66   --golden #FFD700
--border rgba(255,255,255,.08)      --font "Outfit", system-ui
--phi 1.618
```

**The scales are φ-based and that is the point of the identity — honour them.**

- type: `.75 .8125 .875 1 1.272 1.618 2.058 2.618 4.236 6.854` rem
- spacing: `.382 .618 1 1.618 2.618 4.236 6.854` rem

Set `1rem ≈ 15pt` on a 13.333×7.5in (16:9) page and the whole deck inherits the site's
proportions without a single hand-tuned number.

## 2. Origin labels are not decoration

Every figure on a slide carries the label the site gives it. The palette and the Russian
wording both live in the site bundle (`index-*.js`) — extract, do not translate:

| en | ru | colour |
|---|---|---|
| measured | измерено | `#00FF88` |
| proved | доказано | `#7CC7FF` |
| machine-checked in Coq | машинно проверено в Coq | `#C08CFF` |
| specification | спецификация | `#FFD700` |
| derived | выведено | `#FFA45C` |
| third-party figure | внешний источник | `#7FB3FF` |
| plan, not a result | план, не результат | `#B0B8C4` |
| retracted | отозвано | `#FF6B6B` |

Rendering: outlined pill, `1px solid currentColor`, radius 3, uppercase,
letter-spacing `.09em`, weight 600. Section kickers use letter-spacing `.18em` in muted.

A figure the founder computed himself (a quotient of two published numbers) is
**derived**, never third-party. Getting that wrong was a real audit finding.

## 3. Every deck carries a "what this does not claim" panel

Not a disclaimer — a feature. It is the thing the product is sold on. It states, at
minimum: no silicon, what the frequencies actually are, what was not measured, and any
figure withdrawn since. Withdrawn numbers are **named**, not quietly dropped, so a
reviewer who saw the old figure can see it retired.

## 4. Cyrillic: Outfit will not do it

Outfit ships latin / latin-ext only. Checked by cmap, **Manrope** is the closest
geometric grotesque carrying Cyrillic, φ (U+03C6) and × together, in 400/600/800.
Vendor it next to the generator (`fonts/`) so the deck builds anywhere:

```bash
python3 -c "
from fontTools.ttLib import TTFont
f=TTFont('fonts/Manrope_0.ttf'); cm=set(f.getBestCmap())
print('А',0x410 in cm,'я',0x44F in cm,'φ',0x3C6 in cm,'×',0xD7 in cm)"
```

For Russian copy, lift the wording from the site's own RU version (it has a
lang-switcher) rather than translating afresh — «гейт», «стенд», «датапуть»,
«ступени лестницы», «открытый поток» are the author's terms.

## 5. Layout rules that were learned the hard way

- **Size boxes from their content.** Fixed card heights collide with text the moment a
  translation runs longer. `card()` and `panel()` in `build_deck_ru.py` compute their own
  height and return it; stack rows from the returned value, never from a guessed offset.
- **Auto-shrink titles.** Loop the font size down until `stringWidth` fits the column.
  Russian headlines run ~15% longer than English and will run off the page otherwise.
- **Wrap, never clip.** Any helper taking a string must wrap it; a helper that
  `drawString`s a raw line will silently run past the margin.
- **Cap card labels at 2–3 lines** and shorten the copy instead of shrinking the type.

## 6. Verify before you send

Render and *look* — a PDF that compiles can still be unreadable:

```bash
python3 build_deck_ru.py
pdftoppm -png -r 70 Trinity_Hub71_deck_RU.pdf pg   # then read every page
```

Then grep the extracted text for anything withdrawn. This check is not optional; it is
the one that would have caught the numbers that shipped in the Hub71 application:

```bash
for n in "974.66" "827.81" "0.1797" "6.1×" "2.1×" "Ratified" "machine-checked theorems"; do
  printf "%-28s %s\n" "$n" "$(pdftotext deck.pdf - | grep -c "$n")"
done
```

Expect zero, except where the number appears **inside** the retraction notice.

## 7. The rule that outranks the styling

**The site is not the source of truth for numbers.** t27.ai's result set is stamped with
a date; the repository is often newer. Before a figure goes into a deck, find the record
that generated it and compare dates. See `claim_source_staleness` in memory and the
`number-audit` skill. A beautiful deck carrying a retracted number is a worse artefact
than an ugly one carrying none.
