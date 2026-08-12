#!/usr/bin/env python3
"""
partition-lots-round3.py -- the last lot: reason.  2026-08-12

loop-breaker and toolbox were BLOCKED in round 2: appending a clause left them
with 19 and 2 chars of headroom. But both descriptions already END with a
disambiguation sentence that names no skill -- "Not a critic, not an optimism
engine" and "it chooses and chains the skills that do". Rewriting those in place
to name lot-mates costs almost nothing, which beats appending a second clause
that says the same thing twice.

Substitution, not append. Same verification: YAML round-trip, intent preserved,
body untouched, and MIN_HEADROOM enforced.
"""

import sys, re, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent
APPLY = "--apply" in sys.argv
LIMIT, MIN_HEADROOM = 1024, 40

SUBS = {
 "loop-breaker": [
   ("Not a critic, not an optimism engine:",
    "NOT critical-thinker, not creative-thinker:"),
 ],
 "toolbox": [
   ("it does not do the work itself, it chooses and chains the skills that do.",
    "it does not do the work itself: it chooses and chains critical-thinker or loop-breaker."),
   (', "what do you have for this"', ""),
 ],
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
for skill, subs in SUBS.items():
    p = ROOT / skill / "SKILL.md"
    original = p.read_text(encoding="utf-8")
    m = re.search(r"^---\n(.*?)\n---", original, re.S)
    fm = m.group(1)
    span = DESC_SPAN.search(fm + "\n")
    cur = norm(re.sub(r"^description:\s*>?-?\s*", "", span.group(0), count=1))
    before = len(cur)
    miss = [o for o, _ in subs if norm(o) not in cur]
    if miss:
        results.append((skill, "FAIL", f"text not found: {miss[0][:40]!r}")); continue
    for old, new in subs:
        cur = norm(cur.replace(norm(old), new, 1))
    if LIMIT - len(cur) < MIN_HEADROOM:
        results.append((skill, "BLOCK", f"{len(cur)} chars, {LIMIT-len(cur)} headroom")); continue

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
    print(f"{st:5s} {s:14s}  {msg}")
print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: "
      f"{sum(1 for r in results if r[1]=='OK')} ok, "
      f"{sum(1 for r in results if r[1]!='OK')} not applied")
if not APPLY:
    print("re-run with --apply to write")
sys.exit(0 if all(r[1] == "OK" for r in results) else 1)
