#!/usr/bin/env python3
"""Generate the static landing pages served at t27.ai/<slug>/.

Why these are static rather than stubs that bounce into the SPA:

The site is a HashRouter app, so every route lives behind a fragment, and a
fragment is never sent to a server. The clean paths used to be one-line stubs
that ran location.replace('/#/<slug>'). A crawler executing that redirect ends
up at a URL differing from '/' only by its fragment — which it discards — so
every commercial page collapsed into the homepage and none of them could rank
for anything. Meta tags alone do not fix that: a page with no body is thin
content whatever its og: tags say.

So these pages carry the real copy, statically, with no redirect. They are
faster than the SPA (no 800KB bundle), they index, and they link onward to the
app for anyone who wants the interactive site.

The copy here is deliberately a condensation, not a clone, of the React pages:
enough to inform and convert, short enough that keeping the two in step is a
minute's work rather than a chore.

    python3 build-landing.py     # rewrites <slug>/index.html and sitemap.xml
"""

import html
import os

SITE = "https://t27.ai"
EMAIL = "admin@t27.ai"
SAMPLE = "https://github.com/gHashTag/trinity/blob/main/docs/verification/SAMPLE-REPORT.md"

PAGES = {
    "verification": {
        "title": "Hardware-verified RTL — measured on live silicon",
        "eyebrow": "Verification service",
        "h1": "Not simulated. Measured on live silicon.",
        "desc": (
            "Send your RTL and get it measured on a live Xilinx Artix-7: bit-exact conformance against "
            "an independent reference model, achieved timing, resources and the bitstream — on a fully "
            "open-source flow. From $300 per core, first module free."
        ),
        "lede": (
            "Send your RTL. It runs on a real Xilinx Artix-7 and comes back with a signed report: "
            "bit-exact conformance against an independent model, achieved timing, resource usage, and "
            "the bitstream — on a fully open-source toolchain, so every number can be reproduced."
        ),
        "sections": [
            ("What the report contains", [
                ("Bit-exact conformance", "Every node of your datapath checked against an independent reference model with known-answer vectors. Divergence between specification and RTL surfaces before synthesis, not after tape-out."),
                ("Timing and resources", "Achieved frequency, slack, LUT/FF/BRAM/DSP usage and a latch-free check — measured on a live Artix-7, not estimated from a report."),
                ("Reproducible artefacts", "Bitstream, test vectors, logs and the exact toolchain versions, so anyone can re-run the whole flow themselves."),
                ("No vendor lock-in", "Yosys, nextpnr-xilinx, prjxray, openFPGALoader, iverilog. Nothing in the report depends on a proprietary licence you would need to buy."),
            ]),
            ("How it works", [
                ("1. You send RTL or a specification", "And say what “correct” means for it."),
                ("2. I build an independent model", "Written from the operation, never from your RTL — a testbench derived from the same assumptions as a design agrees with the design's bugs."),
                ("3. You get a signed report", "Measured numbers, vectors, bitstream, and every command needed to reproduce it."),
            ]),
            ("Pricing", [
                ("Single core — $300", "One module or IP core: bit-exact check, timing, resources, report."),
                ("Block — $800", "A full block with multiple cores, integration checks and a written analysis."),
                ("Tape-out ready — $2 000", "Everything above plus the preparation a shuttle submission needs."),
                ("Retainer — $1–3k / month", "Ongoing verification as your design changes."),
            ]),
            ("What this is not", [
                ("One device family", "Measurements come from a Xilinx Artix-7. This is not multi-corner characterisation and does not claim to be."),
                ("Not a sign-off flow", "It is an independent check, not a substitute for a full commercial sign-off."),
                ("No encrypted netlists", "I verify what I can read. Encrypted IP cannot be checked this way."),
                ("Estimates are labelled", "Anything estimated rather than measured says so, here and in every report."),
            ]),
        ],
        "cta": "Have a design to verify? The first module is free, so you can judge the report before paying for anything.",
    },
    "proof": {
        "title": "Every number here was measured",
        "eyebrow": "Measured evidence",
        "h1": "Every number here was measured.",
        "desc": (
            "Every hardware claim behind this site with the measurement that produced it — a GF16 matmul "
            "that needs no hard multipliers, a neural network training on-chip, a SKY130 tape-out — and a "
            "plain statement of what these results are not, including one figure withdrawn."
        ),
        "lede": (
            "Hardware claims are cheap to make and hard to check, so this page collects the results behind "
            "everything else: what was built, what it measured, and how it was verified. Where something is "
            "a submission rather than a win, or a prototype rather than a product, it says so."
        ),
        "sections": [
            ("Results", [
                ("GF16 4×4 matmul — 32,252 LUT with zero hard multipliers", "A 4×4 matrix multiplier over my own GF16 format, synthesised for Artix-7. It maps into fabric with no DSP48 blocks at all, or 21,223 LUTs if the 64 hard multipliers are allowed. The block is combinational — no registers, so no clock and no frequency figure belongs to it."),
                ("100% held-out — a network that trains on the FPGA", "Forward pass, gradient and weight update all in RTL with no host in the loop. A 2-layer ReLU network learns XOR on the chip itself, 4 of 4 correct, every node bit-exact from specification to silicon."),
                ("SKY130 — tape-out through Tiny Tapeout", "The same source that runs on the FPGA went to an open ASIC process: GDS produced, gate-level test passed, precheck passed."),
                ("≈3–5.5× — GF-T against comparable formats", "A ternary floating-point format of my own design, best-in-class against comparable ternary formats at mid and far range. No regime decode, native ternary exponent."),
                ("Over the air — tri-net, a full ternary network stack", "133 formal specifications: GF16 physical layer, BPSK modem on AD9361, ETX mesh routing, ChaCha20-Poly1305 / X25519 crypto. Text and images carried between physically separate boards."),
                ("83 formats — a conformance catalogue", "Bit-exact test vectors for FP8, BF16, MXFP4 and microscaling formats: a vendor-neutral reference for verifying low-precision arithmetic."),
            ]),
            ("How any of this is checked", [
                ("Independent model, not a mirror", "The reference model is written from the specification, never from the RTL."),
                ("Per-stage vectors", "Known-answer vectors at every pipeline stage, so a regression points at the stage that broke."),
                ("Hardware replay", "The same vectors run again on the physical board. Simulation agreement does not prove silicon agreement."),
                ("Open toolchain", "Yosys, nextpnr-xilinx, prjxray, openFPGALoader, iverilog. No proprietary licence stands between a claim here and someone reproducing it."),
            ]),
            ("What these results are not", [
                ("Entries are entries", "A DARPA CLARA submission and an OpenAI Parameter Golf entry are submitted work, not awarded contracts or won prizes."),
                ("One device family", "Measurements come from a Xilinx Artix-7 and are not multi-corner characterisation."),
                ("Training is a primitive", "The on-chip training result is proven at small scale: a real network learning on real silicon, not a production training accelerator."),
                ("Estimates are labelled", "Anything estimated rather than measured is labelled as estimated."),
                ("A figure withdrawn", "This page previously reported 323 MHz and 41.2 GOPS for the GF16 matmul. Re-checking the RTL on 8 August 2026 showed the block holds no registers, so it has no clock and no frequency can belong to it. Withdrawn rather than explained away."),
            ]),
        ],
        "cta": "The papers, the source and a full example report are all public. A claim you cannot verify is just a sentence.",
    },
    "ip": {
        "title": "Arithmetic cores that have already been to silicon",
        "eyebrow": "IP licensing",
        "h1": "Arithmetic cores that have already been to silicon.",
        "desc": (
            "License arithmetic cores measured on real hardware: the GF-T ternary multiplier, a GF16 4×4 "
            "matmul that maps into fabric with no hard multipliers, a BPSK modem proven over the air, and on-chip "
            "training primitives. RTL, reference model and the vectors that prove it."
        ),
        "lede": (
            "Every core here was designed, verified bit-exact against an independent model, and measured on "
            "real hardware — one of them through a SKY130 tape-out. You license the RTL, the reference model "
            "and the vectors that prove it, so you can check the claims instead of trusting them."
        ),
        "sections": [
            ("Available cores", [
                ("GF-T multiplier — ternary arithmetic", "The multiplier for GF-T, a ternary floating-point format benchmarking best-in-class (≈3–5.5× against comparable formats). Published as arXiv:2606.05017 with an independent reference model and bit-exact vectors."),
                ("GF16 4×4 matmul — matrix engine", "Maps entirely into fabric, leaving the DSP columns free for the rest of your system: 32,252 LUTs with zero DSP48, or 21,223 LUTs if the 64 hard multipliers are allowed. Combinational, 0 latches."),
                ("BPSK modem — radio PHY", "Built for software-defined radio (AD9361), part of a full ternary network stack with mesh routing and authenticated encryption. Proven device-to-device over the air."),
                ("On-chip training primitives — edge ML", "Neural primitives that perform their own backward pass on the FPGA: forward, gradient and weight update in RTL, no host in the loop. 100% held-out on real silicon."),
            ]),
            ("What a licence includes", [
                ("Readable RTL", "Synthesisable and readable, not obfuscated."),
                ("An independent reference model", "The thing that lets you prove the core is right rather than believe it."),
                ("Per-stage vectors", "Bit-exact test vectors per pipeline stage, so a regression tells you which stage broke."),
                ("A measured report", "Frequency, resources and a latch-free check on real hardware."),
                ("Integration help", "A core that does not land in your system is worth nothing."),
            ]),
            ("Terms", [
                ("Evaluation — from $500", "Source and vectors for a single project, so you can measure it in your own flow first."),
                ("Single project — from $2 500", "Use in one product, with integration support and the verification harness."),
                ("Production / multi-project — quoted", "Broader rights negotiated per case, including royalty-based terms."),
                ("Custom arithmetic — from $150/h", "A format or datapath designed for your constraints, with the same bit-exact verification."),
            ]),
        ],
        "cta": "Tell me the device and the budget you are working against. If none of these cores is right, I will say so — and quote for one built to fit.",
    },
    "course": {
        "title": "Train a neural network on an FPGA",
        "eyebrow": "Course",
        "h1": "Train a neural network on an FPGA.",
        "desc": (
            "Eight modules from an empty toolchain to a neural network performing its own backward pass on "
            "live silicon. Entirely open-source: no Vivado, no licences, no step you cannot reproduce."
        ),
        "lede": (
            "Not inference — training, on the chip itself. Eight modules from an empty toolchain to a network "
            "that learns on live silicon, entirely on open tools: no Vivado, no licences, and no step you "
            "cannot reproduce yourself."
        ),
        "sections": [
            ("Eight modules", [
                ("01 · The open flow from nothing", "Yosys, nextpnr-xilinx, prjxray, openFPGALoader and iverilog installed and verified on macOS arm64 or Linux. First bitstream blinking an LED on a real board, no vendor licence anywhere in the chain."),
                ("02 · Exactly as much Verilog as you need", "Synchronous design, registers versus latches, and why an accidental latch is the classic bug that only shows up on silicon."),
                ("03 · Arithmetic as the foundation of ML in hardware", "Why float is expensive, what quantisation really costs, and where ternary and low-precision formats come from."),
                ("04 · Bit-exact verification — the heart of the course", "An independent Python reference model, per-stage known-answer vectors, checked through iverilog. Why a testbench written from the design's own assumptions cheerfully agrees with its bugs."),
                ("05 · A matrix multiplier that closes timing", "MAC to array to pipeline. Reading the router's timing report and fighting for frequency on a real example — including why a hard multiplier in the path can leave you with no frequency report at all."),
                ("06 · Neural network inference on the FPGA", "Layers, activations, dataflow and on-chip memory, running on the board rather than in a simulator."),
                ("07 · On-chip training — the capstone", "Backward pass and SGD in RTL. The network learns XOR on the FPGA itself, 4 of 4, bit-exact against the reference. Almost nobody has done this by hand."),
                ("08 · Onward to silicon", "The Tiny Tapeout path: preparing a design, what changes between FPGA and ASIC, and where the open silicon ecosystem stands after the move to IHP."),
            ]),
            ("How this differs from the free alternatives", [
                ("hls4ml (CERN) — free", "Inference only, generated through HLS, and the flow underneath is a vendor toolchain. Excellent at what it does — it does not train on the chip, and it does not leave you able to read the RTL it produced."),
                ("Vendor courses (Intel, AMD) — free", "Built to teach you their tools on their silicon. Nothing transfers to a flow you can run without a licence."),
                ("University FPGA courses", "Usually stop at simulation, and where they reach a board it is through Vivado or Quartus."),
                ("What is left", "Two things exist nowhere on that list: a backward pass running on the chip itself, and a flow with no vendor licence in it. If inference through HLS is what you need, use hls4ml — it is good, it is free, and I would tell you the same in an email."),
            ]),
            ("Formats", [
                ("Self-paced — $149", "Video, code, KAT vector sets, community access."),
                ("Self-paced + hardware — $249", "The same, plus remote runs on my Artix-7 boards. No board of your own required."),
                ("Cohort, 4 weeks — $599", "Live sessions, code review, and your own design gone through with you."),
                ("Team workshop — from $2 000", "Two days with your engineers around a problem you actually have."),
            ]),
        ],
        "cta": "Basic Python and some idea of digital logic is enough. Verilog is taught from scratch, and two of the formats include runs on my hardware.",
    },
    "about": {
        "title": "Dmitrii Vasilev — hardware-AI and FPGA/RTL engineer",
        "eyebrow": "About",
        "h1": "From an arXiv paper to a fabricated chip.",
        "desc": (
            "Dmitrii Vasilev — hardware-AI and FPGA/RTL engineer. Designer of the GF-T ternary "
            "floating-point format, taken from an arXiv paper through RTL that needs no hard multipliers "
            "to a SKY130 tape-out, entirely on open-source tools."
        ),
        "lede": (
            "I design number formats and the silicon that runs them. GF-T started as a paper, became RTL "
            "that maps into Artix-7 fabric with no hard multipliers at all, and went through a SKY130 tape-out — "
            "on a toolchain anyone can install for free. Before hardware I spent a decade building products "
            "and teaching: over a thousand developers, and the first React Native course in the "
            "Russian-speaking internet."
        ),
        "sections": [
            ("What I do", [
                ("Custom arithmetic", "Number formats designed against your constraints — ternary, low-precision, φ-based — each with an independent reference model and bit-exact vectors, not just a claim."),
                ("RTL to silicon", "Synthesisable Verilog through an open flow: Yosys, nextpnr-xilinx, prjxray, iverilog. Measured on three Artix-7 boards I own, and taken to SKY130 when it needs to be."),
                ("Verification", "Bit-exact conformance against models written from the specification rather than from the design — the only kind of check that can disagree with the RTL."),
                ("Teaching", "Over a thousand developers taught. Hardware is the current subject; the method has not changed."),
            ]),
            ("Published", [
                ("arXiv:2606.05017 — GoldenFloat", "A φ-based floating-point family, GF4 through GF1024, with the reference implementations that make it checkable."),
                ("arXiv:2606.09686 — 83 numeric formats", "A conformance catalogue with bit-exact vectors for FP8, BF16, MXFP4 and microscaling formats, published so anyone can validate their own arithmetic against it."),
            ]),
            ("Working with me", [
                ("Remote, UTC+7", "Based in Thailand, working with teams across Europe and North America."),
                ("Open tools by default", "Nothing I deliver requires you to buy a licence to reproduce it."),
                ("Available", "Contract and part-time hardware-AI, FPGA/RTL and ML-systems work."),
            ]),
        ],
        "cta": "The CV, the papers and the source are all one click away. If the work looks relevant, write — I answer.",
    },
    "cases": {
        "title": "Verification runs on other people's RTL",
        "eyebrow": "Case studies",
        "h1": "What other people's designs turned out to be.",
        "desc": (
            "What each verification run turned out to be: what was checked, what the bit-exact check "
            "surfaced, and the numbers measured on a live Artix-7. Empty until the first free run finishes."
        ),
        "lede": (
            "Every run ends in a report: what was checked, what it surfaced, and the numbers taken off the "
            "board. They are collected here, with the client's permission and without edits in my favour."
        ),
        "sections": [
            ("Empty for now, and honestly so", [
                ("Nothing has finished yet", "The first runs are free, and until one of them finishes there will be nothing here. An invented case study would be worth less than an empty page: the whole offer rests on the numbers being measured."),
                ("Read the sample instead", "A full example report on my own design, with the same sections yours would get: bit-exact conformance, achieved timing, resources, latch-free check, and the commands to reproduce all of it."),
            ]),
        ],
        "cta": "Want to be the first? The first runs are free and the report is yours to publish or keep.",
    },
}

