#!/usr/bin/env python3
"""
gen-inbox-registry.py -- single-source the inbox UUID registry.

Canonical source: .claude/rules/inbox-registry.md ("## Current inbox registry" table).
Generated copy:   agent-bridge/SKILL.md (block between INBOX_REGISTRY markers).

The agent-bridge plugin ships standalone, so it must EMBED the registry -- but the
embedded table is GENERATED from canonical, never hand-edited. build-marketplace.py
runs this automatically before packaging. Fails loud if the markers are missing.

Usage:
  python3 gen-inbox-registry.py          # regenerate the embedded table from canonical
  python3 gen-inbox-registry.py --check  # exit nonzero if out of sync; write nothing (CI guard)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CANON = ROOT / ".claude" / "rules" / "inbox-registry.md"
TARGET = ROOT / "agent-bridge" / "SKILL.md"

START = ("<!-- INBOX_REGISTRY:START (generated from .claude/rules/inbox-registry.md "
         "-- run gen-inbox-registry.py; do not edit by hand) -->")
END = "<!-- INBOX_REGISTRY:END -->"
SPAN = re.compile(r"<!-- INBOX_REGISTRY:START.*?<!-- INBOX_REGISTRY:END -->", re.DOTALL)


def parse_canonical(text):
    """Return [(project, host, uuid)] from the canonical registry table."""
    table = []
    grabbing = False
    for ln in text.splitlines():
        if ln.strip().startswith("## Current inbox registry"):
            grabbing = True
            continue
        if grabbing:
            if ln.strip().startswith("|"):
                table.append(ln.strip())
            elif table:
                break  # table ended
    rows = []
    for line in table:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        proj, host, uuid = cells[0], cells[1], cells[2].strip("`")
        if proj.lower() == "project":        # header row
            continue
        if set(proj) <= set("-: "):          # separator row
            continue
        rows.append((proj, host, uuid))
    return rows


def render(rows):
    out = ["| Project | Host | Notion Inbox UUID |", "|---|---|---|"]
    out += [f"| {p} | {h} | `{u}` |" for p, h, u in rows]
    return "\n".join(out)


def main():
    check = "--check" in sys.argv[1:]
    rows = parse_canonical(CANON.read_text())
    if not rows:
        sys.exit(f"ERROR: parsed 0 rows from canonical registry: {CANON}")

    block = f"{START}\n{render(rows)}\n{END}"
    target = TARGET.read_text()
    new, n = SPAN.subn(lambda _m: block, target)
    if n == 0:
        sys.exit(f"ERROR: INBOX_REGISTRY markers not found in {TARGET}. "
                 "Add the START/END markers around the table, then re-run.")
    if n > 1:
        sys.exit(f"ERROR: found {n} INBOX_REGISTRY marker spans in {TARGET}; expected 1.")

    if new == target:
        print(f"inbox registry in sync ({len(rows)} entries) -- no change")
        return
    if check:
        sys.exit("ERROR: agent-bridge inbox registry is OUT OF SYNC with canonical. "
                 "Run: python3 gen-inbox-registry.py")
    TARGET.write_text(new)
    print(f"regenerated agent-bridge inbox registry from canonical ({len(rows)} entries)")


if __name__ == "__main__":
    main()
