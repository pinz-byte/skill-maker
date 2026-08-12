#!/usr/bin/env python3
"""
make-catalog-html.py -- render the intent catalog as a self-contained HTML page.
2026-08-12

CATALOG.md serves the model (imported by CLAUDE.md). This serves POPs, who is the
party that actually had the discovery problem: at turn one of the session that
started this work, the model answered "do we have a project manager skill?"
correctly and instantly from context it already had. The human could not.

Reads every */SKILL.md, groups by declared intent lot, and emits CATALOG.html --
one file, no dependencies, live search across names and full descriptions, and
the disambiguation boundary surfaced per skill rather than buried mid-paragraph.

Run: python3 make-catalog-html.py
"""

import re, glob, os, json, html, datetime, collections

try:
    import yaml
except ImportError:
    raise SystemExit("pyyaml required")

SKIP = {"plugins", "team-skills", "shared", "docs", "tools", "automation",
        "team-toolkit", "reentry-workspace", "__pycache__"}

LOT_ORDER = ["orient", "manage", "decide", "observe", "diagnose", "audit",
             "build", "relay", "write", "reason", "hygiene", "delegate"]
LOT_BLURB = {
    "orient": "load context, resume, figure out where we are",
    "manage": "see what's open, blocked, owed",
    "decide": "get a verdict on a position or option",
    "observe": "read live system state right now",
    "diagnose": "something is broken -- find the cause",
    "audit": "verify something already built or claimed",
    "build": "make, publish, or ship an artifact",
    "relay": "move information between agents, projects, people",
    "write": "produce or convert prose and copy",
    "reason": "think harder, break a loop, stress-test",
    "hygiene": "keep files, context, disk, history disciplined",
    "delegate": "hand work to a cheaper model or another tool",
}

skills = []
for p in sorted(glob.glob("*/SKILL.md")):
    d = os.path.basename(os.path.dirname(p))
    if d in SKIP or d.startswith("."):
        continue
    fm = re.search(r"^---\n(.*?)\n---", open(p, encoding="utf-8").read(), re.S)
    if not fm:
        continue
    meta = yaml.safe_load(fm.group(1)) or {}
    desc = " ".join(str(meta.get("description", "")).split())
    lot = (meta.get("metadata") or {}).get("intent", "unsorted")
    # The boundary sentence: the clause naming a sibling.
    bound = ""
    mb = re.search(r"((?:NOT|NO es|Distinto de|For [a-z-]+ use)[^.]*\.)", desc)
    if mb:
        bound = mb.group(1).strip()
    lead = re.split(r"(?<=[a-z])\.\s|\s--\s", desc)[0].strip().rstrip(".,")
    skills.append({"n": d, "lot": lot, "lead": lead, "bound": bound,
                   "desc": desc, "len": len(desc)})

by = collections.defaultdict(list)
for s in skills:
    by[s["lot"]].append(s)

rows = []
for lot in LOT_ORDER + sorted(set(by) - set(LOT_ORDER)):
    if lot not in by:
        continue
    rows.append(f'<section class="lot" data-lot="{html.escape(lot)}">')
    rows.append(f'<h2>{html.escape(lot.upper())}'
                f'<span class="blurb">{html.escape(LOT_BLURB.get(lot,""))}</span>'
                f'<span class="ct">{len(by[lot])}</span></h2>')
    for s in sorted(by[lot], key=lambda x: x["n"]):
        b = (f'<div class="bound">{html.escape(s["bound"])}</div>'
             if s["bound"] else '')
        rows.append(
            f'<article class="sk" data-hay="{html.escape((s["n"]+" "+s["desc"]).lower())}">'
            f'<div class="hd"><code>{html.escape(s["n"])}</code>'
            f'<span class="len">{s["len"]}</span></div>'
            f'<p class="lead">{html.escape(s["lead"])}</p>{b}'
            f'<details><summary>full description</summary>'
            f'<p class="full">{html.escape(s["desc"])}</p></details></article>')
    rows.append("</section>")

