#!/usr/bin/env python3
"""
fix-dead-ledger-refs.py -- repoint /pm at the live Focus Queue.  2026-08-12

FOUND BY POPs, not by the gate. The TASKMASTER Dispatch Ledger
(7793b007e55740859c9738e51274e29f) was archived 2026-07-03 -- its Notion title
is literally "TASKMASTER -- Dispatch Ledger (ARCHIVED 2026-07-03 -- see Focus
Queue)". /pm has pointed at it for 40 days while calling it "the single source
of truth". arise/SKILL.md already reads the live Focus Queue, so the ecosystem
migrated and /pm was the one skill left behind.

Verified live via Notion MCP before writing anything:
  DEAD  db 7793b007-e557-4085-9c97-38e51274e29f
        title property "Task"; Status: Pending|Enviado|En proceso|Respondido|
        Resuelto|Stale
  LIVE  db cd49d2c6-f9d6-40af-bacb-d9662e3323d6  "Focus Queue"
        data source collection://b5c3c737-1219-4888-a081-bbfde500e180
        title property "Item"; Status: Open|In Progress|Waiting|Done|Deferred
        also: Priority, Next Action, Why It Matters, Due Date, Last Touched,
        Assignee (incl. "SKILL MAKER"), Domain, Origin, Source

The schemas are INCOMPATIBLE, so an ID swap alone would leave /pm broken: it
excludes status "Resuelto" and closes rows as "Respondido / Resuelto", none of
which exist in Focus Queue. Every operational instruction is rewritten.

Third dead dependency: tools/ledger_operator.py in pops-symbios. Neither the
file nor the repo exists anywhere under $HOME. The reference is removed rather
than repointed -- do not invent a replacement.

Also fixes space-steward, whose description and body name the dead Ledger in
four places when describing /pm's store.

Run: python3 fix-dead-ledger-refs.py [--apply]
"""

import sys, re, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent
APPLY = "--apply" in sys.argv
LIMIT = 1024

DESC_SUBS = {
 "pm": [
   ("The per-project PM reads the TASKMASTER Dispatch Ledger filtered to THIS project"
    " (Assignee = project)",
    "The per-project PM reads the Focus Queue filtered to THIS project (Assignee = project)"),
   ("closes finished dispatched tasks in the Ledger. It rides the Ledger spine -- no"
    " separate board, no parallel store.",
    "closes finished tasks there. It rides the Focus Queue spine -- no separate board,"
    " no parallel store."),
   ("Pairs with the central Ledger Operator (tools/ledger_operator.py in pops-symbios),"
    " which is the cross-project roll-up.",
    "The Focus Queue itself is the cross-project roll-up."),
 ],
 "space-steward": [
   ("NOT /pm - that reads the Dispatch Ledger (work-task state)",
    "NOT /pm - that reads the Focus Queue (work-task state)"),
 ],
}

