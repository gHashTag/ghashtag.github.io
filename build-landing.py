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
# the only way to start anything from them was to compose an email — the run
# has an entry point that needs no inbox, so it belongs on the page that gets
# found. Only the pages where a run is the next step get the button.
REQUEST_URL = "https://github.com/gHashTag/trinity/issues/new?template=verification-request.yml"
RUNNABLE = {"verification", "cases"}
EMAIL = "admin@t27.ai"
SAMPLE = "https://github.com/gHashTag/trinity/blob/main/docs/verification/SAMPLE-REPORT.md"

PAGES = {
    "gft": {
        "title": "GF-T — a ternary-native float that beats tekum16",
        "eyebrow": "The format",
        "h1": "GF-T — a float whose exponent is ternary.",
        "desc": (
            "GF-T puts the exponent of a float in balanced ternary and keeps the fields fixed: "
            "2.84x and 5.53x more accurate than tekum16 at range, 219 LUTs and zero DSP blocks, "
            "147 MHz pipelined on an Artix-7. Reference model and bit-exact vectors included."
        ),
        "lede": (
            "The exponent is a balanced-ternary number and the fields are fixed. That removes the "
            "incumbent's largest cost \u2014 regime decode \u2014 and makes the exponent add native on a "
            "ternary fabric. Against tekum16: a tie near unity, 2.84x more accurate at mid range and "
            "5.53x at far range."
        ),
        "sections": [
            ("The layout", [
                ("GF-T16", "[ sign | E = 4 balanced-ternary trits | M = 9 mantissa bits ]. value = (-1)^sign x (1 + M/2^9) x 2^e, where e = the sum of t_i x 3^i, in the range -40 to +40."),
                ("Four trits, 81 exponent values", "Radix-3 economy: 3^4 = 81 exponent values from four trits, and on a ternary fabric the exponent add is native \u2014 no binary carry, no base conversion."),
            ]),
            ("Accuracy against tekum16", [
                ("|e| < 8 \u2014 a tie", "GF-T16 3.56e-4 against tekum16 3.27e-4. Mean relative error over an encode-decode round trip, 6000 values, random sign."),
                ("|e| 8 to 20 \u2014 2.84x better", "GF-T16 3.52e-4 against tekum16 1.00e-3."),
                ("|e| 20 to 38 \u2014 5.53x better", "GF-T16 3.53e-4 against tekum16 1.95e-3. Nine mantissa bits at every magnitude, where tekum16 tapers to about four."),
                ("Re-measured independently", "8 August 2026, against the published format's own oracle. The ratios reproduce exactly. Bins are in powers of two, not decades."),
            ]),
            ("What it costs in hardware", [
                ("219 LUTs, zero DSP48", "The GF-T16 multiplier with the bus widths the arithmetic needs, synthesised for xc7 with hard multipliers disabled."),
                ("147.32 MHz pipelined", "Two stages, latency one cycle, one result per cycle. Post-route on an XC7A200T with nextpnr-xilinx. 81.35 MHz combinational."),
                ("The interface cost five times the arithmetic", "The original declares every port 32 bits wide, though nothing in GF-T16 is: synthesis built a 32x32 multiplier and charged 1,179 LUTs or three DSP blocks for it. Correcting the widths is bit-identical over 321,156 input combinations."),
            ]),
            ("Where it loses", [
                ("The range is bounded, and that is the trade", "GF-T16 reaches plus or minus 40 in powers of two, roughly plus or minus 12 decades. tekum16's regime is unbounded, so beyond that GF-T16 overflows and tekum16 keeps working. Fixed fields buy the cheap datapath and the uniform precision; range is the price."),
                ("Measured on one device family", "Artix-7, on the open flow. Not multi-corner characterisation, and ASIC numbers will differ."),
                ("No tekum16 RTL here", "The accuracy comparison uses the published format's own oracle. The cost figures are GF-T's own \u2014 writing a competitor's implementation and then reporting it as more expensive would prove nothing."),
            ]),
        ],
        "cta": "A licence includes the RTL, the independent reference model and the vectors that prove it \u2014 so you can check the claims rather than take them on trust.",
    },
    "verification": {
        "title": "Hardware-verified RTL — measured on live silicon",
        "eyebrow": "Verification service",
        "h1": "Not simulated. Measured on live silicon.",
        "desc": (
            "Point it at a public repository and the checks run for free, with the report published. "
            "Nothing leaves your repo for the open-source tier. Private work is set up by hand: "
            "bit-exact conformance against an independent model, timing, resources and the bitstream, "
            "on a fully open-source flow. From $300 per core, first module free."
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
                ("2.84× / 5.53× — GF-T beats tekum16", "A float whose exponent is a balanced-ternary number and whose fields are fixed: no regime decode to pay for, and on a ternary fabric the exponent add is native. Against tekum16, whose stated advantage is exactly that fabric — a tie near unity, 2.84× lower error at |e| 8–20, 5.53× lower at |e| 20–38, with a uniform 9-bit mantissa where tekum16 tapers to four. Range is bounded at ±40 in powers of two where tekum16's regime is not; that is the trade."),
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
                ("GF-T multiplier — ternary arithmetic", "The multiplier for GF-T: 2.84× and 5.53× lower error than tekum16 at mid and far range, a tie near unity, no regime decode. Published as arXiv:2606.05017 with an independent reference model and bit-exact vectors; ratios re-measured independently on 8 August 2026."),
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
            "discrepancy list is only as good as the last time someone looked."
        ),
    },
    "about": {
        "title": "Dmitrii Vasilev — hardware-AI and FPGA/RTL engineer",
        "eyebrow": "About",
        "h1": "From an arXiv paper to a tape-out.",
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
    "title": "T27.AI — тернарное железо для ИИ, измеренное на кремнии",
    "eyebrow": "Тернарное железо для ИИ",
    "h1": "Числовые форматы и кремний, который их исполняет.",
    "desc": "GF-T — тернарно-нативный float, в 2.84 и 5.53 раза точнее tekum16 на краях диапазона. "
            "Четырёхбитная геометрическая сетка масштаба строго доминирует восьмибитную E8M0 у MXFP4. "
            "RTL, независимая эталонная модель и побитовые векторы — на открытом тулчейне.",
    "lede": "Я проектирую числовые форматы и железо, которое их считает: от статьи на arXiv через RTL, "
            "укладывающийся в логику Artix-7 без единого аппаратного умножителя, до тейпаута на SKY130 — "
            "целиком на инструментах, которые любой поставит бесплатно. Каждая цифра ниже измерена, и рядом "
            "с ней названо, чего она не доказывает.",
    "cta": "Первый модуль верификации бесплатный, и отчёт ваш — публикуйте или оставьте себе.",
    "sections": [
        ["Что здесь измерено", [
            ["GF-T обходит tekum16 — 2.84× и 5.53×",
             "Float, у которого экспонента — сбалансированное троичное число, а поля фиксированы: платить за "
             "декодирование режима не нужно. Ничья у единицы, в 2.84 раза точнее при |e| 8–20 и в 5.53 раза "
             "при |e| 20–38. Перемерено независимо 8 августа 2026."],
            ["Масштаб: строгое доминирование над MXFP4",
             "Геометрическая сетка из степеней φ шириной четыре бита против восьмибитной E8M0: 4.125 бита на вес "
             "против 4.250 и перплексия лучше на обеих моделях — 21.3545 против 22.4998 и 14.8512 против 14.9447. "
             "Дешевле и точнее одновременно."],
            ["Обучение на самом кристалле",
             "Прямой проход, градиент и обновление весов в RTL, без хоста в контуре: сеть учит XOR на FPGA, 4 из 4, "
             "побитово от спецификации до кремния."],
            ["Тейпаут на SKY130",
             "Тот же исходник, что работает на плате, прошёл открытый ASIC-процесс: GDS получен, тест на уровне "
             "вентилей и precheck пройдены."],
        ]],
        ["Где мы проигрываем — и это тоже здесь", [
            ["Элементная ось блочного формата",
             "У блочного формата два поля. Масштаб мы выигрываем, элемент — нет: при 4 битах MXFP4 даёт 21.9397 "
             "против 36.7214 у нашего TNF4. Три захода провалились, граница Ллойда–Макса говорит, что четвёртый "
             "не оправдан."],
            ["Диапазон GF-T ограничен",
             "±40 в степенях двойки, примерно ±12 декад. У режима tekum16 предела нет — дальше он работает, а GF-T "
             "переполняется. Фиксированные поля покупают дешёвый тракт; диапазон — цена."],
            ["Одно семейство устройств",
             "Замеры сняты на Xilinx Artix-7 на открытом флоу. Это не многоугловая характеризация, и для ASIC "
             "числа будут другими."],
        ]],
        ["С чего начать", [
            ["Доказательства", "Каждая цифра сайта с замером, который её породил, — и отдельно то, чем результаты не являются."],
            ["Верификация", "Побитовая сверка вашего RTL с независимой моделью, тайминг и ресурсы на живой плате. Первый модуль бесплатно."],
            ["Формат GF-T", "Раскладка полей, точность против tekum16, стоимость в железе и честный список того, где он проигрывает."],
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

    Only the homepage carried any. Deliberately modest: `WebPage` for everything
    and `Person` for the about page, carrying only facts already written on the
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
