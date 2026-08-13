#!/usr/bin/env python3
"""fix-frontmatter.py -- repair SKILL.md frontmatter broken by a colon in a plain scalar.

Cause: partition-newcomers.py appended clauses of the form
"NOT x (reason): this does y." A colon-space inside a PLAIN (unquoted) YAML
scalar is illegal -- YAML reads it as a mapping. Descriptions that were block
scalars (`>`/`|`) or quoted absorbed it fine; plain ones did not.

Fix: for every SKILL.md whose frontmatter fails to parse, re-emit its
`description` as a folded block scalar (`>-`), preserving the text verbatim.
Colons are legal there.

Run from the SKILL MAKER repo root:

    python3 fix-frontmatter.py          # report only
    python3 fix-frontmatter.py --apply  # write the fixes

Only touches files that FAIL to parse. Verifies each file re-parses after the
rewrite and reverts that single file if it does not.
"""
import os
import re
import sys
import textwrap

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not available. pip3 install pyyaml")

ROOT = os.path.abspath(os.path.dirname(__file__))
SKIP_DIRS = {"plugins", "rescued", ".git", ".claude", "node_modules", "__pycache__"}
APPLY = "--apply" in sys.argv
WRAP = 92


def skill_files():
    for d in sorted(os.listdir(ROOT)):
        if d in SKIP_DIRS or d.startswith(".") or not os.path.isdir(os.path.join(ROOT, d)):
            continue
        p = os.path.join(ROOT, d, "SKILL.md")
        if os.path.isfile(p):
            yield d, p


def split_fm(txt):
    m = re.match(r"^---\n(.*?)\n---\n?", txt, re.S)
    return (m.group(1), txt[m.end():]) if m else (None, None)


def parses(fm):
    try:
        yaml.safe_load(fm)
        return True, None
    except Exception as e:
        return False, str(e).split("\n")[0]


def desc_span(fm):
    m = re.search(r"^description:", fm, re.M)
    if not m:
        return None
    rest = fm[m.end():]
    nxt = re.search(r"\n(?=[A-Za-z_][A-Za-z0-9_-]*:)", rest)
    return m.start(), m.end() + (nxt.start() if nxt else len(rest))


def to_block(fm):
    span = desc_span(fm)
    if not span:
        return None, "no description key"
    s, e = span
    block = fm[s:e]
    raw = block[len("description:"):]
    raw = re.sub(r"^\s*[>|][-+]?\s*\n?", " ", raw, count=1)
    text = " ".join(raw.split())
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    text = text.replace('\\"', '"')
    lines = textwrap.wrap(text, width=WRAP) or [""]
    new = "description: >-\n" + "\n".join("  " + l for l in lines)
    return fm[:s] + new + fm[e:], len(text)


def main():
    broken, fixed, failed, longdesc = [], [], [], []
    for name, path in skill_files():
        txt = open(path, encoding="utf-8").read()
        fm, body = split_fm(txt)
        if fm is None:
            continue
        ok, err = parses(fm)
        if ok:
            d = yaml.safe_load(fm).get("description") or ""
            if len(str(d)) > 900:
                longdesc.append((name, len(str(d))))
            continue
        broken.append((name, err))
        if not APPLY:
            continue
        new_fm, info = to_block(fm)
        if new_fm is None:
            failed.append((name, info))
            continue
        ok2, err2 = parses(new_fm)
        if not ok2:
            failed.append((name, f"still invalid after rewrite: {err2}"))
            continue
        open(path, "w", encoding="utf-8").write(f"---\n{new_fm}\n---\n{body}")
        fixed.append((name, info))
        if info > 900:
            longdesc.append((name, info))

    print(f"scanned {len(list(skill_files()))} top-level SKILL.md")
    print(f"broken frontmatter: {len(broken)}")
    for n, e in broken:
        print(f"  {n}: {e}")
    if not APPLY:
        print("\nreport only -- re-run with --apply to rewrite these as block scalars.")
        return 0
    print(f"\nfixed: {len(fixed)}")
    for n, ln in fixed:
        print(f"  {n}  ({ln} chars)")
    if failed:
        print(f"\nCOULD NOT FIX ({len(failed)}) -- these need a hand edit:")
        for n, why in failed:
            print(f"  {n}: {why}")
    if longdesc:
        print(f"\nWARN description over 900 chars (1024 is the silent-failure limit):")
        for n, ln in sorted(longdesc, key=lambda x: -x[1]):
            print(f"  {n}: {ln}")
    print("\nNEXT:\n  ./publish.sh")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