NAV = [
    ("verification", "Verification"),
    ("proof", "Evidence"),
    ("ip", "Licensing"),
    ("course", "Course"),
    ("cases", "Case studies"),
    ("about", "About"),
]

CSS = """*,*::before,*::after{box-sizing:border-box}
:root{--bg:#05070a;--card:#0b1014;--ink:#e9f1ee;--muted:#8fa79f;--accent:#00ff88;--rule:#1b2724}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--accent)}
.wrap{max-width:820px;margin:0 auto;padding:28px 20px 72px}
header.top{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;padding-bottom:18px;border-bottom:1px solid var(--rule)}
.brand{font-weight:700;letter-spacing:.18em;font-size:12px;color:var(--accent);text-decoration:none}
/* Inline anchors wrap by word, which split "CASE STUDIES" across two lines and
   pushed "CASE" off the right edge at 375px. Flex with a gap wraps whole items. */
nav.top{display:flex;flex-wrap:wrap;gap:6px 14px}
nav.top a{font-size:12px;text-transform:uppercase;letter-spacing:.08em;text-decoration:none;color:var(--muted);white-space:nowrap}
nav.top a:hover,nav.top a[aria-current]{color:var(--accent)}
.eyebrow{color:var(--accent);text-transform:uppercase;letter-spacing:.14em;font-size:12px;margin:38px 0 10px}
h1{font-size:clamp(1.9rem,5.5vw,2.7rem);line-height:1.15;margin:0 0 14px;text-wrap:balance}
.lede{font-size:1.08rem;color:var(--muted);margin:0 0 26px;max-width:62ch}
h2{font-size:1.25rem;margin:40px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--rule)}
.items{display:grid;gap:14px}
.item{background:var(--card);border:1px solid var(--rule);border-radius:14px;padding:16px 18px}
.item h3{font-size:1rem;margin:0 0 6px;color:var(--accent)}
.item p{margin:0;font-size:.95rem;color:#c6d5d0}
.cta{margin-top:42px;background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:24px}
.cta p{margin:0 0 16px;color:#c6d5d0}
.btn{display:inline-block;background:var(--accent);color:#04140d;font-weight:700;text-decoration:none;padding:12px 24px;border-radius:999px;font-size:.92rem}
.btn.sec{background:transparent;color:var(--ink);border:1px solid var(--rule);font-weight:500}
.btns{display:flex;flex-wrap:wrap;gap:10px}
footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--rule);color:var(--muted);font-size:.85rem}
footer a{color:var(--muted)}
@media(prefers-color-scheme:light){:root{--bg:#fbfdfc;--card:#fff;--ink:#101a17;--muted:#5b6f68;--accent:#0a7a4c;--rule:#dde7e3}.item p{color:#394944}.cta p{color:#394944}.btn{color:#fff}}
"""


