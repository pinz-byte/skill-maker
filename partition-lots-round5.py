#!/usr/bin/env python3
"""
partition-lots-round5.py -- clear TRIM_DEBT.  2026-08-12

The five skills excused in skill-intent-audit.py's TRIM_DEBT set. Each already
disambiguates against something -- just not against a LOT-MATE (continuity-seed
vs /compact, space-steward vs /pm, qa-mirror vs a roaming setup). So these are
small, targeted edits: cut one redundant clause, name a sibling.

Every CUT is guarded: the removed concept must still exist in the skill body, or
the edit is refused. MIN_HEADROOM=40 still applies.

After this runs clean, delete TRIM_DEBT's contents in skill-intent-audit.py --
the gate warns if the set lists a skill that is no longer naked.
"""

import sys, re, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent
APPLY = "--apply" in sys.argv
LIMIT, MIN_HEADROOM = 1024, 40

# skill -> (subs [(old,new)], body_guard_or_None)
PLAN = {
 "continuity-seed": ([
   (" Think of compact as compression, continuity-seed as serialization.", ""),
   ("If unsure which one the user wants, ask.",
    "If unsure which one the user wants, ask. NOT reentry, which reconstructs state from"
    " the machines: this one writes the briefing."),
 ], "compact"),
 "project-migrate": ([
   (', or casual variations like "let\'s move this over to the other Mac"', ""),
   ("Scope: Cowork projects with a filesystem only -- Chat-hosted projects have nothing to move.",
    "Scope: Cowork projects with a filesystem only. NOT project-handover, which documents a"
    " transfer to new owners: this moves machines."),
 ], "satellite"),
 "qa-mirror": ([
   (" Pairs with QA_MIRROR_SETUP.md for the one-time mirror config.",
    " NOT carmatch-intel (reads a data pipeline): this grabs the live mirrored phone screen."),
 ], "QA_MIRROR_SETUP"),
 "space-steward": ([
   (', "operational hygiene", "what automation is live"', ""),
   ("Pairs with workspace-plugin-audit and skill-miner.",
    "Pairs with workspace-plugin-audit; NOT projectmd-optimizer, which compresses one CLAUDE.md."),
 ], None),
 "workspace-plugin-audit": ([
   (" -- confirmed 2026-07-03 when a plugin sat 5+ weeks / 52 commits stale despite daily"
    " marketplace updates", ""),
   ("Also trigger on \"still not showing up\"",
    "NOT auditor-general (reviews builds): this is marketplace install state."
    " Also trigger on \"still not showing up\""),
 ], "stale"),
}

DESC_SPAN = re.compile(r"^description:.*?(?=^[A-Za-z_]+:|\Z)", re.S | re.M)
norm = lambda s: " ".join(s.split())


def emit(desc, width=92):
    words, lines, cur = desc.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "description: >-\n" + "".join(f"  {l}\n" for l in lines)


def body_of(txt):
    ends = [m.end() for m in re.finditer(r"^---\s*$", txt, re.M)]
    return txt[ends[1]:] if len(ends) >= 2 else ""


results = []
for skill, (subs, guard) in PLAN.items():
    p = ROOT / skill / "SKILL.md"
    original = p.read_text(encoding="utf-8")
    m = re.search(r"^---\n(.*?)\n---", original, re.S)
    fm = m.group(1)
    span = DESC_SPAN.search(fm + "\n")
    cur = norm(re.sub(r"^description:\s*>?-?\s*", "", span.group(0), count=1))
    before = len(cur)

    if guard and guard.lower() not in body_of(original).lower():
        results.append((skill, "FAIL", f"REFUSED: '{guard}' absent from body")); continue
    miss = [o for o, _ in subs if norm(o) not in cur]
    if miss:
        results.append((skill, "FAIL", f"not found: {miss[0][:48]!r}")); continue
    for old, new in subs:
        cur = norm(cur.replace(norm(old), new, 1))
    if LIMIT - len(cur) < MIN_HEADROOM:
        results.append((skill, "BLOCK", f"{len(cur)}, {LIMIT-len(cur)} headroom")); continue

    new_fm = fm[:span.start()] + emit(cur) + fm[span.end():]
    new_txt = original[:m.start()] + "---\n" + new_fm.rstrip("\n") + "\n---" + original[m.end():]
    try:
        parsed = yaml.safe_load(re.search(r"^---\n(.*?)\n---", new_txt, re.S).group(1))
    except Exception as e:
        results.append((skill, "FAIL", f"YAML would break: {e}")); continue
    if norm(parsed.get("description", "")) != cur:
        results.append((skill, "FAIL", "round-trip mismatch")); continue
    if not (parsed.get("metadata") or {}).get("intent"):
        results.append((skill, "FAIL", "intent lost")); continue
    if body_of(new_txt).strip() != body_of(original).strip():
        results.append((skill, "FAIL", "body changed -- refusing")); continue

    if APPLY:
        p.write_text(new_txt, encoding="utf-8")
    results.append((skill, "OK", f"{before} -> {len(cur)} ({LIMIT-len(cur)} headroom)"))

for s, st, msg in results:
    print(f"{st:5s} {s:24s}  {msg}")
print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: {sum(1 for r in results if r[1]=='OK')}/5 ok")
if not APPLY:
    print("re-run with --apply to write")
sys.exit(0 if all(r[1] == "OK" for r in results) else 1)
