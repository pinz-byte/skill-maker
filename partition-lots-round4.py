#!/usr/bin/env python3
"""
partition-lots-round4.py -- the last two.  2026-08-12

The strict gate (TRIM_DEBT version) exposed apex-ultra-council and
inpositive-language, which the earlier permissive "at most one naked per lot"
rule had been hiding. Both fixed by editing text that already exists rather than
appending:

  apex-ultra-council  already ends "use \"council\" instead" -- council is a real
                      skill but NOT a lot-mate. Point it at council-global, which
                      is. Shorter than the original, so headroom improves.
  inpositive-language 1023/1024 -- no room at all. The 3-step mechanism is
                      documented 16 times over in the body, so it comes out of the
                      description (guarded) and a clause goes in.
"""

import sys, re, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent
APPLY = "--apply" in sys.argv
LIMIT, MIN_HEADROOM = 1024, 40

# skill -> (list_of_(old,new)_substitutions, body_guard_keyword_or_None)
PLAN = {
 "apex-ultra-council": ([
   ('If the user just wants today\'s cached tiers, use "council" instead.',
    'For cached tiers use council-global instead.'),
 ], None),
 "inpositive-language": ([
   (" Runs a 3-step edit pass: (1) flag negation and limiting words (no, not, don't,"
    " can't, never, impossible, problem, fail, lack, difficult, worry, struggle);"
    " (2) reframe each flag into an affirmative statement with the same factual meaning;"
    " (3) polish for tone (ambitious, resilient, optimistic).", ""),
   ("Preserves negation required for legal, safety, or factual accuracy -- flags those"
    " instead of rewriting.",
    "Preserves negation required for legal, safety, or factual accuracy. NOT"
    " patel-tone-converter (persuasive rewrite): this enforces affirmative framing."),
 ], "reframe"),
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
        results.append((skill, "FAIL", f"text not found: {miss[0][:45]!r}")); continue
    for old, new in subs:
        cur = norm(cur.replace(norm(old), new, 1))
    if LIMIT - len(cur) < MIN_HEADROOM:
        results.append((skill, "BLOCK", f"{len(cur)}, only {LIMIT-len(cur)} headroom")); continue

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
    print(f"{st:5s} {s:20s}  {msg}")
print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: {sum(1 for r in results if r[1]=='OK')} ok")
if not APPLY:
    print("re-run with --apply to write")
sys.exit(0 if all(r[1] == "OK" for r in results) else 1)
