#!/usr/bin/env python3
"""
partition-lots.py -- write disambiguation clauses into the 13 skills whose
descriptions name no sibling in their own intent lot.  2026-08-12

Each edit: optional CUT (prose removed to make room -- never a trigger phrase),
then ADD (a clause naming at least one lot-mate and the boundary between them).

Safety: operates on the normalized description string, re-emits it as a YAML
folded block, then RE-PARSES the file and asserts the result matches what was
intended and stays under 1024. Any file that fails verification is restored.

Run: python3 partition-lots.py [--apply]
"""

import sys, re, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent
APPLY = "--apply" in sys.argv
LIMIT = 1024

# skill -> (cut_substring_or_None, clause_to_append)
EDITS = {
 "apex-builder-gate": (None,
   " NOT self-audit (an agent grading its own finished work) or auditor-general"
   " (post-hoc review): this fires BEFORE execution and blocks it."),
 "astrodiary-ds-enforcer": (
   " Design drift is cheaper to catch before the first line is written than after"
   " the whole screen is done wrong.",
   " NOT verify-loop or self-audit: AstroDiary UI only."),
 "critical-thinker": (None,
   " NOT logic-thinker (maps premises, tests validity) or loop-breaker (escapes a"
   " stuck frame): this attacks the idea itself."),
 # The next three would land with 3-7 chars of headroom on clause alone. Rationale
 # prose is cut instead: a description is a retrieval surface, not documentation --
 # the "why" belongs in the skill body, where it costs nothing.
 "git-ops": (
   " Use this skill whenever the user or an agent needs to commit, clean history, read"
   " the log, summarize build state, manage branches, or resolve conflicts.",
   " NOT meta-no-bare-names (gates file names and dated headers pre-commit)."),
 "herald-config-doctor": (
   " The herald-health-monitor DETECTS stale config every run but never FIXES it, so the"
   " same three findings recur (\"4th run, still pending\") while masking real regressions.",
   " NOT machine-bridge (sandbox-to-machine handoff) or gcp-iam-resolver (cloud IAM)."),
 "machine-bridge": (
   " Cowork agents run in a Linux sandbox whose session path rotates every session and"
   " whose mounts can lag the user's machine, producing a recurring failure class:",
   " NOT gcp-iam-resolver (cloud IAM) or disk-doctor."),
 "meta-no-bare-names": (None,
   " NOT git-ops, which performs the commit itself: this gate only blocks bad file"
   " names and stale headers."),
 "session-bootstrap": (
   " Cowork is stateless — every session boots blank — so this is how you"
   " reconstitute a workspace instead of re-deriving it.",
   " NOT arise or reentry (both read existing state): this mounts and verifies."),
 "session-rules": (None,
   " NOT arise (loads live project state) or session-bootstrap (mounts folders and"
   " credentials): this fetches only the cross-project reasoning rules."),
 "skill-miner": (None,
   " NOT skillmaker-publish (ships finished skills) or soul-builder (writes SOUL.md):"
   " this only proposes what to build next."),
 "skillmaker-publish": (None,
   " NOT skill-miner (proposes new skills): this validates and ships what already exists."),
 "soul-builder": (None,
   " NOT skill-miner (proposes skills) or skillmaker-publish (ships them): this writes"
   " a project's SOUL.md."),
 "patel-tone-converter": (
   " Pensado en primer lugar para las iniciativas de VMC Subastas / Echo Chamber"
   " (correos a ejecutivos y leads de subastas), pero usable para reescribir cualquier"
   " mensaje de venta o prospeccion que necesite mas gancho y menos tono corporativo plano.",
   " Usable para cualquier mensaje de venta o prospeccion que necesite mas gancho."
   " NO es copy-masterkey (pipeline completo) ni vmc-listing-copy (fichas de subasta)."),
}

DESC_SPAN = re.compile(r"^description:.*?(?=^[A-Za-z_]+:|\Z)", re.S | re.M)


def norm(s):
    return " ".join(s.split())


def emit(desc, width=92):
    words, lines, cur = desc.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "description: >-\n" + "".join(f"  {l}\n" for l in lines)


results = []
for skill, (cut, add) in EDITS.items():
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
            results.append((skill, "FAIL", "CUT text not found -- description changed?")); continue
        cur = norm(cur.replace(c, "", 1))
    if norm(add).split()[1] in cur and "NOT" in cur.upper()[-260:]:
        results.append((skill, "SKIP", "already carries a clause")); continue
    cur = norm(cur + add)

    if len(cur) > LIMIT:
        results.append((skill, "FAIL", f"would be {len(cur)} chars (>{LIMIT})")); continue

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

    if APPLY:
        p.write_text(new_txt, encoding="utf-8")
    results.append((skill, "OK", f"{before} -> {len(cur)} chars ({LIMIT-len(cur)} headroom)"))

w = max(len(s) for s, _, _ in results)
for s, st, msg in results:
    print(f"{st:5s} {s:{w}s}  {msg}")
bad = [r for r in results if r[1] == "FAIL"]
print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: "
      f"{sum(1 for r in results if r[1]=='OK')} ok, {len(bad)} failed")
if not APPLY:
    print("re-run with --apply to write")
sys.exit(1 if bad else 0)
