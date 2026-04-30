"""Pull all chapters from Neon → docs-src/src/*.md + SUMMARY.md."""
import psycopg2, os, re
URI = "postgresql://neondb_owner:npg_NHBC5hdbM0Kx@ep-curly-math-ao51pquy-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
ROOT = "/home/user/workspace/coq-census/repos/ghashtag.github.io/docs-src/src"
os.makedirs(ROOT, exist_ok=True)

def slug(ch_num):
    return ch_num.lower().replace('.','-')

conn = psycopg2.connect(URI); conn.autocommit = True
cur = conn.cursor()
cur.execute("""SELECT ch_num,title,status,priority,evidence_axis,word_count,theorems_count,body_md,issue_url
                 FROM ssot.chapters ORDER BY
                 CASE WHEN ch_num LIKE 'Ch.%' THEN 1 ELSE 2 END,
                 CASE WHEN ch_num LIKE 'Ch.%' THEN
                   LPAD(SUBSTRING(ch_num FROM 4),3,'0')
                 ELSE ch_num END""")
chapters = cur.fetchall()

# Override ordering for chapters: Ch.1..34, then App.A..J
def sort_key(c):
    ch = c[0]
    if ch.startswith('Ch.'):
        try: return (0, int(ch[3:]))
        except: return (0, 999)
    if ch.startswith('App.'):
        return (1, ord(ch[4]))
    return (2,0)

chapters = sorted(chapters, key=sort_key)

# Intro page
intro_md = """# GOLDEN SUNFLOWERS

**PhD on φ-Numerics for Neural Network Training**

> Anchor: $\\varphi^2 + \\varphi^{-2} = 3$ · TRINITY · v3.0 MEASURED HARDWARE · 🌻

This online edition is **synced live from Neon SSOT** (`schema=ssot`).
Every chapter body lives in `ssot.chapters.body_md`; agents that complete a
ONE SHOT directive update the row, and a GitHub Action rebuilds this book.

## Three evidence axes

1. **Empirical** — BPB benchmark vs FineWeb · multi-agent IGLA RACE · pre-registered seeds
2. **Formal Verification** — **297 Qed** in [t27/proofs/canonical/](https://github.com/gHashTag/t27/tree/feat/canonical-coq-home/proofs/canonical) · 38 bundles · 11 IGLA invariants · 28 falsification examples · CI-gated
3. **Hardware** — **QMTech XC7A100T** Artix-7 · **0 DSP** · **63 toks/sec @ 92 MHz** · **0.94–1.07 W bench** · 5.8 / 19.6 % LUT · 9.8 / 52 % BRAM · 1003 toks HSLM sim-verified

## Sources of truth

| Layer | Link |
|---|---|
| **Coq SSOT** | [t27#569](https://github.com/gHashTag/t27/pull/569) |
| **Master Book v3.0** | [trios#380](https://github.com/gHashTag/trios/issues/380) |
| **Coq Census** | [trios#373 comment](https://github.com/gHashTag/trios/issues/373#issuecomment-4351659821) |
| **SSOT issue** | [trios#372](https://github.com/gHashTag/trios/issues/372) |
| **Live Dashboard** | `phd-dashboard.up.railway.app` |
| **Download PDF** | [t27.ai/pdf/full](/pdf/full) (compiled live by tectonic) |

## Sanctioned seeds

`{F₁₇=1597, F₁₈=2584, F₁₉=4181, F₂₀=6765, F₂₁=10946} ∪ {L₇=29, L₈=47}`

Forbidden seeds: `{42, 43, 44, 45}` (never used).

## R5-honest disclosure

**297 Qed proven · 41 Admitted (Coq.Interval upgrade lane) · 11 Abort (no silent merges).**
**AI-as-author forbidden** — only `AI-assisted code generation` in Acknowledgments.

`phi^2 + phi^-2 = 3 · TRINITY · NEVER STOP 🌻`
"""
open(f"{ROOT}/intro.md","w").write(intro_md)

# Per-chapter pages
status_emoji = {'drafted':'🟢','done':'🟢','running':'🟡','stub':'🔴','wait-A1':'🟡','in_progress':'🟡','review':'🟡'}
def status_class(s):
    return 'status-done' if s in ('drafted','done') else 'status-running' if s in ('running','wait-A1','in_progress','review') else 'status-pending'

for ch in chapters:
    ch_num, title, status, prio, axis, words, thm_cnt, body_md, issue_url = ch
    fname = f"{slug(ch_num)}.md"
    se = status_emoji.get(status,'⚪')
    cls = status_class(status)
    axis_label = {1:'Empirical',2:'Formal',3:'Hardware'}.get(axis or 0, '-')
    issue_n = (issue_url or '').split('/')[-1] if issue_url else ''
    issue_link = f"[#{issue_n}]({issue_url})" if issue_url else "-"
    header = (
        f"<div class=\"{cls}\" style=\"display:flex;flex-wrap:wrap;gap:.6em;margin-bottom:1em;font-size:.95em\">"
        f"<span><b>{se} Status:</b> {status}</span>"
        f"<span><b>Priority:</b> {prio or '-'}</span>"
        f"<span><b>Axis:</b> {axis_label}</span>"
        f"<span><b>Target:</b> {words or '?'}w</span>"
        f"<span><b>Theorems:</b> {thm_cnt or 0}</span>"
        f"<span><b>Issue:</b> {issue_link}</span>"
        f"</div>\n\n---\n\n"
    )
    body = body_md or f"# {title}\n\n*Stub — pending agent draft.*"
    open(f"{ROOT}/{fname}","w").write(header + body)

# SUMMARY.md
summary = ["# Summary\n", "[Introduction](intro.md)", "[About the Author](about.md)\n", "\n# Part I — Body\n"]
ch_nums = [c[0] for c in chapters if c[0].startswith('Ch.')]
for c in chapters:
    if c[0].startswith('Ch.'):
        summary.append(f"- [{c[0]} · {c[1]}]({slug(c[0])}.md)")
summary.append("\n# Part II — Appendices\n")
for c in chapters:
    if c[0].startswith('App.'):
        summary.append(f"- [{c[0]} · {c[1]}]({slug(c[0])}.md)")
open(f"{ROOT}/SUMMARY.md","w").write('\n'.join(summary)+'\n')

print(f"Wrote {len(chapters)} chapter pages + SUMMARY.md to {ROOT}")
print("Sample SUMMARY:")
print(open(f"{ROOT}/SUMMARY.md").read()[:600])
conn.close()