BODY_SUBS = {
 "pm": [
   ("You ride the TASKMASTER Dispatch Ledger -- there is no separate\nper-project board to maintain.",
    "You ride the Focus Queue -- there is no separate\nper-project board to maintain."),
   ("""1. Read this project's rows from the TASKMASTER Dispatch Ledger
   (DB 7793b007e55740859c9738e51274e29f, filter Assignee = <this project>), excluding
   terminal status Resuelto.""",
    """1. Read this project's rows from the Focus Queue
   (db cd49d2c6-f9d6-40af-bacb-d9662e3323d6, data source
   collection://b5c3c737-1219-4888-a081-bbfde500e180), filter Assignee = <this project>,
   excluding terminal status Done and Deferred. Title property is `Item`, not `Task`."""),
   ("""2. Brief POPs in one breath, blockers first: Current focus / Blocked (what's stuck and on what) /
   Open / In progress / Recently closed.""",
    """2. Brief POPs in one breath, blockers first: Waiting (what's stuck and on what) /
   In Progress / Open / Recently Done. Lead each item with Priority; carry `Next Action`
   verbatim -- it is the row's whole point. Surface `Due Date` when set, and flag any row
   whose `Last Touched` has gone quiet."""),
   ("3. Honest band: if the Ledger read fails, say so",
    "3. Honest band: if the Focus Queue read fails, say so"),
   ("""- When a dispatched task for this project is finished, close it in the Ledger (Status
  Respondido / Resuelto) so the central Ledger Operator stops flagging it stalled.""",
    """- When a task for this project is finished, set Status = Done. Use Deferred when it is
  parked deliberately, Waiting when it is blocked on something external -- never leave a
  finished row Open."""),
   ("- This chat = the project's exclusive PM, sourced from the Ledger.\n"
    "- Cross-project view: tools/ledger_operator.py (pops-symbios) -> #lattice-01, read between sessions.\n"
    "- Task spine: the TASKMASTER Dispatch Ledger (single source of truth). No PROJECT_STATE.md.",
    "- This chat = the project's exclusive PM, sourced from the Focus Queue.\n"
    "- Cross-project view: the Focus Queue unfiltered -- it spans every project already.\n"
    "- Task spine: the Focus Queue (single source of truth). No PROJECT_STATE.md.\n"
    "- Superseded 2026-07-03: the TASKMASTER Dispatch Ledger (7793b007...) is ARCHIVED.\n"
    "  Never read or write it. `tools/ledger_operator.py` no longer exists."),
 ],
 "space-steward": [
   ("Work-task state lives in the Dispatch Ledger and is `/pm`'s",
    "Work-task state lives in the Focus Queue and is `/pm`'s"),
   ("Never the Dispatch Ledger (that is /pm).", "Never the Focus Queue (that is /pm)."),
   ("- `/pm` - work-task state from the Dispatch Ledger.",
    "- `/pm` - work-task state from the Focus Queue."),
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


results = []
for skill in sorted(set(DESC_SUBS) | set(BODY_SUBS)):
    p = ROOT / skill / "SKILL.md"
    original = p.read_text(encoding="utf-8")
    m = re.search(r"^---\n(.*?)\n---", original, re.S)
    fm, rest = m.group(1), original[m.end():]

    span = DESC_SPAN.search(fm + "\n")
    desc = norm(re.sub(r"^description:\s*>?-?\s*", "", span.group(0), count=1))
    before = len(desc)
    for old, new in DESC_SUBS.get(skill, []):
        if norm(old) not in desc:
            results.append((skill, "FAIL", f"desc text not found: {old[:44]!r}")); break
        desc = norm(desc.replace(norm(old), new, 1))
    else:
        for old, new in BODY_SUBS.get(skill, []):
            if old not in rest:
                results.append((skill, "FAIL", f"body text not found: {old[:44]!r}")); break
            rest = rest.replace(old, new, 1)
        else:
            if len(desc) > LIMIT:
                results.append((skill, "FAIL", f"desc {len(desc)} > {LIMIT}")); continue
            new_fm = fm[:span.start()] + emit(desc) + fm[span.end():]
            new_txt = original[:m.start()] + "---\n" + new_fm.rstrip("\n") + "\n---" + rest
            try:
                parsed = yaml.safe_load(re.search(r"^---\n(.*?)\n---", new_txt, re.S).group(1))
            except Exception as e:
                results.append((skill, "FAIL", f"YAML would break: {e}")); continue
            if norm(parsed.get("description", "")) != desc:
                results.append((skill, "FAIL", "round-trip mismatch")); continue
            if (parsed.get("metadata") or {}).get("intent") is None:
                results.append((skill, "FAIL", "intent lost")); continue
            # Dead identifiers are legal ONLY inside the explicit tombstone note that
            # tells a reader never to use them. Strip the tombstone, then scan: anything
            # left is a live reference to a corpse.
            scan = re.sub(r"- Superseded 2026-07-03:.*?(?=\n- |\n#|\Z)", "",
                          new_txt, flags=re.S)
            dead = sorted(set(re.findall(
                r"7793b007|Dispatch Ledger|ledger_operator|Respondido|Resuelto", scan)))
            if dead:
                results.append((skill, "FAIL",
                                f"live refs to dead spine remain: {dead}")); continue
            if APPLY:
                p.write_text(new_txt, encoding="utf-8")
            results.append((skill, "OK",
                            f"desc {before}->{len(desc)} ({LIMIT-len(desc)} headroom), "
                            f"{len(BODY_SUBS.get(skill,[]))} body edits"))

for s, st, msg in results:
    print(f"{st:5s} {s:16s}  {msg}")
print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: {sum(1 for r in results if r[1]=='OK')}/2 ok")
if not APPLY:
    print("re-run with --apply to write")
sys.exit(0 if all(r[1] == "OK" for r in results) else 1)
