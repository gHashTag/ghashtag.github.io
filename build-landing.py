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
# The pre-filled issue the verify-request workflow answers on its own. These
# static landings are the pages a stranger reaches from search, and until now
# the available way to start anything from them was to compose an email — the run
# has an entry point that needs no inbox, so it belongs on the page that gets
# found. Pages where a run is the next step get the button.
REQUEST_URL = "https://github.com/gHashTag/trinity/issues/new?template=verification-request.yml"
RUNNABLE = {"verification", "cases"}
EMAIL = "admin@t27.ai"
SAMPLE = "https://github.com/gHashTag/trinity/blob/main/docs/verification/SAMPLE-REPORT.md"

PAGES = {
    "gft": {
        "title": "GF-T — a ternary-native float with measured takum comparisons",
        "eyebrow": "The format",
        "h1": "GF-T — a float whose exponent is ternary.",
        "desc": (
            "GF-T puts the exponent of a float in balanced ternary and keeps the fields fixed: "
            "2.1x lower error in a 16-bit takum comparison and 2.6x in a 32-bit comparison, 219 LUTs and zero DSP blocks, "
            "147 MHz pipelined on an Artix-7. Reference model and bit-exact vectors included."
        ),
        "lede": (
            "The exponent is a balanced-ternary number and the fields are fixed. That removes the "
            "incumbent's largest cost \u2014 regime decode \u2014 and makes the exponent add native on a "
            "ternary fabric. Against takum, the measured comparisons show 2.1x lower error at 16 bits "
            "and 2.6x at 32 bits."
        ),
        "sections": [
            ("The layout", [
                ("GF-T16", "[ sign | E = 4 balanced-ternary trits | M = 9 mantissa bits ]. value = (-1)^sign x (1 + M/2^9) x 2^e, where e = the sum of t_i x 3^i, in the range -40 to +40."),
                ("Four trits, 81 exponent values", "Radix-3 economy: 3^4 = 81 exponent values from four trits, and on a ternary fabric the exponent add is native \u2014 no binary carry, no base conversion."),
            ]),
            ("Accuracy against takum", [
                ("16-bit comparison \u2014 2.1x lower error", "The measured comparison against a 16-bit takum format reports 2.1x lower error for GF-T."),
                ("32-bit comparison \u2014 2.6x lower error", "The measured comparison against a 32-bit takum format reports 2.6x lower error for GF-T."),
                ("Re-measured independently", "8 August 2026, against the published format's own oracle. The compared widths are stated with each result."),
                ("What this does not establish", "The comparisons do not establish a universal ranking: width and range are part of the stated test conditions."),
            ]),
            ("What it costs in hardware", [
                ("219 LUTs, zero DSP48", "The GF-T16 multiplier with the bus widths the arithmetic needs, synthesised for xc7 with hard multipliers disabled."),
                ("147.32 MHz pipelined", "Two stages, latency one cycle, one result per cycle. Post-route on an XC7A200T with nextpnr-xilinx. 81.35 MHz combinational."),
                ("The interface cost five times the arithmetic", "The original declares every port 32 bits wide, though nothing in GF-T16 is: synthesis built a 32x32 multiplier and charged 1,179 LUTs or three DSP blocks for it. Correcting the widths is bit-identical over 321,156 input combinations."),
            ]),
            ("Where it loses", [
                ("The range is bounded, and that is the trade", "GF-T16 reaches plus or minus 40 in powers of two, roughly plus or minus 12 decades. Fixed fields buy the cheap datapath and the uniform precision; range is the price, so comparisons name their width and range."),
                ("Measured on one device family", "Artix-7, on the open flow. Not multi-corner characterisation, and ASIC numbers will differ."),
                ("No takum RTL here", "The accuracy comparison uses the published format's own oracle. The cost figures are GF-T's own \u2014 writing a competitor's implementation and then reporting it as more expensive would prove nothing."),
            ]),
        ],
        "cta": "A licence includes the RTL, the independent reference model and the vectors that prove it \u2014 so you can check the claims rather than take them on trust.",
    },
    "verification": {
        "title": "Hardware-verified RTL — measured on binary FPGA",
        "eyebrow": "Verification service",
        "h1": "Not simulated. Measured on a binary FPGA.",
        "desc": (
            "Point it at a public repository and the checks run for free, with the report published. "
            "Nothing leaves your repo for the open-source tier. Private work is set up by hand: "
            "bit-exact conformance against an independent model, timing, resources and the bitstream, "
            "on a fully open-source flow. From $300 per core, an introductory module free."
        ),
        "lede": (
            "For a public repository you give a URL and nothing else — the checks run in the open and the "
            "report is published here whichever way it goes. For private work the run is arranged "
            "directly. Either way it comes back as a signed report: bit-exact conformance against an "
            "independent model, achieved timing, resources and the bitstream, on a fully open-source "
            "toolchain, so every number can be reproduced."
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
            # Filled from tiers.json at the entry point, below.
            ("Pricing", []),
            ("What this is not", [
                ("One device family", "Measurements come from a Xilinx Artix-7. This is not multi-corner characterisation and does not claim to be."),
                ("Not a sign-off flow", "It is an independent check, not a substitute for a full commercial sign-off."),
                ("No encrypted netlists", "I verify what I can read. Encrypted IP cannot be checked this way."),
                ("Estimates are labelled", "Anything estimated rather than measured says so, here and in every report."),
            ]),
        ],
        "cta": "Have a design to verify? An introductory module is free, so you can judge the report before paying for anything.",
    },
    "proof": {
        "title": "Every number here was measured",
        "eyebrow": "Measured evidence",
        "h1": "Every number here was measured.",
        "desc": (
            "Every hardware claim behind this site with the measurement that produced it — a GF16 matmul "
            "that needs no hard multipliers, a neural network training on-chip, a SKY130 design submitted for fabrication — and a "
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
                ("100% held-out — a network that trains on the FPGA", "Forward pass, gradient and weight update all in RTL with no host in the loop. A 2-layer ReLU network learns XOR on the chip itself, 4 of 4 correct, every node bit-exact from specification to the binary FPGA."),
                ("SKY130 — submitted for fabrication through Tiny Tapeout", "The design was submitted for fabrication through an open ASIC process: GDS was produced, the gate-level test passed, and precheck passed. No die measurements are claimed."),
                ("2.1× / 2.6× — measured GF-T and takum comparisons", "A float whose exponent is a balanced-ternary number and whose fields are fixed: no regime decode to pay for, and on a ternary fabric the exponent add is native. The measured comparisons report 2.1× lower error at 16 bits and 2.6× at 32 bits against takum. Range is bounded at ±40 in powers of two; that limit is stated with the comparison."),
                ("Over the air — tri-net, a full ternary network stack", "133 formal specifications: GF16 physical layer, BPSK modem on AD9361, ETX mesh routing, ChaCha20-Poly1305 / X25519 crypto. Text and images carried between physically separate boards."),
                ("83 formats — a conformance catalogue", "Bit-exact test vectors for FP8, BF16, MXFP4 and microscaling formats: a vendor-neutral reference for verifying low-precision arithmetic."),
            ]),
            ("How any of this is checked", [
                ("Independent model, not a mirror", "The reference model is written from the specification, never from the RTL."),
                ("Per-stage vectors", "Known-answer vectors at every pipeline stage, so a regression points at the stage that broke."),
                ("Hardware replay", "The same vectors run again on the physical board. Simulation agreement does not prove agreement on the binary FPGA."),
                ("Open toolchain", "Yosys, nextpnr-xilinx, prjxray, openFPGALoader, iverilog. No proprietary licence stands between a claim here and someone reproducing it."),
            ]),
            ("What these results are not", [
                ("Entries are entries", "A DARPA CLARA submission and an OpenAI Parameter Golf entry are submitted work, not awarded contracts or won prizes."),
                ("One device family", "Measurements come from a Xilinx Artix-7 and are not multi-corner characterisation."),
                ("Training is a primitive", "The on-chip training result is proven at small scale: a real network learning on a binary FPGA, not a production training accelerator."),
                ("Estimates are labelled", "Anything estimated rather than measured is labelled as estimated."),
                ("A figure withdrawn", "This page previously reported 323 MHz and 41.2 GOPS for the GF16 matmul. Re-checking the RTL on 8 August 2026 showed the block holds no registers, so it has no clock and no frequency can belong to it. Withdrawn rather than explained away."),
            ]),
        ],
        "cta": "The papers, the source and a full example report are all public. A claim you cannot verify is just a sentence.",
    },
    "ip": {
        "title": "Arithmetic cores measured on a binary FPGA",
        "eyebrow": "IP licensing",
        "h1": "Arithmetic cores measured on a binary FPGA.",
        "desc": (
            "License arithmetic cores measured on real hardware: the GF-T ternary multiplier, a GF16 4×4 "
            "matmul that maps into fabric with no hard multipliers, a BPSK modem proven over the air, and on-chip "
            "training primitives. RTL, reference model and the vectors that prove it."
        ),
        "lede": (
            "Every core here was designed, verified bit-exact against an independent model, and measured on "
            "the binary FPGA ALINX AX7203 (Xilinx Artix-7 XC7A200T); a SKY130 design was submitted for fabrication. You license the RTL, the reference model "
            "and the vectors that prove it, so you can check the claims instead of trusting them."
        ),
        "sections": [
            ("Available cores", [
                ("GF-T multiplier — ternary arithmetic", "The multiplier for GF-T: measured 2.1× lower error against 16-bit takum and 2.6× against 32-bit takum, with no regime decode. Published as arXiv:2606.05017 with an independent reference model and bit-exact vectors; ratios re-measured independently on 8 August 2026."),
                ("GF16 4×4 matmul — matrix engine", "Maps entirely into fabric, leaving the DSP columns free for the rest of your system: 32,252 LUTs with zero DSP48, or 21,223 LUTs if the 64 hard multipliers are allowed. Combinational, 0 latches."),
                ("BPSK modem — radio PHY", "Built for software-defined radio (AD9361), part of a full ternary network stack with mesh routing and authenticated encryption. Proven device-to-device over the air."),
                ("On-chip training primitives — edge ML", "Neural primitives that perform their own backward pass on the FPGA: forward, gradient and weight update in RTL, no host in the loop. 100% held-out on the binary FPGA."),
            ]),
            ("What a licence includes", [
                ("Readable RTL", "Synthesisable and readable, not obfuscated."),
                ("An independent reference model", "The thing that lets you prove the core is right rather than believe it."),
                ("Per-stage vectors", "Bit-exact test vectors per pipeline stage, so a regression tells you which stage broke."),
                ("A measured report", "Frequency, resources and a latch-free check on real hardware."),
                ("Integration help", "A core that does not land in your system is worth nothing."),
            ]),
            ("Terms", [
                ("Evaluation — from $500", "Source and vectors for a single project, so you can measure it in your own flow before deployment."),
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
            "a binary FPGA. Entirely open-source: no Vivado, no licences, no step you cannot reproduce."
        ),
        "lede": (
            "Not inference — training, on the chip itself. Eight modules from an empty toolchain to a network "
            "that learns on a binary FPGA, entirely on open tools: no Vivado, no licences, and no step you "
            "cannot reproduce yourself."
        ),
        "sections": [
            ("Eight modules", [
                ("01 · The open flow from nothing", "Yosys, nextpnr-xilinx, prjxray, openFPGALoader and iverilog installed and verified on macOS arm64 or Linux. A bitstream blinks an LED on a real board, no vendor licence anywhere in the chain."),
                ("02 · Exactly as much Verilog as you need", "Synchronous design, registers versus latches, and why an accidental latch is the classic bug that shows up on hardware."),
                ("03 · Arithmetic as the foundation of ML in hardware", "Why float is expensive, what quantisation really costs, and where ternary and low-precision formats come from."),
                ("04 · Bit-exact verification — the heart of the course", "An independent Python reference model, per-stage known-answer vectors, checked through iverilog. Why a testbench written from the design's own assumptions cheerfully agrees with its bugs."),
                ("05 · A matrix multiplier that closes timing", "MAC to array to pipeline. Reading the router's timing report and fighting for frequency on a real example — including why a hard multiplier in the path can leave you with no frequency report at all."),
                ("06 · Neural network inference on the FPGA", "Layers, activations, dataflow and on-chip memory, running on the board rather than in a simulator."),
                ("07 · On-chip training — the capstone", "Backward pass and SGD in RTL. The network learns XOR on the FPGA itself, 4 of 4, bit-exact against the reference. Almost nobody has done this by hand."),
                ("08 · From FPGA to an ASIC submission", "The Tiny Tapeout path: preparing a design, what changes between FPGA and ASIC, and where the open ASIC ecosystem stands after the move to IHP."),
            ]),
            ("How this differs from the free alternatives", [
                ("hls4ml (CERN) — free", "Inference is generated through HLS and the flow underneath is a vendor toolchain. It does not train on the chip or leave you able to read the RTL it produced."),
                ("Vendor courses (Intel, AMD) — free", "Built to teach you their tools on their hardware. Nothing transfers to a flow you can run without a licence."),
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
    "resources": {
        "title": "Papers, datasets and upstream patches",
        "eyebrow": "The record",
        "h1": "Everything citable, with its identifier.",
        "desc": (
            "Three arXiv papers, ten Zenodo records with DOIs, and the patches sent upstream to the "
            "open FPGA toolchain. The corpus is link-checked, dated, and lists its own known "
            "discrepancies rather than hiding them."
        ),
        "lede": (
            "One page holding everything that can be cited or checked: the preprints, the archived "
            "datasets and their DOIs, the patches sent to other people's projects, and the accounts "
            "that are actually mine. It exists so a reviewer does not have to take a claim on trust "
            "or reconstruct the trail from a CV."
        ),
        "sections": [
            ("What is on it", [
                ("Three arXiv preprints", "arXiv:2605.28405, arXiv:2606.05017 and arXiv:2606.09686. Listed with their identifiers, so the version you read is the version being referred to."),
                ("Ten Zenodo records, each with a DOI", "The GoldenFloat format description and the Trinity B001 to B007 collection, among others. A DOI resolves to a fixed deposit, which a repository link does not."),
                ("Six patches sent upstream", "Changes offered to openXC7 and nextpnr-xilinx, numbered #109 to #115, covering timing constraint parsing, clock buffer placement and IDDR initialisation. Their state is shown on the page as it stands, not as it was hoped."),
                ("Accounts and identities", "ORCID and the channels that are genuinely mine, so a name collision elsewhere does not get attributed here."),
            ]),
            ("Why it is arranged this way", [
                ("The corpus carries a date", "The links were checked on a stated date, which is shown on the page. A list of references with no check date says nothing about whether it still resolves."),
                ("Known discrepancies are counted, not hidden", "The page computes its own broken and contradictory entries and shows how many there are. A reference list that never admits a bad entry has simply never been checked."),
                ("Identifiers over links", "A DOI or an arXiv id survives a repository being renamed, moved or made private. Where one exists, it is what is given."),
            ]),
        ],
        "cta": (
            "Cite the DOI or the arXiv identifier rather than a repository URL \u2014 those survive a "
            "rename. If something here does not resolve for you, that is worth an email: the "
            "discrepancy list reflects the last recorded check."
        ),
    },
    "about": {
        "title": "Dmitrii Vasilev — hardware-AI and FPGA/RTL engineer",
        "eyebrow": "About",
        "h1": "From an arXiv paper to an ASIC submission.",
        "desc": (
            "Dmitrii Vasilev — hardware-AI and FPGA/RTL engineer. Designer of the GF-T ternary "
            "floating-point format, taken from an arXiv paper through RTL that needs no hard multipliers "
            "to a SKY130 submission for fabrication, entirely on open-source tools."
        ),
        "lede": (
            "I design number formats and RTL measured on a binary FPGA. GF-T started as a paper, became RTL "
            "that maps into Artix-7 fabric with no hard multipliers at all, and went through a SKY130 design submitted for fabrication — "
            "on a toolchain anyone can install for free. Before hardware I spent a decade building products "
            "and teaching: over a thousand developers, and a React Native course for the "
            "Russian-speaking internet."
        ),
        "sections": [
            ("What I do", [
                ("Custom arithmetic", "Number formats designed against your constraints — ternary, low-precision, φ-based — each with an independent reference model and bit-exact vectors, not just a claim."),
                ("RTL to binary FPGA", "Synthesisable Verilog through an open flow: Yosys, nextpnr-xilinx, prjxray, iverilog. Measured on the binary FPGA ALINX AX7203 (Xilinx Artix-7 XC7A200T); a SKY130 design was submitted for fabrication."),
                ("Verification", "Bit-exact conformance against models written from the specification rather than from the design — a check that can disagree with the RTL."),
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
            "surfaced, and the numbers measured on a live Artix-7. Empty until an introductory free run finishes."
        ),
        "lede": (
            "Every run ends in a report: what was checked, what it surfaced, and the numbers taken off the "
            "board. They are collected here, with the client's permission and without edits in my favour."
        ),
        # Filled from runs.json at import time, below. Left empty here so that a
        # missing data file is a hard failure rather than a page that quietly
        # reverts to claiming nothing has finished.
        "sections": [],
        "cta": "Need a run? Introductory runs are free and the report is yours to publish or keep.",
    },
}

NAV = [
    ("gft", "GF-T"),
    ("verification", "Verification"),
    ("proof", "Evidence"),
    ("ip", "Licensing"),
    ("course", "Course"),
    ("cases", "Case studies"),
    ("resources", "Resources"),
    ("about", "About"),
]

CSS = """*,*::before,*::after{box-sizing:border-box}
:root{--bg:#05070a;--card:#0b1014;--ink:#e9f1ee;--muted:#8fa79f;--accent:#00ff88;--rule:#1b2724}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--accent)}
/* Centred to match the app. These pages were left-aligned while every page in
   the SPA centres its content, so landing here from a link felt like a different
   site with everything shoved against the left edge. */
.wrap{max-width:820px;margin:0 auto;padding:28px 20px 72px;text-align:center}
header.top{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:center;padding-bottom:18px;border-bottom:1px solid var(--rule)}
.brand{font-weight:700;letter-spacing:.18em;font-size:12px;color:var(--accent);text-decoration:none}
/* Inline anchors wrap by word, which split "CASE STUDIES" across two lines and
   pushed "CASE" off the right edge at 375px. Flex with a gap wraps whole items. */
nav.top{display:flex;flex-wrap:wrap;gap:6px 14px;justify-content:center}
nav.top a{font-size:12px;text-transform:uppercase;letter-spacing:.08em;text-decoration:none;color:var(--muted);white-space:nowrap}
nav.top a:hover,nav.top a[aria-current]{color:var(--accent)}
.eyebrow{color:var(--accent);text-transform:uppercase;letter-spacing:.14em;font-size:12px;margin:38px 0 10px}
h1{font-size:clamp(1.9rem,5.5vw,2.7rem);line-height:1.15;margin:0 0 14px;text-wrap:balance}
.lede{font-size:1.08rem;color:var(--muted);margin:0 auto 26px;max-width:62ch}
h2{font-size:1.25rem;margin:40px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--rule);text-align:center}
.items{display:grid;gap:14px}
.item{background:var(--card);border:1px solid var(--rule);border-radius:14px;padding:16px 18px}
.item h3{font-size:1rem;margin:0 0 6px;color:var(--accent)}
.item p{margin:0;font-size:.95rem;color:#c6d5d0}
.cta{margin-top:42px;background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:24px}
.cta p{margin:0 0 16px;color:#c6d5d0}
.btn{display:inline-block;background:var(--accent);color:#04140d;font-weight:700;text-decoration:none;padding:12px 24px;border-radius:999px;font-size:.92rem}
.btn.sec{background:transparent;color:var(--ink);border:1px solid var(--rule);font-weight:500}
.btns{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--rule);color:var(--muted);font-size:.85rem}
footer a{color:var(--muted)}
@media(prefers-color-scheme:light){:root{--bg:#fbfdfc;--card:#fff;--ink:#101a17;--muted:#5b6f68;--accent:#0a7a4c;--rule:#dde7e3}.item p{color:#394944}.cta p{color:#394944}.btn{color:#fff}}
"""


# Russian copy lives in landing-ru.json rather than a second dict here, so the
# two cannot be edited past each other without the mismatch showing up as a
# structural difference the loader refuses.
RU_NAV = {
    "gft": "GF-T", "verification": "Верификация", "proof": "Доказательства",
    "ip": "Лицензии", "course": "Курс", "cases": "Кейсы",
    "resources": "Реестр", "about": "Обо мне",
}
RU_UI = {
    "run": "Запустить проверку своего репозитория",
    "sample": "Прочитать пример отчёта",
    "app": "Открыть интерактивную версию",
    "other": "Read in English",
}


def load_ru():
    """Russian copy, refused unless it matches the English structure exactly.

    A translation that silently loses a section ships a page that is half the
    length of its English twin and claims, via hreflang, to be the same document.
    Failing the build is the cheaper outcome.
    """
    import json
    if not os.path.exists("landing-ru.json"):
        return {}
    data = json.load(open("landing-ru.json", encoding="utf-8"))
    data.pop("_comment", None)
    if "cases" in data:
        data["cases"]["sections"] = cases_sections("ru")
        data["cases"].update(_cases_copy("ru"))
    if "verification" in data:
        secs = data["verification"]["sections"]
        for k, sec in enumerate(secs):
            if sec[0] in ("Цены", "Pricing"):
                secs[k] = list(pricing_section("ru"))
        data["verification"].update(verification_copy("ru"))
    for slug, ru in data.items():
        en = PAGES.get(slug)
        if en is None:
            raise SystemExit(f"landing-ru.json: '{slug}' has no English page")
        for k in ("title", "eyebrow", "h1", "desc", "lede", "cta"):
            if not ru.get(k):
                raise SystemExit(f"landing-ru.json: {slug} is missing '{k}'")
        if len(ru["sections"]) != len(en["sections"]):
            raise SystemExit(
                f"landing-ru.json: {slug} has {len(ru['sections'])} sections, "
                f"English has {len(en['sections'])}"
            )
        for i, (rs, es) in enumerate(zip(ru["sections"], en["sections"])):
            if len(rs[1]) != len(es[1]):
                raise SystemExit(
                    f"landing-ru.json: {slug} section {i} has {len(rs[1])} items, "
                    f"English has {len(es[1])}"
                )
    return data


# ---------------------------------------------------------------------------
# The case-studies page said "Empty for now, and honestly so — nothing has
# finished yet" while runs.json held ten finished runs, five of them on other
# people's designs. The claim had been true when it was written; the SPA was
# repaired and this generator was not, so the static page — the one a crawler
# and a link preview see — went on telling visitors there was nothing here.
#
# It is generated from the data now, so it cannot disagree with it again.
# ---------------------------------------------------------------------------

def _runs():
    import json
    if not os.path.exists("runs.json"):
        raise SystemExit("runs.json is missing; /cases/ cannot be generated from data")
    d = json.load(open("runs.json", encoding="utf-8"))
    # The file is {"provenance": {...}, "runs": [...]}; taking every value of the
    # top-level dict picks up provenance as if it were a run.
    if isinstance(d, list):
        runs = d
    elif isinstance(d.get("runs"), list):
        runs = d["runs"]
    else:
        raise SystemExit("runs.json has no 'runs' list")
    if not runs:
        raise SystemExit("runs.json parsed to zero runs")
    return runs


def cases_sections(lang="en"):
    """One section per run: the design, then every check with its command."""
    ru = lang == "ru"
    out = []
    for r in _runs():
        third = r.get("thirdParty")
        if ru:
            tag = "чужой дизайн" if third else "свой дизайн"
            head = f'{r["design"]} — {r["repo"]} ({tag})'
        else:
            tag = "third-party" if third else "my own"
            head = f'{r["design"]} — {r["repo"]} ({tag})'
        items = []
        what = (r.get("whatRu") if ru else None) or r.get("what", "")
        items.append(("Что это" if ru else "What it is",
                      f'{what} Top: {r.get("top","?")}. Tiles: {r.get("tiles","?")}. '
                      + (f'Прогон от {r.get("date","")}.' if ru else f'Run of {r.get("date","")}.')))
        for c in r.get("checks", []):
            detail = (c.get("detailRu") if ru else None) or c.get("detail", "")
            cmd = c.get("command", "")
            text = detail + ((("  Команда: " if ru else "  Command: ") + cmd) if cmd else "")
            items.append((f'{c.get("status","?")} · {c.get("name","?")}', text))
        out.append((head, items))
    return out


def _provenance_line(lang="en"):
    """The tools that produced these numbers, named. A cell count without its
    yosys version is not reproducible, and this page tells the reader to
    re-run the commands."""
    import json
    d = json.load(open("runs.json", encoding="utf-8"))
    pv = d.get("provenance", {}) if isinstance(d, dict) else {}
    if not pv:
        return ""
    bits = " · ".join(x for x in (pv.get("yosys"), pv.get("iverilog")) if x)
    if not bits:
        return ""
    # The offered workflow pins a different yosys than the one these runs were
    # measured with. Both facts are true and the difference is real — about 9%
    # on cell count, with wires and flip-flops stable — so it is stated rather
    # than left for a reader to discover by re-running and disagreeing.
    # Was a hard-coded "Yosys 0.68+71", written after observing the pinned
    # workflow once. Two runs of that same pin then reported 0.68+71 and
    # 0.68+80 — so `osscadsuite-version: '2026-08-12'` fixes the suite release
    # and NOT the yosys build inside it. Stating a single build number here
    # claimed a reproducibility the pin does not deliver, on the page that
    # promises exactly that. What is true is the weaker sentence.
    pinned = ("a pinned oss-cad-suite release (2026-08-12), whose yosys build has "
              "been observed to vary — 0.68+71 and 0.68+80 on two runs of the same pin")
    if lang == "ru":
        return (f" Прогоны выполнены {pv.get('ranAt','')} на: {bits}."
                f" Предлагаемый воркфлоу закреплён на другой версии — {pinned};"
                " повтор даст другое число ячеек и те же провода и триггеры.")
    return (f" Produced on {pv.get('ranAt','')} with: {bits}."
            f" The workflow offered on this site pins a different build — {pinned} —"
            " so a re-run differs on cell count and agrees on wires and flip-flops.")


def _cases_copy(lang="en"):
    runs = _runs()
    n = len(runs)
    third = sum(1 for r in runs if r.get("thirdParty"))
    if lang == "ru":
        return {
            "desc": (f"Что показали проверки чужого RTL: {n} прогонов, из них {third} на чужих дизайнах. "
                     "Под каждой строкой — команда, которой она получена."),
            "lede": (f"Здесь {n} завершённых прогонов, {third} из них на дизайнах других людей. "
                     "Каждая проверка приведена вместе с командой, чтобы её можно было повторить, "
                     "и вместе с тем, чего она не устанавливает." + _provenance_line("ru")),
            "cta": "Нужен прогон? Первый бесплатен, отчёт ваш — публикуйте или оставьте себе.",
        }
    return {
        "desc": (f"What each verification run turned out to be: {n} runs, {third} of them on other "
                 "people's designs, each line with the command that produced it."),
        "lede": (f"{n} finished runs, {third} of them on designs that are not mine. Every check is "
                 "shown with the command that produced it, and with what it does not establish."
                 + _provenance_line("en")),
        "cta": "Need a run? Introductory runs are free and the report is yours to publish or keep.",
    }


# ---------------------------------------------------------------------------
# /verification/ used to carry a hand-written price list — $300 / $800 / $2 000
# / $1-3k per month — while DELIVERY_TIERS, which the app reads, said "Free",
# "From $2 500 per core" and "Quoted per design". Eight-fold on one line item,
# and each page linked to the other. The static one is what carries the
# canonical link and what search indexes.
#
# The same page's lede promised the free public run returns "bit-exact
# conformance ... achieved timing, resources and the bitstream" — the exact
# conflation verificationTiers.ts was written to remove. Both come from the
# data now.
# ---------------------------------------------------------------------------

def _tiers():
    import json
    if not os.path.exists("tiers.json"):
        raise SystemExit("tiers.json is missing; /verification/ cannot be generated from data")
    d = json.load(open("tiers.json", encoding="utf-8"))
    t = d.get("tiers") or []
    if len(t) < 3:
        raise SystemExit(f"tiers.json parsed to {len(t)} tiers; expected at least 3")
    return d


def pricing_section(lang="en"):
    ru = lang == "ru"
    d = _tiers()
    items = []
    for t in d["tiers"]:
        name = t["name"]["ru" if ru else "en"]
        price = t["price"]["ru" if ru else "en"]
        turn = t["turnaround"]["ru" if ru else "en"]
        first = (t["delivers"]["ru" if ru else "en"] or [""])[0]
        lead = "Срок: " if ru else "Turnaround: "
        items.append((f"{name} — {price}", f"{lead}{turn}. {first}"))
    return ("Цены" if ru else "Pricing", items)


def verification_copy(lang="en"):
    d = _tiers()
    lede = d.get("lede", {}).get("ru" if lang == "ru" else "en", "")
    free = d["tiers"][0]["price"]["ru" if lang == "ru" else "en"]
    if lang == "ru":
        return {
            "desc": ("Наведите на публичный репозиторий — структурная проверка идёт бесплатно, "
                     "отчёт публикуется. " + free + ". Соответствие независимой модели и работа "
                     "на плате — отдельные ступени, с отдельной ценой."),
            "lede": lede,
        }
    return {
        "desc": ("Point it at a public repository and the structural check runs for free, with the "
                 "report published. " + free + ". Conformance against an independent model and "
                 "work on the board are separate tiers, priced separately."),
        "lede": lede,
    }


def render(slug, p, lang="en"):
    ru = lang == "ru"
    prefix = "/ru" if ru else ""
    url = f"{SITE}{prefix}/{slug}/"
    run_btn = (
        f'<a class="btn" href="{REQUEST_URL}">{RU_UI["run"] if ru else "Start a run on your repo"}</a>\n    '
        if slug in RUNNABLE else ""
    )
    nav = "".join(
        f'<a href="{prefix}/{s}/"{" aria-current=\"page\"" if s == slug else ""}>'
        f'{html.escape(RU_NAV.get(s, label) if ru else label)}</a>'
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

    # Each language is canonical for itself and both name each other, or a search
    # engine files one as a duplicate of the other and the translation earns
    # nothing.
    alt = (
        f'\n<link rel="alternate" hreflang="en" href="{SITE}/{slug}/" />'
        f'\n<link rel="alternate" hreflang="ru" href="{SITE}/ru/{slug}/" />'
        f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/{slug}/" />'
    )
    og = f"og-{slug}-ru.png" if ru else f"og-{slug}.png"
    return f"""<!doctype html>
<html lang="{'ru' if ru else 'en'}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(p['title'])} · TRINITY</title>
<meta name="description" content="{html.escape(p['desc'])}" />
<link rel="canonical" href="{url}" />{alt}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="TRINITY" />
<meta property="og:locale" content="{'ru_RU' if ru else 'en_US'}" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{html.escape(p['title'])}" />
<meta property="og:description" content="{html.escape(p['desc'])}" />
<meta property="og:image" content="{SITE}/{og}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{html.escape(p['title'])}" />
<meta name="twitter:description" content="{html.escape(p['desc'])}" />
<link rel="icon" href="/favicon.svg" />
{landing_ld(slug, p, "ru" if ru else "en") if slug else ""}
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
    {run_btn}<a class="btn sec" href="mailto:{EMAIL}?subject={html.escape(p['title'])}">{EMAIL}</a>
    <a class="btn sec" href="{SAMPLE}">{RU_UI["sample"] if ru else "Read a sample report"}</a>
    <a class="btn sec" href="{'/?lang=ru#/' if ru else '/#/'}{slug}">{RU_UI["app"] if ru else "Open the interactive site"}</a>
    <a class="btn sec" href="{('/' + slug + '/') if ru else ('/ru/' + slug + '/')}" hreflang="{'en' if ru else 'ru'}" lang="{'en' if ru else 'ru'}">{RU_UI["other"] if ru else "Читать по-русски"}</a>
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


def result_slugs():
    """Per-design result pages, read off disk so the sitemap cannot drift."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r")
    if not os.path.isdir(root):
        return []
    out = []
    for dirpath, _dirs, files in os.walk(root):
        if "index.html" in files:
            out.append(os.path.relpath(dirpath, root).replace(os.sep, "/"))
    return sorted(out)


def doc_pages():
    """The GOLDEN SUNFLOWERS chapters served under /docs/.

    Forty-eight substantive pages that were in no sitemap at all — the book is
    linked from the landings, so a crawler could reach it, but nothing told one
    that it exists or how large it is. Listed with the .html extension because
    that is the form the book's own internal links use; both forms resolve, and
    publishing the other one would only invent a second URL for every chapter.
    """
    if not os.path.isdir("docs"):
        return []
    # print.html is the whole book on one page (9,065 words against ~430 in a
    # chapter). Listing it beside the chapters is duplicate content that competes
    # with them for the same queries, so it stays out.
    skip = {"404.html", "print.html"}
    names = sorted(
        f for f in os.listdir("docs")
        if f.endswith(".html") and f not in skip
    )
    if not names:
        raise SystemExit("sitemap: docs/ exists but holds no pages — check the path")
    return [f"docs/{f}" for f in names]


def blog_pages():
    """The static blog pages written by build-blog.py.

    The blog was in no sitemap at all and `/blog` answered 404 with the SPA
    shim, so the articles — one of them carrying the scale-field result — were
    invisible to any crawler that does not run JavaScript. Read off disk for the
    same reason the result pages are: a hand-kept list drifts from what exists.
    """
    out = []
    # English at blog/, Russian at ru/blog/. Both are listed: they are separate
    # URLs with reciprocal hreflang, not duplicates of one another.
    for root in ("blog", "ru/blog"):
        if not os.path.isdir(root):
            continue
        found = [
            f"{root}/{name}/"
            for name in sorted(os.listdir(root))
            if os.path.isfile(os.path.join(root, name, "index.html"))
        ]
        if not found:
            raise SystemExit(f"sitemap: {root}/ exists but holds no posts — run build-blog.py")
        out += [f"{root}/"] + found
    if not out:
        return []
    return out


# The Russian entry point. Without it /ru/ answered 404, so a reader who trimmed
# /ru/gft/ back to its parent hit an error page, and the English homepage — which
# is the SPA and renders its first screen in English — was the only front door.
RU_HOME = {
    "title": "T27.AI — тернарное железо для ИИ, измеренное на бинарной FPGA",
    "eyebrow": "Тернарное железо для ИИ",
    "h1": "Числовые форматы и бинарная FPGA, которая их исполняет.",
    "desc": "GF-T — тернарно-нативный float: в измеренных сравнениях с takum точнее в 2.1 раза при 16 битах и в 2.6 раза при 32 битах. "
            "Результаты указаны вместе с разрядностью и диапазоном. "
            "RTL, независимая эталонная модель и побитовые векторы — на открытом тулчейне.",
    "lede": "Я проектирую числовые форматы и железо, которое их считает: от статьи на arXiv через RTL, "
            "укладывающийся в логику Artix-7 без единого аппаратного умножителя, до отправки дизайна на изготовление через SKY130 — "
            "целиком на инструментах, которые любой поставит бесплатно. Каждая цифра ниже измерена, и рядом "
            "с ней названо, чего она не доказывает.",
    "cta": "Вводный модуль верификации бесплатный, и отчёт ваш — публикуйте или оставьте себе.",
    "sections": [
        ["Что здесь измерено", [
            ["Сравнения GF-T и takum — 2.1× и 2.6×",
             "Float, у которого экспонента — сбалансированное троичное число, а поля фиксированы: платить за "
             "декодирование режима не нужно. Измеренные сравнения дают в 2.1 раза меньшую ошибку при 16 битах "
             "и в 2.6 раза при 32 битах; ширина и диапазон названы рядом с каждым результатом."],
            ["Условия измерений",
             "Сравнения не задают общий рейтинг форматов: разрядность и диапазон входят в условия каждого результата."],
            ["Обучение на бинарной FPGA",
             "Прямой проход, градиент и обновление весов в RTL, без хоста в контуре: сеть учит XOR на FPGA, 4 из 4, "
             "побитово от спецификации до бинарной FPGA."],
            ["SKY130: отправлен на изготовление",
             "Тот же исходник, что работает на плате, прошёл открытый ASIC-процесс: GDS получен, тест на уровне "
             "вентилей и precheck пройдены."],
        ]],
        ["Где мы проигрываем — и это тоже здесь", [
            ["Элементная ось блочного формата",
             "У блочного формата масштаб и элементная часть имеют разные ограничения. Результаты для GF-T "
             "не переносятся на общий рейтинг форматов."],
            ["Диапазон GF-T ограничен",
             "±40 в степенях двойки, примерно ±12 декад. Фиксированные поля покупают дешёвый тракт и равномерную "
             "точность ценой диапазона; это ограничение указано рядом со сравнением."],
            ["Одно семейство устройств",
             "Замеры сняты на Xilinx Artix-7 на открытом флоу. Это не многоугловая характеризация, и для ASIC "
             "числа будут другими."],
        ]],
        ["С чего начать", [
            ["Доказательства", "Каждая цифра сайта с замером, который её породил, — и отдельно то, чем результаты не являются."],
            ["Верификация", "Побитовая сверка вашего RTL с независимой моделью, тайминг и ресурсы на живой плате. Первый модуль бесплатно."],
            ["Формат GF-T", "Раскладка полей, точность против takum, стоимость в железе и честный список того, где он проигрывает."],
            ["Блог", "Статьи выходят здесь раньше, чем где-либо ещё, с пруфами и открытыми вопросами."],
        ]],
    ],
}


def render_ru_home():
    """The Russian front door, built from the same renderer as the landings."""
    p = dict(RU_HOME)
    html_out = render("", p, "ru")
    # render() builds every path as <prefix>/<slug>/, and an empty slug leaves
    # doubled slashes: a canonical of /ru//, an og image of og--ru.png, and a
    # link of href="//" — which a browser reads as protocol-relative and sends to
    # a different host entirely. Repaired here rather than by threading a special
    # case through render(), and asserted below so a silent one cannot survive.
    out = (html_out
           .replace(f"{SITE}/ru//", f"{SITE}/ru/")
           .replace(f"{SITE}//", f"{SITE}/")
           .replace(f"{SITE}/og--ru.png", f"{SITE}/og-home-ru.png")
           .replace('href="/#/"', 'href="/"')
           .replace('href="/?lang=ru#/"', 'href="/?lang=ru"')
           .replace('href="//"', 'href="/"')
           .replace('href="/ru//"', 'href="/ru/"'))
    for bad in ('href="//"', "/ru//", "og--ru", f"{SITE}//"):
        if bad in out:
            raise SystemExit(f"render_ru_home: {bad!r} survived the empty-slug repair")
    # The Russian home has an empty slug, so the landing_ld() call inside render()
    # skipped it and it was the one page left without structured data.
    import json as _json
    ld = ('<script type="application/ld+json">' + _json.dumps({
        "@context": "https://schema.org", "@type": "WebPage",
        "name": RU_HOME["title"], "description": RU_HOME["desc"],
        "url": f"{SITE}/ru/", "inLanguage": "ru",
        "isPartOf": {"@type": "WebSite", "name": "TRINITY", "url": f"{SITE}/"},
    }, ensure_ascii=False, separators=(",", ":")) + "</script>")
    out = out.replace('<link rel="icon" href="/favicon.svg" />',
                      '<link rel="icon" href="/favicon.svg" />\n' + ld, 1)
    if "application/ld+json" not in out:
        raise SystemExit("render_ru_home: the JSON-LD anchor was not found")
    return out


def landing_ld(slug, p, lang):
    """Structured data for a landing.

    The homepage carried structured data. Deliberately modest: `WebPage` for everything
    and `Person` for the about page, carrying facts already written on the
    page itself. Prices are NOT emitted as `offers` — the pages say "from $500"
    and "quoted per case", and turning that into a machine-readable commitment
    would state something firmer than the page does.
    """
    import json as _json
    prefix = "/ru" if lang == "ru" else ""
    url = f"{SITE}{prefix}/{slug}/"
    doc = {
        "@context": "https://schema.org",
        "@type": "ProfilePage" if slug == "about" else "WebPage",
        "name": p["title"],
        "description": p["desc"],
        "url": url,
        "inLanguage": "ru" if lang == "ru" else "en",
        "isPartOf": {"@type": "WebSite", "name": "TRINITY", "url": f"{SITE}/"},
    }
    if slug == "about":
        doc["mainEntity"] = {
            "@type": "Person",
            "name": "Dmitrii Vasilev",
            "jobTitle": "Hardware-AI and FPGA/RTL engineer",
            "url": f"{SITE}/about/",
            # sameAs asserts identity, so every entry has to resolve. An arXiv
            # author page was drafted here and removed: arxiv.org/a/vasilev_d_1
            # returns 404, and claiming an identity URL that does not exist is
            # worse than listing one profile fewer.
            "sameAs": [
                "https://github.com/gHashTag",
                "https://linkedin.com/in/neurocoder",
            ],
        }
    return ('<script type="application/ld+json">'
            + _json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def _lastmod(path):
    """The date a page's content last actually changed, from git.

    A sitemap without lastmod tells a crawler nothing about what is worth
    re-reading, and 82 URLs here had none. But a fabricated date is worse than
    none: it teaches a crawler to ignore the field. So this reads the last commit
    that touched the file, and if the working tree differs from that commit —
    i.e. the page has just been regenerated with new content — it uses today,
    because that is when the content changed.

    Pages the generator rewrites byte-identically produce no diff and keep their
    real date, which is the behaviour that makes the field worth having.
    """
    import subprocess
    f = path if path else "index.html"
    f = f if os.path.isfile(f) else os.path.join(path, "index.html")
    if not os.path.isfile(f):
        return None
    # An untracked file is not "dirty" to git diff -- it is invisible to it --
    # so a brand new page fell through to git log, found no commit, and got no
    # lastmod at all. A page that has never been committed is new content by
    # definition, which is exactly the case the field exists to announce.
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", f],
                             capture_output=True).returncode == 0
    dirty = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", f],
                           capture_output=True).returncode
    if not tracked or dirty:
        import datetime
        return datetime.date.today().isoformat()
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f],
                       capture_output=True, text=True)
    d = r.stdout.strip()
    return d or None


def sitemap(slugs):
    # /status/ and the per-design result pages are generated by build-results.py,
    # so they are listed here rather than derived from PAGES.
    extra = ["status/"] + [f"r/{s}/" for s in result_slugs()]
    # Russian landings are separate URLs with reciprocal hreflang, so they are
    # listed rather than folded into their English twins.
    extra += ["ru/"] + [f"ru/{s}/" for s in sorted(load_ru())]
    paths = [""] + [f"{x}/" for x in slugs] + extra + blog_pages() + doc_pages()
    out = []
    for s in paths:
        lm = _lastmod(s)
        tail = f"<lastmod>{lm}</lastmod>" if lm else ""
        out.append(f"\n  <url><loc>{SITE}/{s}</loc>{tail}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(out) + "\n</urlset>\n")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    # Built from runs.json so the page cannot disagree with the data again.
    # The Russian side is filled inside load_ru(), after that file is read.
    PAGES["cases"]["sections"] = cases_sections("en")
    PAGES["cases"].update(_cases_copy("en"))

    # /verification/ carried a hand-written price list that disagreed with the
    # data by 8x on one line item. Emitted from tiers.json now.
    for k, sec in enumerate(PAGES["verification"]["sections"]):
        if sec[0] == "Pricing":
            PAGES["verification"]["sections"][k] = pricing_section("en")
    PAGES["verification"].update(verification_copy("en"))

    # A price on the page that is not in the data is the defect this replaces,
    # so it is checked rather than trusted. Any $-amount in the rendered
    # English copy must appear verbatim in tiers.json.
    import re as _re
    _t = _tiers()
    _known = " ".join(
        t["price"]["en"] + " " + t["price"]["ru"] for t in _t["tiers"]
    )
    _page = " ".join(
        [PAGES["verification"]["desc"], PAGES["verification"]["lede"]]
        + [a + " " + b for _h, _items in PAGES["verification"]["sections"] for a, b in _items]
    )
    for _amt in _re.findall(r"\$\s?[0-9][0-9  ,]*", _page):
        if _amt.strip() not in _known:
            raise SystemExit(
                f"verification: the page quotes {_amt.strip()!r}, which is not in tiers.json"
            )

    # A page that claims emptiness while the data holds runs is the defect this
    # replaces, so it is checked rather than trusted: one section per run, and
    # no section may say the page is empty.
    _n = len(_runs())
    if len(PAGES["cases"]["sections"]) != _n:
        raise SystemExit(f"cases: {len(PAGES['cases']['sections'])} sections for {_n} runs")
    _flat = " ".join(h + " " + " ".join(a + " " + b for a, b in items)
                     for h, items in PAGES["cases"]["sections"])
    for _bad in ("Nothing has finished", "Empty for now", "nothing here"):
        if _bad.lower() in _flat.lower():
            raise SystemExit(f"cases: the page still says {_bad!r} while runs.json holds {_n} runs")
    for slug, p in PAGES.items():
        os.makedirs(slug, exist_ok=True)
        with open(f"{slug}/index.html", "w", encoding="utf-8") as fh:
            fh.write(render(slug, p))
        print(f"wrote {slug}/index.html")
    for slug, p in load_ru().items():
        os.makedirs(f"ru/{slug}", exist_ok=True)
        with open(f"ru/{slug}/index.html", "w", encoding="utf-8") as fh:
            fh.write(render(slug, p, "ru"))
        print(f"wrote ru/{slug}/index.html")
    os.makedirs("ru", exist_ok=True)
    with open("ru/index.html", "w", encoding="utf-8") as fh:
        fh.write(render_ru_home())
    print("wrote ru/index.html")
    with open("sitemap.xml", "w", encoding="utf-8") as fh:
        fh.write(sitemap(list(PAGES)))
    with open("robots.txt", "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("wrote sitemap.xml, robots.txt")
