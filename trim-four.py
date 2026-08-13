#!/usr/bin/env python3
"""trim-four.py -- bring the 4 over-limit descriptions back under the 1024 cap.

All four were UNDER the limit before partition-newcomers.py added its clauses
(946 / 972 / 957 / 902). The clauses were ~130 chars each and pushed them over.
This rewrites each description with a short clause that still names its sibling,
plus a trim of the most redundant trigger phrases. Nothing structural is removed:
every distinct trigger family and every behavioral rule survives.

Run from the SKILL MAKER repo root:

    python3 trim-four.py
    ./publish.sh

Refuses to write any description that would land over 1000 chars, so it cannot
re-create the failure it exists to fix. Backs up each file to SKILL.md.bak3.
"""
import os
import re
import shutil
import sys
import textwrap

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not available. pip3 install pyyaml")

ROOT = os.path.abspath(os.path.dirname(__file__))
CEILING = 1000
WRAP = 92

NEW = {
"apex-health":
    'Read-only health sweep of the APEX Ultra runtime (M1) -- probes every surface '
    '(loop.py/snapshot, Schwab token, council_loop board, signal plans, scanner via '
    'watchdog, sa_news_feed, MASTERS, HERMES/Slack) and returns a verdict table with '
    'evidence, using a failure-signature library so known incidents are recognized in '
    'seconds. Use whenever the user says "system health check", "sweep the system", '
    '"is apex alive", "is everything running", "apex status", "estado del sistema", '
    '"is the loop up", "why is the board stale", "why no alerts today", "snapshot looks '
    'frozen", or asks ANY is-it-up / why-is-it-quiet / why-is-this-stale question about '
    'APEX Ultra, even casually mid-session. Also fire proactively before relaying a '
    'council verdict when data freshness is uncertain. Diagnoses and prescribes only -- '
    'never fixes (builder-handoff) and never deliberates (council-run). NOT '
    'carmatch-intel: that reads the CarMatch extractor pipeline.',

"dashboard-section":
    'Builds dashboard sections (new or rebuild) across any Subastop product -- AVT '
    'backoffice, CarMatch, AVT PLUS. Compresses the audit-reframe-spec-verify lifecycle '
    'from 2-3 hours of ad-hoc work to 30-45 minutes. Use whenever the user says "build '
    'dashboard section", "redo tab X", "audit tab Y", "BI view for Z", "make tab '
    'productive", "rebuild as BI surface", "convert flat browser to dashboard", '
    '"dashboard for [thing]", "dash next section", "let\'s tackle [tab name]", "new '
    'section in the dash", "this tab is desaprovechada", or mentions any dashboard tab '
    'name (Vehiculos, Chats, Pipeline, Comparables, MSRP, Usuarios, Scrape, AI Copy, '
    'Overview, Market Data) alongside a change verb (redo, audit, rebuild, fix, '
    'improve). Auto-detects product from path, routes to the right archetype (Analytical '
    'BI / Operational Monitoring / Directory CRUD), orchestrates the 4-phase lifecycle. '
    'NOT pre-deliver: that is the ship gate for strategic artifacts.',

"ds-enforcer":
    'Design system enforcement for Subastop ecosystem UIs (dashboards, cockpits, '
    'evaluators, landing pages). Fires BEFORE and AFTER writing any HTML/CSS in a '
    'Subastop project to catch design drift before it ships. Use whenever writing, '
    'reviewing, or reworking UI code in VMC, MAF, CarMatch, AVT, or any Subastop '
    'product. Trigger on: "ds enforcer", "design enforcer", "check the design", "enforce '
    'the DS", "is this on-spec", "does this match the design system", "audit this UI", '
    '"fix the design", "glass panel looks wrong", "section header is off", "this doesn\'t '
    'match the Stitch design", or any request to review or correct UI code in a Subastop '
    'context. Also trigger PROACTIVELY at the start of any build session that will '
    'produce HTML/CSS for a Subastop product, even if the user did not ask -- drift is '
    'cheaper to catch before the first line than after the panel is done wrong. NOT '
    'brief-bridge: that produces the Stitch prompt.',

"pre-deliver":
    'Pre-delivery gate for strategic artifacts in AVT_CarMatch_meta. Runs six checks '
    'BEFORE shipping -- canonical-read, scope-split, confidence-calibration, '
    'reframe-vs-extend, memory-hit, self-pattern-match -- emits PASS or BLOCK with '
    'corrections. Trigger BEFORE writing or editing BUILDER_PROMPT_*.md, IB_*.md, '
    'DIAGNOSTIC_*.md, AUDIT_*.md, RECON_*.md, FERRY_*.md, ANALYSIS_*.md, REFRAME_*.md in '
    'this project; BEFORE recommending a strategic fork (alpha vs beta, abort vs '
    'continue); BEFORE reframing session direction; BEFORE sending a strategic '
    'recommendation longer than ~40 lines. Trigger AFTER POPs reframes mid-session '
    '(frustration markers, "indignante", "te equivocas", direction change). Also on '
    '"/pre-deliver", "gate this", "before I send", "run the gate", "is this ready". '
    'Enforcement layer for feedback_* memories that document but do not fire at decision '
    'time. NOT self-audit: that is the builder checking its own work.',
}


def split_fm(txt):
    m = re.match(r"^---\n(.*?)\n---\n?", txt, re.S)
    return (m.group(1), txt[m.end():]) if m else (None, None)


def desc_span(fm):
    m = re.search(r"^description:", fm, re.M)
    if not m:
        return None
    rest = fm[m.end():]
    nxt = re.search(r"\n(?=[A-Za-z_][A-Za-z0-9_-]*:)", rest)
    return m.start(), m.end() + (nxt.start() if nxt else len(rest))


def main():
    over = [(k, len(v)) for k, v in NEW.items() if len(v) > CEILING]
    if over:
        sys.exit(f"ERROR: replacement text itself is too long: {over}. Nothing written.")

    results, failed = [], []
    for name, text in NEW.items():
        path = os.path.join(ROOT, name, "SKILL.md")
        if not os.path.isfile(path):
            failed.append((name, "SKILL.md not found"))
            continue
        raw = open(path, encoding="utf-8").read()
        fm, body = split_fm(raw)
        if fm is None:
            failed.append((name, "no frontmatter"))
            continue
        span = desc_span(fm)
        if not span:
            failed.append((name, "no description key"))
            continue
        before = len(str(yaml.safe_load(fm).get("description", "")))
        s, e = span
        block = "description: >-\n" + "\n".join(
            "  " + l for l in textwrap.wrap(text, width=WRAP))
        new_fm = fm[:s] + block + fm[e:]
        try:
            after = len(str(yaml.safe_load(new_fm).get("description", "")))
        except Exception as ex:
            failed.append((name, f"rewrite does not parse: {str(ex).splitlines()[0]}"))
            continue
        if after > CEILING:
            failed.append((name, f"still {after} chars after rewrite"))
            continue
        shutil.copy2(path, path + ".bak3")
        open(path, "w", encoding="utf-8").write(f"---\n{new_fm}\n---\n{body}")
        results.append((name, before, after))

    for n, b, a in results:
        print(f"  {n:<20} {b} -> {a}  (saved {b - a})")
    if failed:
        print("\nNOT WRITTEN:")
        for n, why in failed:
            print(f"  {n}: {why}")
        return 1
    print(f"\n{len(results)} descriptions rewritten, all under {CEILING}. "
          "Backups: SKILL.md.bak3")
    print("\nNEXT:\n  ./publish.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