def render(slug, p):
    url = f"{SITE}/{slug}/"
    nav = "".join(
        f'<a href="/{s}/"{" aria-current=\"page\"" if s == slug else ""}>{html.escape(label)}</a>'
        for s, label in NAV
    )
    body = []
    for heading, items in p["sections"]:
        body.append(f"<h2>{html.escape(heading)}</h2>\n<div class=\"items\">")
        for name, text in items:
            body.append(
                f'<div class="item"><h3>{html.escape(name)}</h3><p>{html.escape(text)}</p></div>'
            )
        body.append("</div>")
    sections = "\n".join(body)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(p['title'])} · TRINITY</title>
<meta name="description" content="{html.escape(p['desc'])}" />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="TRINITY" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{html.escape(p['title'])}" />
<meta property="og:description" content="{html.escape(p['desc'])}" />
<meta property="og:image" content="{SITE}/og-{slug}.svg" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{html.escape(p['title'])}" />
<meta name="twitter:description" content="{html.escape(p['desc'])}" />
<link rel="icon" href="/favicon.svg" />
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="brand" href="/">T27.AI</a>
  <nav class="top">{nav}</nav>
</header>

<p class="eyebrow">{html.escape(p['eyebrow'])}</p>
<h1>{html.escape(p['h1'])}</h1>
<p class="lede">{html.escape(p['lede'])}</p>

