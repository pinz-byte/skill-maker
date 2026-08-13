#!/usr/bin/env python3
"""partition-newcomers.py -- unblock publish.sh after promoting the rescued skills.

Run once, natively, from the SKILL MAKER repo root:

    python3 partition-newcomers.py
    ./publish.sh

Three jobs:
  1. PULL `morning` back out. The live Customize -> Skills list attributes it to
     **Anthropic**, not POPs -- same rule as skill-creator. Moves it back to
     rescued/ and drops it from lfp-symbios in build-marketplace.py.
  2. ASSIGN the 4 skills `assign --apply` left unsorted.
  3. PARTITION: append an explicit `NOT <sibling>` clause to the description of
     every skill the gate named as "names no sibling". Naming the sibling is what
     the gate actually checks.

Idempotent: a skill that already carries its clause is skipped. Backs up
build-marketplace.py to build-marketplace.py.bak2.
"""
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
RESCUED = os.path.join(ROOT, "rescued")
BUILD = os.path.join(ROOT, "build-marketplace.py")

PULL_OUT = "morning"

ASSIGN = {
    "apu-series-generator": "build",
    "cc-session-analyzer": "audit",
    "ib": "reason",
    "masterkey": "reason",
}

# skill -> clause appended to its description. Each names a same-lot sibling.
CLAUSES = {
    # lot: audit
    "dashboard-section":
        "NOT pre-deliver (the ship gate for strategic artifacts): this runs the "
        "audit-reframe-spec-verify lifecycle for one dashboard section.",
    "dependency-audit":
        "NOT auditor-general (reviews a build after it lands): this prices external "
        "dependencies BEFORE any code ships.",
    "forensic-auditor":
        "NOT auditor-general (delivers a verdict on a finished build): this traces "
        "where data came from and how a system was actually built.",
    "pre-deliver":
        "NOT self-audit (the builder checking its own work before delivery): this is "
        "the six-check ship gate for AVT_CarMatch_meta strategic artifacts.",
    "cc-session-analyzer":
        "NOT work-retrospective (audits one finished piece of work): this mines 30 "
        "days of Claude Code sessions into an HTML usage report.",
    # lot: build
    "factory-gate":
        "NOT phased-deploy (runs the commit-build-deploy sequence): this BLOCKS "
        "Pagebuilder Factory work until the stage gates pass.",
    "phased-deploy":
        "NOT carmatch-deploy (CarMatch-specific targets and gotchas): this is the "
        "generic phased commit-build-deploy discipline for any project.",
    "project-init":
        "NOT projectmd-gen (writes CLAUDE.md and nothing else): this scaffolds the "
        "whole .claude/ directory -- hooks, agent config and rules.",
    "apu-series-generator":
        "NOT project-init (scaffolds a project): this stamps APU production series "
        "lines onto badge artwork for laser engraving.",
    # lot: decide
    "council":
        "NOT council-run (fires a fresh intraday deliberation): this DISPLAYS the "
        "latest cached verdicts, read-only.",
    # lot: manage
    "builder-handoff":
        "NOT pm (tracks what is open on a project): this packages work the sandbox "
        "cannot execute into a handoff for a real machine.",
    "pm":
        "NOT builder-handoff (packages sandbox-blocked work for a real machine): this "
        "reads the Focus Queue for THIS project and closes its rows.",
    # lot: observe
    "apex-health":
        "NOT carmatch-intel (reads the CarMatch extractor pipeline): this probes the "
        "APEX Ultra runtime on M1.",
    "investigator":
        "NOT apex-health (probes one named runtime on demand): this is an always-on "
        "posture that hunts the missing piece in any interaction.",
    # lot: orient
    "cowork-friday-handoff":
        "NOT continuity-seed (writes a briefing for the next session): this closes the "
        "work week into the Continuity Feed.",
    "projectmd-gen":
        "NOT projectmd-auditor (ranks the CLAUDE.md files that already exist): this "
        "generates one from scratch by scanning the project.",
    # lot: reason
    "amorata-voice-system":
        "NOT masterkey (a general creative process): this loads Amorata's dual-voice "
        "architecture for the Carta natal project only.",
    "ib":
        "NOT ceo-planner (pressure-tests a plan that already exists): this builds the "
        "intention from zero -- matrix first, then blueprint.",
    "masterkey":
        "NOT ib (builds a project intention): this is the 7-step creative process for "
        "producing one artifact.",
    "ultrathink":
        "NOT critical-thinker (attacks the idea itself): this only escalates reasoning "
        "depth on the current prompt.",
    "work-retrospective":
        "NOT self-audit (runs before delivery): this captures learning AFTER the work "
        "is finished.",
    # lot: write
    "brief-bridge":
        "NOT copy-deck (writes the page copy itself): this converts IB output, design "
        "tokens and real copy into a paste-ready Stitch prompt.",
    "ds-enforcer":
        "NOT brief-bridge (produces the Stitch prompt): this enforces Subastop design "
        "tokens before and after any HTML/CSS is written.",
    "source-scout":
        "NOT copy-deck (produces marketing copy): this discovers, validates and "
        "configures new vehicle listing sources for the AVT Extractor.",
    "voice-bench-gate":
        "NOT copy-deck (writes the copy): this grounds every claim in a verified "
        "source before the copy gets written.",
}


