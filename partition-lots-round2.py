#!/usr/bin/env python3
"""
partition-lots-round2.py -- the remaining 21 lot-mates.  2026-08-12

Round 1 (partition-lots.py) did 13. The detector was then corrected from a prose
regex to the real invariant -- "does this description NAME a sibling in its own
lot" -- which surfaced 21 more. Same machinery, plus one new guard.

NEW GUARD (from round 1's near-miss): a CUT is refused unless a distinctive
keyword from the removed text still appears in the skill BODY. Round 1 cut
rationale from three descriptions on the principle that a description is a
retrieval surface and the "why" belongs in the body -- correct there, verified
after the fact. This makes it verified BEFORE.

Run: python3 partition-lots-round2.py [--apply]
"""

import sys, re, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent
APPLY = "--apply" in sys.argv
LIMIT = 1024
# A clause that lands at 1023/1024 "passes" while making the skill un-editable.
# Refuse any edit leaving less than this much room. Skills that cannot take a
# clause without breaching it are BLOCKED on the description trim pending since
# docs/TOOLBOX_AUDIT_2026-06-24.md -- report them, do not force a hollow clause in.
MIN_HEADROOM = 40

# skill -> (cut_or_None, body_keyword_that_must_survive_or_None, clause)
EDITS = {
 # --- audit ---------------------------------------------------------------
 "projectmd-auditor": (None, None,
   " NOT auditor-general (reviews builds and fixes): this only ranks CLAUDE.md context files."),
 "pwa-verify": (
   " Exists because stale service-worker bundles have repeatedly masked whether a fix"
   " landed -- one defect survived six deploys this way before the stale cache was"
   " identified as the root cause.", "service",
   " NOT verify-loop (checks work before delivery) or self-audit: this verifies a shipped"
   " deploy on a real device."),
 "qa-sequence": (None, None,
   " NOT self-audit or verify-loop: this reviews a recorded QA pass frame by frame."),
 "self-audit": (None, None,
   " NOT auditor-general: the builder checks its own work."),
 "workspace-plugin-audit": (None, None,
   " NOT auditor-general: marketplace install state."),
 # --- delegate ------------------------------------------------------------
 "codex-audit-handoff": (None, None,
   " NOT offload: this packages work for Codex."),
 "offload": (None, None,
   " NOT codex-audit-handoff (packages work for Codex): this spins a cheaper Claude subagent."),
 # --- diagnose ------------------------------------------------------------
 "disk-doctor": (None, None,
   " NOT machine-bridge (sandbox-to-machine handoff) or gcp-iam-resolver: Mac disk space only."),
 "gcp-iam-resolver": (None, None,
   " NOT herald-config-doctor: GCP IAM only."),
 # --- hygiene -------------------------------------------------------------
 "projectmd-optimizer": (None, None,
   " NOT space-steward: one CLAUDE.md."),
 "space-steward": (None, None,
   " NOT projectmd-optimizer (compresses CLAUDE.md)."),
 # --- observe -------------------------------------------------------------
 "carmatch-intel": (None, None,
   " NOT qa-mirror (live phone screen): this reads the CarMatch pipeline."),
 "qa-mirror": (None, None,
   " NOT carmatch-intel (pipeline state): live phone mirror only."),
 # --- orient --------------------------------------------------------------
 "continuity-seed": (None, None,
   " NOT reentry (reconstructs state from the machines): this writes a briefing."),
 "reentry": (None, None,
   " NOT continuity-seed (writes a handoff doc) or session-bootstrap (mounts folders):"
   " this reconstructs build state."),
 # --- reason --------------------------------------------------------------
 "loop-breaker": (None, None,
   " NOT critical-thinker or logic-thinker."),
 "toolbox": (None, None,
   " NOT critical-thinker or loop-breaker: routes."),
 # --- relay ---------------------------------------------------------------
 "agent-bridge": (None, None,
   " NOT inbox-triage (surfaces without acting): this reads, acts, and responds."),
 "notebooklm-bridge": (None, None,
   " NOT agent-bridge (project-to-project inboxes): this queries a NotebookLM notebook."),
 "project-handover": (
   " Built from real handover failure modes: stale org access, a job silently pointing at"
   " a dead path for weeks, unsynced repo clones.", "stale",
   " NOT project-migrate (moves a project between machines): this transfers ownership to people."),
 "project-migrate": (None, None,
   " NOT project-handover (transfer to new owners): machines only."),
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
for skill, (cut, guard, add) in EDITS.items():
    p = ROOT / skill / "SKILL.md"
    if not p.exists():
        results.append((skill, "FAIL", "no SKILL.md")); continue
    original = p.read_text(encoding="utf-8")
    m = re.search(r"^---\n(.*?)\n---", original, re.S)
    if not m:
        results.append((skill, "FAIL", "no frontmatter")); continue
    fm = m.group(1)
    span = DESC_SPAN.search(fm + "\n")
    if not span:
        results.append((skill, "FAIL", "no description field")); continue
    cur = norm(re.sub(r"^description:\s*>?-?\s*", "", span.group(0), count=1))
    before = len(cur)

    if cut:
        c = norm(cut)
        if c not in cur:
            results.append((skill, "FAIL", "CUT text not found")); continue
        if guard and guard.lower() not in body_of(original).lower():
            results.append((skill, "FAIL",
                            f"REFUSED: '{guard}' absent from body -- cut would delete, not relocate"))
            continue
        cur = norm(cur.replace(c, "", 1))
    cur = norm(cur + add)
    if LIMIT - len(cur) < MIN_HEADROOM:
        results.append((skill, "BLOCK",
                        f"{before} + clause = {len(cur)}, only {LIMIT-len(cur)} headroom "
                        f"(< {MIN_HEADROOM}) -- needs a description trim first"))
        continue

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

w = max(len(s) for s, _, _ in results)
for s, st, msg in results:
    print(f"{st:5s} {s:{w}s}  {msg}")
bad = [r for r in results if r[1] == "FAIL"]
blocked = [r[0] for r in results if r[1] == "BLOCK"]
print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: {sum(1 for r in results if r[1]=='OK')} ok, "
      f"{len(blocked)} blocked on trim, {len(bad)} failed")
if blocked:
    print("blocked (description too long to carry a real clause): " + ", ".join(blocked))
if not APPLY:
    print("re-run with --apply to write")
sys.exit(1 if bad else 0)