{sections}

<div class="cta">
  <p>{html.escape(p['cta'])}</p>
  <div class="btns">
    <a class="btn" href="mailto:{EMAIL}?subject={html.escape(p['title'])}">{EMAIL}</a>
    <a class="btn sec" href="{SAMPLE}">Read a sample report</a>
    <a class="btn sec" href="/#/{slug}">Open the interactive site</a>
  </div>
</div>

<footer>
  Dmitrii Vasilev — hardware-AI and FPGA/RTL engineer.
  <a href="https://github.com/gHashTag">GitHub</a> ·
  <a href="https://linkedin.com/in/neurocoder">LinkedIn</a> ·
  <a href="{SITE}/cv.pdf">CV</a> ·
  <a href="https://arxiv.org/abs/2606.05017">arXiv:2606.05017</a> ·
  <a href="https://arxiv.org/abs/2606.09686">arXiv:2606.09686</a>
</footer>
</div>
</body>
</html>
"""


def sitemap(slugs):
    urls = "".join(
        f"\n  <url><loc>{SITE}/{s}</loc></url>" for s in [""] + [f"{x}/" for x in slugs]
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}\n</urlset>\n'


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    for slug, p in PAGES.items():
        os.makedirs(slug, exist_ok=True)
        with open(f"{slug}/index.html", "w", encoding="utf-8") as fh:
            fh.write(render(slug, p))
        print(f"wrote {slug}/index.html")
    with open("sitemap.xml", "w", encoding="utf-8") as fh:
        fh.write(sitemap(list(PAGES)))
    with open("robots.txt", "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("wrote sitemap.xml, robots.txt")