DOC = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SKILL MAKER -- Intent Catalog</title><style>
:root{--bg:#0f1115;--card:#171a21;--ink:#e6e9ef;--dim:#9aa4b2;--line:#252a33;--acc:#7aa2f7;--warn:#e0af68}
@media(prefers-color-scheme:light){:root{--bg:#f7f8fa;--card:#fff;--ink:#1a1d23;--dim:#5a6472;--line:#e3e6ea;--acc:#2f5fd0;--warn:#9a6b00}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 ui-sans-serif,-apple-system,"SF Pro Text",Segoe UI,sans-serif;padding:0 0 4rem}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);
padding:1.1rem 1.4rem .9rem;z-index:5}
h1{margin:0 0 .15rem;font-size:1.05rem;letter-spacing:.02em}
.sub{color:var(--dim);font-size:.8rem;margin-bottom:.7rem}
#q{width:100%;padding:.6rem .75rem;border-radius:8px;border:1px solid var(--line);
background:var(--card);color:var(--ink);font-size:.92rem}
#q:focus{outline:2px solid var(--acc);outline-offset:1px}
main{padding:1.2rem 1.4rem;max-width:920px;margin:0 auto}
.lot{margin:0 0 1.9rem}
h2{font-size:.76rem;letter-spacing:.12em;color:var(--acc);margin:0 0 .7rem;
display:flex;align-items:baseline;gap:.6rem;border-bottom:1px solid var(--line);padding-bottom:.4rem}
.blurb{color:var(--dim);letter-spacing:0;font-weight:400;font-size:.78rem;text-transform:none}
.ct{margin-left:auto;color:var(--dim);font-weight:400}
.sk{background:var(--card);border:1px solid var(--line);border-radius:9px;
padding:.7rem .85rem;margin:0 0 .5rem}
.hd{display:flex;align-items:center;gap:.6rem}
code{font:600 .87rem ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink)}
.len{margin-left:auto;color:var(--dim);font-size:.7rem;font-variant-numeric:tabular-nums}
.lead{margin:.35rem 0 0;color:var(--dim);font-size:.86rem}
.bound{margin-top:.45rem;padding:.35rem .5rem;border-left:2px solid var(--warn);
background:color-mix(in srgb,var(--warn) 8%,transparent);font-size:.8rem;border-radius:0 4px 4px 0}
details{margin-top:.45rem}summary{cursor:pointer;color:var(--dim);font-size:.76rem}
.full{font-size:.8rem;color:var(--dim);margin:.4rem 0 0}
.hide{display:none}
footer{max-width:920px;margin:0 auto;padding:0 1.4rem;color:var(--dim);font-size:.75rem}
</style>
<header><h1>SKILL MAKER &mdash; Intent Catalog</h1>
<div class="sub">__N__ skills across __L__ lots &middot; generated __D__ &middot;
indexed by what you want, not what the skill is called</div>
<input id="q" placeholder="search names and descriptions (e.g. project, stuck, publish, phone)" autofocus></header>
<main>__ROWS__</main>
<footer>Highlighted lines are disambiguation boundaries &mdash; what a skill is
<em>not</em>, versus its lot-mates. Regenerate with <code>python3 make-catalog-html.py</code>.</footer>
<script>
var q=document.getElementById('q'),cards=[].slice.call(document.querySelectorAll('.sk')),
lots=[].slice.call(document.querySelectorAll('.lot'));
q.addEventListener('input',function(){var t=q.value.trim().toLowerCase();
cards.forEach(function(c){c.classList.toggle('hide',t&&c.dataset.hay.indexOf(t)<0)});
lots.forEach(function(l){var any=[].slice.call(l.querySelectorAll('.sk'))
.some(function(c){return !c.classList.contains('hide')});l.classList.toggle('hide',!any)})});
</script></html>"""

out = (DOC.replace("__ROWS__", "\n".join(rows))
          .replace("__N__", str(len(skills)))
          .replace("__L__", str(len(by)))
          .replace("__D__", datetime.date.today().isoformat()))
open("CATALOG.html", "w", encoding="utf-8").write(out)
print(f"wrote CATALOG.html -- {len(skills)} skills, {len(by)} lots, "
      f"{sum(1 for s in skills if s['bound'])} with a visible boundary")