def split_fm(txt):
    m = re.match(r"^---\n(.*?)\n---\n?", txt, re.S)
    return (m.group(1), txt[m.end():]) if m else (None, None)


def desc_span(fm):
    """Return (start, end) char offsets of the whole description block in fm."""
    m = re.search(r"^description:", fm, re.M)
    if not m:
        return None
    start = m.start()
    rest = fm[m.end():]
    nxt = re.search(r"\n(?=[A-Za-z_][A-Za-z0-9_-]*:)", rest)
    end = m.end() + (nxt.start() if nxt else len(rest))
    return start, end


def append_clause(fm, clause):
    span = desc_span(fm)
    if not span:
        return None
    s, e = span
    block = fm[s:e]
    head = block.split("\n", 1)[0]
    val = head[len("description:"):].strip()

    if val.startswith(">") or val.startswith("|"):
        lines = [l for l in block.split("\n")[1:] if l.strip()]
        indent = re.match(r"^(\s*)", lines[-1]).group(1) if lines else "  "
        new = block.rstrip() + "\n" + indent + clause
    elif val.startswith('"') or val.startswith("'"):
        q = val[0]
        i = block.rstrip().rfind(q)
        if i <= block.find(q):
            return None
        body = block.rstrip()
        new = body[:i].rstrip() + " " + clause + body[i:]
    else:
        new = block.rstrip() + " " + clause
    return fm[:s] + new + fm[e:]


def set_intent(fm, lot):
    if re.search(r"^\s*intent:", fm, re.M):
        return re.sub(r"^(\s*)intent:.*$", rf"\g<1>intent: {lot}", fm, count=1, flags=re.M)
    if re.search(r"^metadata:\s*$", fm, re.M):
        return re.sub(r"^metadata:\s*$", f"metadata:\n  intent: {lot}", fm, count=1, flags=re.M)
    return fm.rstrip() + f"\nmetadata:\n  intent: {lot}"


def edit(skill, clause=None, lot=None):
    p = os.path.join(ROOT, skill, "SKILL.md")
    if not os.path.isfile(p):
        return f"MISSING {skill}/SKILL.md"
    txt = open(p, encoding="utf-8").read()
    fm, body = split_fm(txt)
    if fm is None:
        return f"NO FRONTMATTER {skill}"
    notes = []
    if lot:
        fm = set_intent(fm, lot)
        notes.append(f"intent={lot}")
    if clause:
        key = clause.split(":")[0].strip()
        if key in fm:
            notes.append("clause already present")
        else:
            new_fm = append_clause(fm, clause)
            if new_fm is None:
                return f"COULD NOT PARSE description in {skill}"
            fm = new_fm
            notes.append("clause added")
    open(p, "w", encoding="utf-8").write(f"---\n{fm}\n---\n{body}")
    return f"{skill}: " + ", ".join(notes)


def pull_out():
    src, dst = os.path.join(ROOT, PULL_OUT), os.path.join(RESCUED, PULL_OUT)
    moved = False
    if os.path.isdir(src) and not os.path.isdir(dst):
        shutil.move(src, dst)
        moved = True
    src_txt = open(BUILD, encoding="utf-8").read()
    if f'"{PULL_OUT}"' in src_txt:
        shutil.copy2(BUILD, BUILD + ".bak2")
        out = re.sub(rf'"{PULL_OUT}",\s*', "", src_txt, count=1)
        out = re.sub(rf',\s*"{PULL_OUT}"', "", out, count=1)
        open(BUILD, "w", encoding="utf-8").write(out)
        return moved, True
    return moved, False


def main():
    if not os.path.isfile(BUILD):
        sys.exit("ERROR: run this from the SKILL MAKER repo root.")
    os.makedirs(RESCUED, exist_ok=True)

    moved, degrouped = pull_out()
    print(f"morning: moved back to rescued/={moved}  removed from GROUPS={degrouped}")

    print("\nassigning the 4 unsorted:")
    for s, lot in ASSIGN.items():
        print("  " + edit(s, clause=CLAUSES.get(s), lot=lot))

    print("\npartitioning (clause names a same-lot sibling):")
    for s, c in CLAUSES.items():
        if s in ASSIGN:
            continue
        print("  " + edit(s, clause=c))

    print(f"\n{len(CLAUSES)} clauses, 4 intents, 1 skill pulled out.")
    print("Backup: build-marketplace.py.bak2")
    print("\nNEXT:\n  ./publish.sh")
    print("If the gate still FAILs, paste the FAIL lines back -- each remaining")
    print("name just needs its own NOT-clause; nothing else is wrong.")


if __name__ == "__main__":
    main()
