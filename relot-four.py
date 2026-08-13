#!/usr/bin/env python3
"""relot-four.py -- clear the last 4 partition failures.

Root cause: the gate requires the sibling named in a NOT-clause to live in the
SAME lot. Four of my clauses named a sibling in a different lot, so they read as
"names no sibling":

  cc-session-analyzer  (audit)  named work-retrospective, which landed in reason
  work-retrospective   (reason) named self-audit,         which lives in audit
  project-init         (build)  named projectmd-gen,      which landed in orient
  projectmd-gen        (orient) named projectmd-auditor,  which lives in audit

Two of those are the machine putting the skill in the wrong lot, not the clause
being wrong. Fixing the lots fixes three of the four for free:

  work-retrospective: reason -> audit
      A post-work audit belongs with self-audit and auditor-general, not with
      critical-thinker. This validates BOTH its own clause (names self-audit,
      now same lot) AND cc-session-analyzer's (names work-retrospective).

  projectmd-gen: orient -> build
      It generates a file; it does not orient a session. This validates
      project-init's clause (names projectmd-gen, now same lot).

Only projectmd-gen still needs a new clause, pointing at its build lot-mate.

Run from the SKILL MAKER repo root:

    python3 relot-four.py
    ./publish.sh

Backs up each touched file to SKILL.md.bak4. Verifies every rewrite re-parses
and stays under 1000 chars.
"""
import os
import re
import shutil
import sys

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not available. pip3 install pyyaml")

ROOT = os.path.abspath(os.path.dirname(__file__))
CEILING = 1000

RELOT = {
    "work-retrospective": "audit",
    "projectmd-gen": "build",
}

# skill -> (text to find at the start of the stale clause, replacement clause)
RECLAUSE = {
    "projectmd-gen": (
        "NOT projectmd-auditor",
        "NOT project-init (scaffolds the whole .claude/ directory -- hooks, agent "
        "config and rules): this only scans a project and writes its CLAUDE.md.",
    ),
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


def set_intent(fm, lot):
    if re.search(r"^\s*intent:", fm, re.M):
        return re.sub(r"^(\s*)intent:.*$", rf"\g<1>intent: {lot}", fm, count=1, flags=re.M)
    if re.search(r"^metadata:\s*$", fm, re.M):
        return re.sub(r"^metadata:\s*$", f"metadata:\n  intent: {lot}", fm, count=1, flags=re.M)
    return fm.rstrip() + f"\nmetadata:\n  intent: {lot}"


def rewrite_desc(fm, marker, clause):
    span = desc_span(fm)
    if not span:
        return None, "no description key"
    try:
        text = str(yaml.safe_load(fm).get("description", ""))
    except Exception as e:
        return None, f"unparseable before edit: {str(e).splitlines()[0]}"
    i = text.find(marker)
    if i < 0:
        return None, f"marker {marker!r} not present"
    new_text = (text[:i] + clause).strip()
    if len(new_text) > CEILING:
        return None, f"would be {len(new_text)} chars"
    import textwrap
    block = "description: >-\n" + "\n".join(
        "  " + l for l in textwrap.wrap(new_text, width=92))
    s, e = span
    return fm[:s] + block + fm[e:], len(new_text)


def main():
    touched = []
    for name in sorted(set(RELOT) | set(RECLAUSE)):
        path = os.path.join(ROOT, name, "SKILL.md")
        if not os.path.isfile(path):
            print(f"  MISSING {name}/SKILL.md")
            return 1
        raw = open(path, encoding="utf-8").read()
        fm, body = split_fm(raw)
        if fm is None:
            print(f"  NO FRONTMATTER {name}")
            return 1
        notes = []
        if name in RELOT:
            fm = set_intent(fm, RELOT[name])
            notes.append(f"intent -> {RELOT[name]}")
        if name in RECLAUSE:
            marker, clause = RECLAUSE[name]
            new_fm, info = rewrite_desc(fm, marker, clause)
            if new_fm is None:
                print(f"  FAILED {name}: {info}")
                return 1
            fm = new_fm
            notes.append(f"clause rewritten ({info} chars)")
        try:
            yaml.safe_load(fm)
        except Exception as e:
            print(f"  FAILED {name}: result does not parse: {str(e).splitlines()[0]}")
            return 1
        shutil.copy2(path, path + ".bak4")
        open(path, "w", encoding="utf-8").write(f"---\n{fm}\n---\n{body}")
        touched.append((name, ", ".join(notes)))

    for n, note in touched:
        print(f"  {n:<20} {note}")
    print("\nExpected effect on the gate:")
    print("  audit/cc-session-analyzer  -> its clause now names a same-lot sibling")
    print("  reason/work-retrospective  -> moved to audit, its clause names self-audit")
    print("  build/project-init         -> its clause now names a same-lot sibling")
    print("  build/projectmd-gen        -> new clause names project-init")
    print("\nBackups: SKILL.md.bak4\n\nNEXT:\n  ./publish.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
