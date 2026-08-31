#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор колоды TRINITY S³AI / TRI PHONE — ru+en, в палитре t27.ai.

Появился 31.08.2026: прежние PDF лежали без генератора, обновить их можно
было только переписав. Теперь: python3 deck/build-deck.py — и оба PDF
пересобираются из одной структуры данных. Палитра — сайта (index.css):
фон #05070a, текст #e8efec, акцент #00FF88, золото #FFD700.
"""
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

HERE = os.path.dirname(os.path.realpath(__file__))
FONT = os.path.join(HERE, '..', 'fonts', 'Inter-Variable.ttf')
pdfmetrics.registerFont(TTFont('Inter', FONT))
pdfmetrics.registerFont(TTFont('DIN', '/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf'))
from reportlab.lib.colors import Color
GHOST = Color(1, 0.84, 0, 0.07)   # призрачное золото для фолио

W, H = 960, 540
BG, TEXT = HexColor('#05070a'), HexColor('#e8efec')
MUTED, ACCENT, GOLD = HexColor('#8fa39b'), HexColor('#00FF88'), HexColor('#FFD700')
BORDER = HexColor('#22302a')

def wrap(c, text, size, maxw, font='Inter'):
    out, line = [], ''
    for w in text.split():
        t = (line + ' ' + w).strip()
        if c.stringWidth(t, font, size) <= maxw: line = t
        else: out.append(line); line = w
    if line: out.append(line)
    return out

class Deck:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(W, H))
        self.page = 0
    def bg(self):
        self.c.setFillColor(BG); self.c.rect(0, 0, W, H, stroke=0, fill=1)
    def footer(self, lang):
        self.page += 1
        self.c.setFillColor(MUTED); self.c.setFont('Inter', 8)
        self.c.drawString(40, 20, 'TRINITY S³AI · t27.ai · admin@t27.ai')
        self.c.drawRightString(W-40, 20, str(self.page))
    def text(self, x, y, s, size, color=TEXT, maxw=None, leading=None, font='Inter'):
        self.c.setFillColor(color); self.c.setFont(font, size)
        if maxw is None:
            self.c.drawString(x, y, s); return y - (leading or size*1.4)
        for ln in wrap(self.c, s, size, maxw, font):
            self.c.drawString(x, y, ln); y -= (leading or size*1.38)
        return y
    def folio(self, n):
        # призрачный номер-фолио, как в глянце: огромная цифра у правого края
        self.c.setFillColor(GHOST); self.c.setFont('DIN', 340)
        self.c.drawRightString(W-24, 70, f'{n:02d}')
    def rule(self, y, color=GOLD, w=1.2, x0=40, x1=None):
        self.c.setStrokeColor(color); self.c.setLineWidth(w)
        self.c.line(x0, y, x1 or W-40, y)
    def kicker(self, s):
        self.c.setFillColor(ACCENT); self.c.setFont('Inter', 10.5)
        self.c.drawString(40, H-46, s.upper())
        self.rule(H-54, ACCENT, 0.8, 40, 40 + self.c.stringWidth(s.upper(), 'Inter', 10.5))
    def h(self, s, y=None):
        yy = self.text(40, y or H-112, s.upper(), 52, TEXT, maxw=W-90, leading=54, font='DIN')
        self.rule(yy + 38, GOLD, 1.4)
        return yy + 20

def slide(d, lang, kicker, title, blocks):
    d.bg(); d.folio(d.page + 1); d.kicker(kicker); y = d.h(title) - 8
    for b in blocks:
        kind = b[0]
        if kind == 'lede':
            y = d.text(40, y, b[1], 11.5, MUTED, maxw=W-80) - 6
        elif kind == 'point':   # (point, головка, тело)
            y = d.text(40, y, b[1].upper(), 19, ACCENT, maxw=W-120, leading=21, font='DIN') - 1
            y = d.text(40, y, b[2], 10.5, TEXT, maxw=W-150, leading=15) - 12
        elif kind == 'gold':
            y = d.text(40, y, b[1].upper(), 19, GOLD, maxw=W-120, leading=21, font='DIN') - 1
            y = d.text(40, y, b[2], 10.5, TEXT, maxw=W-150, leading=15) - 12
        elif kind == 'table':   # (table, [головки], [строки], [ширины])
            heads, rows, widths = b[1], b[2], b[3]
            x = 40
            for hcell, wd in zip(heads, widths):
                d.text(x, y, hcell, 9.5, MUTED); x += wd
            y -= 16
            d.c.setStrokeColor(BORDER); d.c.line(40, y+6, W-40, y+6)
            for row in rows:
                x = 40; ymin = y
                for cell, wd in zip(row, widths):
                    yy = d.text(x, y, cell, 9.5, TEXT, maxw=wd-14, leading=12)
                    ymin = min(ymin, yy); x += wd
                y = ymin - 6
                d.c.setStrokeColor(BORDER); d.c.line(40, y+8, W-40, y+8)
        elif kind == 'gap':
            y -= b[1]
    d.footer(lang); d.c.showPage()

def metrics_slide(d, lang, kicker, title, lede, cells, boundary_head, boundary):
    d.bg(); d.folio(d.page + 1); d.kicker(kicker); y = d.h(title) - 6
    y = d.text(40, y, lede, 10.5, MUTED, maxw=W-160) - 14
    colw, x0, top = (W-80)/4, 40, y
    rowh = 112
    for i, (value, tag, note) in enumerate(cells):
        cx = x0 + (i % 4) * colw; cy = top - (i // 4) * rowh
        vsize = 34
        while vsize > 14 and d.c.stringWidth(value, 'DIN', vsize) > colw - 22:
            vsize -= 1
        d.text(cx, cy, value, vsize, TEXT, font='DIN')
        d.text(cx, cy-15, tag, 7.5, ACCENT if 'ИЗМЕР' in tag or 'MEASURED' in tag else GOLD)
        d.text(cx, cy-29, note, 8.6, MUTED, maxw=colw-18, leading=10.5)
    y = top - ((len(cells)+3)//4) * rowh - 2
    d.rule(y+18, GOLD, 1.0)
    y = d.text(40, y, boundary_head.upper(), 15, GOLD, maxw=W-80, font='DIN') - 2
    d.text(40, y, boundary, 9, MUTED, maxw=W-160, leading=11.5)
    d.footer(lang); d.c.showPage()

def title_slide(d, lang, t):
    d.bg()
    d.c.setFillColor(GHOST); d.c.setFont('DIN', 420)
    d.c.drawRightString(W-10, 40, 'Φ')
    d.text(40, H-56, 'TRINITY S³AI', 12, MUTED)
    d.rule(H-66, ACCENT, 0.8, 40, 150)
    d.text(40, H-190, 'TRI PHONE', 128, TEXT, font='DIN')
    sub_head = 'ПРОВЕРЯЕМЫЙ КАРМАННЫЙ КОМПЬЮТЕР' if lang=='ru' else 'A POCKET COMPUTER YOU CAN AUDIT'
    d.text(40, H-232, sub_head, 30, GOLD, maxw=W-90, font='DIN')
    d.rule(H-252, GOLD, 1.4)
    y = d.text(40, H-286, t['sub'], 11.5, TEXT, maxw=W-320, leading=15.5) - 4
    y = d.text(40, y, t['line'], 10.5, ACCENT, maxw=W-320, leading=14)
    d.text(W-40-d.c.stringWidth('φ² + 1/φ² = 3','Inter',22), H-300, 'φ² + 1/φ² = 3', 22, GOLD)
    d.text(40, 58, t['author'], 9, MUTED, maxw=W-80)
    d.footer(lang); d.c.showPage()

def build(lang, path):
    d = Deck(path); L = lambda ru, en: ru if lang == 'ru' else en
    title_slide(d, lang, {
        'title': L('TRI PHONE: проверяемый карманный компьютер','TRI PHONE: a pocket computer you can audit'),
        'sub': L('Флагман-курс: тернарный FPGA-карманник — и одноплатный компьютер — под TRIOS с агентом TRI CLAW. Каждый слой проверяем: от битстрима до слова агента. Связь — mesh, не сотовая.',
                 'Flagship course: a ternary FPGA pocket computer — and an SBC — running TRIOS with the TRI CLAW agent. Every layer auditable: from bitstream to the agent’s word. Mesh connectivity, not cellular.'),
        'line': L('Ступень v0 строится сейчас: TRI CLAW, гейтвер-концепт. Ток/с на целевом кристалле НЕ измерены — это сказано здесь, а не найдено в due diligence.',
                  'Rung v0 is in progress: TRI CLAW, a gateware concept. Tokens/s on the target part are NOT measured — said here, not discovered in due diligence.'),
        'author': L('Дмитрий Васильев — основатель, инженер FPGA/RTL и hardware-AI · ORCID 0009-0008-4294-6159 · t27.ai · admin@t27.ai · github.com/gHashTag · август 2026',
                    'Dmitrii Vasilev — founder, FPGA/RTL and hardware-AI engineer · ORCID 0009-0008-4294-6159 · t27.ai · admin@t27.ai · github.com/gHashTag · August 2026'),
    })
    slide(d, lang, L('Проблема','Problem'), L('Низкая точность уехала в кремний. Доверие — нет.','Low precision moved into silicon. Trust did not.'), [
        ('point', L('Точность стала переменной проектирования железа.','Precision became a hardware design variable.'),
                  L('Четыре бита стали мейнстримом за одно поколение; стандарт соответствия (IEEE P3109) не ратифицирован. Купить нельзя ровно одно: доказательство, что декодер совпадает со спецификацией бит в бит.',
                    'Four bits went mainstream in one hardware generation; the conformance standard (IEEE P3109) is not ratified. Exactly one thing cannot be bought: proof that a decoder matches its spec bit for bit.')),
        ('point', L('И одновременно: агент уехал на стол пользователя.','And at the same time: the agent moved onto the user’s desk.'),
                  L('Агент-в-коробке уже продаётся (Jetson-приставка с агентным стеком, €549). На закрытом кремнии, без аттестации, без квитанций: проверить, что агент сделал, нельзя в принципе.',
                    'The agent-in-a-box already sells (a Jetson appliance with an agent stack, €549). Closed silicon, no attestation, no receipts: what the agent did cannot be verified even in principle.')),
        ('gold', L('Дыра — на пересечении.','The hole is at the intersection.'),
                 L('Проверяемое устройство существует (Precursor). Агент существует (ClawBox). Тернарный LLM на FPGA существует (в статьях). Проверяемого агента не делает никто.',
                   'The verifiable device exists (Precursor). The agent exists (ClawBox). Ternary LLMs on FPGAs exist (in papers). Nobody ships a verifiable agent.')),
    ])
    slide(d, lang, L('Продукт','Product'), L('Лестница: каждая ступень продаётся сама и кормит следующую','A ladder: each rung sells alone and feeds the next'), [
        ('table',
         [L('Ступень','Rung'), L('Что это','What it is'), L('Железо','Hardware'), L('Статус','Status')],
         [[ 'v0 · TRI CLAW',
            L('агент, которого можно проверить: аттестация при загрузке (Phi), BLAKE3-квитанция на действие (Euler), тернарный движок при пустой колонке DSP (Gamma)',
              'an agent you can audit: attestation at boot (Phi), a BLAKE3 receipt per action (Euler), a ternary engine with an empty DSP column (Gamma)'),
            L('серийная плата Artix-7 200T; своего железа ноль','stock Artix-7 200T board; zero custom hardware'),
            L('концепт опубликован; ток/с не измерены','concept published; tok/s unmeasured')],
          [ 'v1 · TRI-NET NODE',
            L('v0 + mesh-радио с печатями покрытия: байты через два радиоскачка байт-в-байт, печать сошлась в 3 точках',
              'v0 + mesh radio with coverage seals: bytes across two radio hops byte-exact, the seal agreed at 3 points'),
            L('Pluto/uSDR-класс; партнёрский путь железа','Pluto/uSDR class; a partner hardware path'),
            L('демо есть; пропускная способность не измерена','demo exists; throughput unmeasured')],
          [ L('v2 · TRI PHONE — ФЛАГМАН','v2 · TRI PHONE — FLAGSHIP'),
            L('карман: экран, клавиатура, батарея, mesh; TRIOS + TRI CLAW; каждый слой проверяем',
              'pocket device: display, keyboard, battery, mesh; TRIOS + TRI CLAW; every layer auditable'),
            L('своё устройство класса Precursor','a Precursor-class device of our own'),
            L('видение; открытые вопросы названы','a vision; open questions named')]],
         [150, 370, 200, 160]),
        ('gap', 6),
        ('point', L('Три кристалла, которые не доехали до фабрики, — это и есть три слоя.','The three dies that never reached the foundry are the three layers.'),
                  L('TRI-1 Phi / Euler / Gamma: RTL зелёный в CI, GDS собирается открытым потоком, конформанс-векторы, Apache-2.0, DOI 10.5281/zenodo.19227877. Кремния нет — и он не нужен: слои доставляются как гейтвер.',
                    'TRI-1 Phi / Euler / Gamma: RTL green in CI, GDS built by the open flow, conformance vectors, Apache-2.0, DOI 10.5281/zenodo.19227877. No silicon exists — and none is needed: the layers ship as gateware.')),
    ])
    slide(d, lang, L('TRI CLAW · v0','TRI CLAW · v0'), L('Агент, которого можно проверить — пустое пересечение рынка','An agent you can audit — the market’s empty intersection'), [
        ('table',
         [L('Кто','Who'), L('Что','What'), L('Чего нет','What is missing')],
         [[L('Агент-боксы (Jetson)','Agent boxes (Jetson)'), L('агент-приставка, €549','agent appliance, €549'), L('ни аттестации, ни квитанций, ни открытого битстрима','no attestation, no receipts, no open bitstream')],
          ['Precursor', L('проверяемый карманник на FPGA; >$220k на Crowd Supply','a verifiable FPGA pocket device; >$220k on Crowd Supply'), L('нет ИИ','no AI')],
          ['TeLLMe / TerEffic / LUT-LLM', L('тернарные LLM-движки на edge-FPGA','ternary LLM engines on edge FPGAs'), L('статьи, не продукты; проверяемость — не предмет','papers, not products; verification not the point')],
          ['TRI CLAW', L('пересечение всех трёх','the intersection of all three'), L('концепт + три слоя гейтвера; ток/с не измерены','a concept + three gateware layers; tok/s unmeasured')]],
         [190, 330, 360]),
        ('gap', 4),
        ('gold', L('Предел открытого флоу — 7-я серия. Здесь это достоинство.','The open flow ends at the 7-series. Here that is a feature.'),
                 L('Precursor выбрал 7-ю серию как самый изученный кремний. Агент, продающий доверие, целится в кремний, которому можно продуктивно не доверять. В этом флоу — 27 наших влитых исправлений.',
                   'Precursor chose the 7-series as the most-studied silicon. An agent that sells trust targets silicon one can productively distrust. That flow carries 27 of our merged fixes.')),
    ])
    slide(d, lang, L('Решение и ценность','Solution & value'), L('Под лестницей — стенд: продаём не формат, а доказательство','Under the ladder, the rig: we sell proof, not a format'), [
        ('point', L('Реализация — синтезируемые декодеры и арифметические ядра.','Implementation — synthesisable decoders and arithmetic cores.'),
                  L('RTL, прошедший открытый поток на реальном железе, отдаётся с теми же командами синтеза, что дали числа. Без Vivado в контуре.',
                    'RTL that passed the open flow on real hardware ships with the same synthesis commands that produced the numbers. No Vivado in the loop.')),
        ('point', L('Conformance-стенд — точные по битам векторы плюс независимый второй оракул.','The conformance rig — bit-exact vectors plus an independent second oracle.'),
                  L('Скопировать формат — вечер работы; воспроизвести корпус соответствия, которому команда чипа поверит, — нет. Это и есть ров.',
                    'Copying a format is an evening’s work; reproducing a conformance corpus a chip team will trust is not. That is the moat.')),
        ('point', L('Теория, которая говорит, какие форматы вообще могут существовать.','Theory that says which formats can exist at all.'),
                  L('Т25 закрепляет трёхсимвольный алфавит весов единственностью; Т27 перечисляет безумножительные масштабы. Т26: в Z[φ] линейная часть сети считается без ошибки округления — машинно проверено в Coq. Это свойство решётки, а не преимущество φ.',
                    'T25 pins the three-symbol weight alphabet by uniqueness; T27 enumerates the multiplier-free scales. T26: in Z[φ] the network’s linear part computes with zero rounding error — machine-checked in Coq. A lattice property, not a φ advantage.')),
        ('gold', L('TRI CLAW стоит на этом стенде.','TRI CLAW stands on this rig.'),
                 L('Аттестация, квитанции и тернарный движок — те же RTL-блоки, та же дисциплина векторов. Продукт не заменяет бизнес соответствия — он его витрина.',
                   'Attestation, receipts and the ternary engine are the same RTL blocks, the same vector discipline. The product does not replace the conformance business — it is its storefront.')),
    ])
    metrics_slide(d, lang, L('Измерено','Measured'), L('Что существует до денег','What exists before any money'),
        L('Каждая цифра получена открытым тулчейном на названной микросхеме. Частоты не заявляются: см. границы внизу.',
          'Every figure below came from the open toolchain on a named part. No frequencies are claimed: see the boundary line.'),
        [(L('66 LUT','66 LUT'), L('ИЗМЕРЕНО','MEASURED'), L('декодер GFTernary, XC7A200T; голый провод — 112 LUT','GFTernary decoder, XC7A200T; bare wire is 112 LUT')),
         ('38×', L('ИЗМЕРЕНО','MEASURED'), L('сумматор: 397 LUT против 15 251 у tekum8','adder: 397 LUT vs 15,251 for tekum8')),
         ('1.4–1.9× / 3.2–4.1×', L('ИЗМЕРЕНО','MEASURED'), L('развёрнутый тернарный узел против int4/int8, веер 8–64, пост-синтез; ряд немонотонен: 56.2→75.4→66.8→68.1','unfolded ternary node vs int4/int8, fan-in 8–64, post-synthesis; series non-monotonic: 56.2→75.4→66.8→68.1')),
         ('0', L('МАШИННО ПРОВЕРЕНО В COQ','MACHINE-CHECKED IN COQ'), L('ошибки округления на линейной части в Z[φ], Т26','rounding error on the linear path in Z[φ], T26')),
         ('52 / 83', L('ДОКАЗАНО','PROVEN'), L('теорем в статье / форматов в каталоге','theorems in the paper / formats in the catalogue')),
         ('27', L('ВЛИТО АПСТРИМ','MERGED UPSTREAM'), L('исправлений в nextpnr-xilinx — флоу, которым всё это собрано','fixes merged into nextpnr-xilinx — the flow that builds all of this')),
         ('2', L('РАДИОСКАЧКА','RADIO HOPS'), L('байт-в-байт, печать покрытия сошлась в 3 точках: 0x9DBE2510','byte-exact; the coverage seal agreed at 3 points: 0x9DBE2510')),
         ('9', L('ЧУЖОЕ, НЕ НАШЕ','THEIRS, NOT OURS'), L('ток/с TeLLMe на KV260 при 7 Вт — существование, не перенос','TeLLMe tok/s on a KV260 at 7 W — existence, not transfer'))],
        L('Граница заявления, проведённая нами','The claim boundary, drawn by us'),
        L('Кремния нет. Тернарной ткани не было. Энергия не измерялась. Ток/с TRI CLAW на A200T не измерены. TRIOS на встраиваемом ядре не запускался. Числа узла — пост-синтез на развёрнутой схеме, не post-P&R на свёрнутой.',
          'No silicon. No ternary fabric was used. Energy unmeasured. TRI CLAW tok/s on the A200T unmeasured. TRIOS has never run on an embedded core. Node figures are post-synthesis on an unfolded circuit, not post-P&R on a folded one.'))
    slide(d, lang, L('Рынок','Market'), L('Считаем снизу, по чужим кассам','Bottom-up, from other people’s tills'), [
        ('point', L('Устройство класса Precursor краудфандится: >$220k, <500 штук, $512–768.','A Precursor-class device crowdfunds: >$220k, <500 units, $512–768.'),
                  L('Проверяемость сама по себе вывезла кампанию. Crowd Supply даёт полный цикл (комиссия ~12%, Matching Funds 50–100% сверху, логистика Mouser).',
                    'Verifiability alone carried the campaign. Crowd Supply is full-service (~12% fee, Matching Funds 50–100% on top, Mouser logistics).')),
        ('point', L('Аудитория уже посчитана соседями: 190 бэкеров uSDR × $339–899 = $128k.','The audience is already counted by neighbours: 190 uSDR backers × $339–899 = $128k.'),
                  L('Инженеры открытого радио и открытого железа — ровно те, кто покупает и Precursor, и агент-боксы.',
                    'Open-radio and open-hardware engineers — the same people who buy Precursor and agent boxes.')),
        ('point', L('Слой IP-бизнеса под этим не исчезает.','The IP layer underneath does not go away.'),
                  L('Рынок полупроводникового IP — $9.8 млрд (2025); прокси лицензии ~$1.2 млн; роялти по ставкам, которые публикует Arm. Продукт — витрина стенда, не его замена.',
                    'The semiconductor IP market is $9.8B (2025); a licence proxy is ~$1.2M; royalties at rates Arm discloses. The product is the rig’s storefront, not its replacement.')),
    ])
    slide(d, lang, L('Бизнес-модель','Business model'), L('Пять полос выручки, все продаются командам, не пользователям','Five revenue lanes, all sold to teams, not end users'), [
        ('table',
         [L('Слой','Layer'), L('Что получает заказчик','What the customer gets'), L('Цена / цикл','Price / cycle')],
         [[L('Продукт TRI CLAW (v0)','TRI CLAW product (v0)'), L('гейтвер+стек на серийной плате; кампания на Crowd Supply после измерения ток/с','gateware+stack on a stock board; a Crowd Supply campaign after tok/s is measured'), L('$500–800/шт, прецедент Precursor','$500–800/unit, Precursor precedent')],
          [L('Лицензия на ядро','Core licence'), L('синтезируемый декодер или ядро: RTL + команды синтеза','a synthesisable decoder or core: RTL + synthesis commands'), L('за проект; прокси ~$1.2 млн / 6–12 мес','per project; proxy ~$1.2M / 6–12 mo')],
          [L('Conformance-стенд','Conformance rig'), L('точные по битам векторы, второй оракул, сиды и поток','bit-exact vectors, second oracle, seeds and flow'), L('годовая подписка','annual subscription')],
          [L('Роялти','Royalties'), L('с единицы отгруженного кремния','per unit of shipped silicon'), L('Arm раскрывает ~5% как сопоставимое','Arm discloses ~5% as comparable')],
          [L('Измерение как услуга','Measurement as a service'), L('заказчик присылает RTL — меряем тем же стендом и сидами','customer sends RTL — measured on the same rig and seeds'), L('фикс / 30–60 дней','fixed / 30–60 days')]],
         [170, 430, 280]),
        ('gap', 2),
        ('gold', L('Ров — стенд и дисциплина, не патенты.','The moat is the rig and the discipline, not patents.'),
                 L('Препринты и открытый RTL создают приоритет публикации, а не исключительность. Защитимый актив — корпус, которому команда чипа поверит, и публичная запись снятых заявлений.',
                   'Preprints and open RTL create publication priority, not exclusivity. The defensible asset is a corpus a chip team will trust — and the public record of withdrawn claims.')),
    ])
    slide(d, lang, L('Команда','Team'), L('Один инженер, один стенд, публичная запись ошибок','One engineer, one rig, a public record of mistakes'), [
        ('point', L('Дмитрий Васильев — основатель.','Dmitrii Vasilev — founder.'),
                  L('Инженер FPGA/RTL и hardware-AI. Ведёт линию сам: спецификация → RTL → открытый поток → измерение → статья. Два публичных препринта (arXiv 2606.05017, 2606.09686), каталог 83 форматов, третья статья с 52 теоремами (Coq там, где указано), 27 влитых исправлений в nextpnr-xilinx, стенд из трёх плат ALINX AX7203.',
                    'FPGA/RTL and hardware-AI engineer. Runs the whole line: spec → RTL → open flow → measurement → paper. Two public preprints (arXiv 2606.05017, 2606.09686), an 83-format catalogue, a third paper with 52 theorems (Coq where stated), 27 merged nextpnr-xilinx fixes, a rig of three ALINX AX7203 boards.')),
        ('point', L('Редкое — не математика и не RTL.','The rare part is neither the maths nor the RTL.'),
                  L('Один человек доводит утверждение от теоремы до разведённого числа и публикует отзывы собственных заявлений. Эта же дисциплина вшита в продукт: квитанции, аттестация, открытый битстрим.',
                    'One person carries a claim from theorem to placed-and-routed number and publishes his own retractions. The same discipline is baked into the product: receipts, attestation, an open bitstream.')),
    ])
    slide(d, lang, L('Дорожка','Roadmap'), L('Три шага, и каждый проверяем со стороны','Three steps, each externally checkable'), [
        ('point', L('1 · Измерить ток/с малой тернарной модели (0.1–0.7B) на A200T.','1 · Measure tok/s of a small ternary model (0.1–0.7B) on the A200T.'),
                  L('Table-lookup matmul — тот же приём, на котором сошлась академия. Число публикуется, каким бы ни вышло. Это гейт всей лестницы.',
                    'Table-lookup matmul — the approach academia converged on. The number gets published whatever it turns out to be. This gates the whole ladder.')),
        ('point', L('2 · TRIOS-минимум на слабом ядре + демо 90 секунд.','2 · A minimal TRIOS on a weak core + a 90-second demo.'),
                  L('Загрузка → аттестация → задача агента → квитанция → проверка квитанции на другом компьютере.',
                    'Boot → attestation → one agent task → one receipt → the receipt verified on a different computer.')),
        ('point', L('3 · Заявка на Crowd Supply с числом в руках.','3 · Apply to Crowd Supply with the number in hand.'),
                  L('Сосед по полке — Precursor. Открытые вопросы (имя «claw» занято соседями; юрлицо и комплаенс площадки; батарея не мерена) идут в кампанию первым разделом, как это принято у нас.',
                    'The shelf neighbour is Precursor. The open questions (the “claw” name space is crowded; entity and platform compliance; battery unmeasured) go into the campaign as its first section, as is our habit.')),
        ('gold', L('Три вещи, которые стоит запомнить.','Three things worth remembering.'),
                 L('Проверяемого агента не делает никто; наши три недоехавших кристалла — готовые слои такого агента; и всё, чего мы не знаем, написано на этом слайде, а не спрятано.',
                   'Nobody ships a verifiable agent; our three unfabricated dies are that agent’s ready-made layers; and everything we do not know is written on this slide, not hidden.')),
    ])
    d.c.save()
    print(f'{path}: {d.page} слайдов')

if __name__ == '__main__':
    build('ru', os.path.join(HERE, 'trinity-s3ai-deck-ru.pdf'))
    build('en', os.path.join(HERE, 'trinity-s3ai-deck-en.pdf'))
