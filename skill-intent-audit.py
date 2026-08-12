#!/usr/bin/env python3
"""
skill-intent-audit.py -- intent partitioning for the SKILL MAKER catalog.  v2 2026-08-12

v2 changes (v1 shipped a gate that was red 100% of the time -- the exact
herald-config-doctor anti-pattern: detects forever, never goes green, masks real
regressions):
  * severity split: only UNPARTITIONED CROWDING fails the build. Unassigned intent
    and long descriptions are warnings.
  * description cap demoted to a warning at 900 (near the real 1024 silent-failure
    limit) instead of an asserted 600 that every skill failed.
  * new `assign` command: writes `metadata: intent: <lot>` into all 52 SKILL.md
    files so the migration is one command, not 52 hand-edits.
  * plugin grouping used as a prior -- lfp-thinkers/lfp-copy/lfp-apex already
    encode intent and v1 ignored that signal.

Problem it solves
-----------------
Skill descriptions are BIDS in an auction for the user's intent. Raising a bid
(longer description, more trigger phrases) stops working once many skills bid on
the same concept. Measured 2026-08-12: 26 of 52 skills claim "session", 23 claim
"check", 20 claim "project"; 33 descriptions sit within 124 chars of the 1024
silent-failure ceiling. The bidding strategy is exhausted.

The fix is a LOT TAXONOMY: partition intent space so each intent has one obvious
owner, and make crowding legal only when explicitly partitioned.

Commands
--------
  catalog          write CATALOG.md -- intent-first index, meant to be @-imported
                   by CLAUDE.md so "do we have a skill for X" is answered before
                   it is asked.
  check            exit 1 ONLY on unpartitioned crowding. Wire beside the GROUPS
                   guard in build-marketplace.py.
  assign           show proposed intent per skill (dry run).
  assign --apply   write them into frontmatter.
"""

import sys, re, glob, os, datetime, collections

WARN_CAP = 900          # hard silent-failure limit is 1024
SKIP_DIRS = {"plugins", "team-skills", "shared", "docs", "tools",
             "automation", "team-toolkit", "reentry-workspace", "__pycache__"}

# The closed vocabulary. Phrased as what the USER WANTS, not what the skill is.
LOTS = [
    ("orient",   "load context, resume, figure out where we are",
     ["resume", "continuity", "seed", "reentry", "handoff", "orient", "bootstrap",
      "summon", "arise", "cold", "session start", "where are we"]),
    ("manage",   "see what's open, blocked, owed -- track work",
     ["ledger", "dispatch", "project manager", "backlog", "roadmap", "assignee",
      "blocked", "open tasks", "what's open", "prioriti"]),
    ("decide",   "get a verdict on a position, ticker, or option",
     ["council", "verdict", "ticker", "asymmetry", "trade", "go / near-miss",
      "deliberate", "voices"]),
    ("observe",  "read live system state right now",
     ["snapshot", "live state", "freshness", "pipeline status", "health",
      "read-only status", "intel", "monitor", "is it running"]),
    ("diagnose", "something is broken -- find and fix the cause",
     ["broken", "failure", "error", "permission denied", "drift", "remediat",
      "doctor", "resolver", "stale path", "disk", "denied"]),
    ("audit",    "verify something already built or already claimed",
     ["audit", "verify", "validate", "post-hoc", "independent", "examiner",
      "did it land", "evidence", "qa", "gate", "pre-flight"]),
    ("build",    "make, publish, or ship an artifact",
     ["publish", "marketplace", "scaffold", "generate a skill", "ship",
      "deploy", "package", "author", "create a plugin", "surface friction"]),
    ("relay",    "move information between agents, projects, or people",
     ["inbox", "message", "mail", "bridge", "forward", "notify", "send to",
      "cross-project", "handover", "onboard"]),
    ("write",    "produce or convert prose, copy, documents",
     ["copy", "tone", "prose", "listing", "email", "landing", "persuas",
      "rewrite", "descripcion", "correo", "language system"]),
    ("reason",   "think harder, break a loop, stress-test an idea",
     ["think", "reason", "critique", "brainstorm", "loop", "logic",
      "counterargument", "stress-test", "router", "perspective"]),
    ("hygiene",  "keep files, context, disk, and history disciplined",
     ["hygiene", "stale", "cleanup", "bare name", "commit message", "git log",
      "steward", "dated header", "space", "compress"]),
    ("delegate", "hand work to a cheaper model, another agent, or another tool",
     ["subagent", "cheaper", "sonnet", "haiku", "delegat", "offload", "hand off to"]),
]
LOT_NAMES = {l[0] for l in LOTS}

# Plugin grouping already encodes intent. Use it as a strong prior.
PLUGIN_PRIOR = {"lfp-thinkers": "reason", "lfp-copy": "write", "lfp-apex": "decide"}
PLUGIN_EXCEPT = {"apex-builder-gate": "audit"}

def names_a_sibling(desc, me, lotmates):
    """A description is disambiguated when it NAMES another skill in its own lot.

    This replaces a prose-pattern regex (\\bNOT\\b|pairs with|...) that measured
    writing style rather than meaning: it missed logic-thinker's "For attacking an
    idea use critical-thinker", vmc-listing-copy's Spanish "Distinto de
    patel-tone-converter", and would pass a description that said "NOT" about
    nothing. Naming the sibling is the invariant that actually partitions intent.
    """
    for other in lotmates:
        if other == me:
            continue
        pat = r"[\s\-_]?".join(re.escape(w) for w in other.split("-")) + r"s?\b"
        if re.search(pat, desc, re.I):
            return True
    return False


def plugin_map(root="."):
    m = {}
    for p in glob.glob(os.path.join(root, "plugins/*/skills/*/")):
        parts = os.path.normpath(p).split(os.sep)
        m[parts[-1]] = parts[-3]
    return m


def parse(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"^---\n(.*?)\n---", txt, re.S)
    fm = m.group(1) if m else ""
    dm = re.search(r"description:\s*>?\s*\n?(.*?)(?=\n[a-z_]+:\s|\Z)", fm, re.S)
    desc = " ".join((dm.group(1) if dm else "").split())
    im = re.search(r"^\s*intent:\s*([a-z]+)\s*$", fm, re.M)
    return txt, fm, desc, (im.group(1) if im else None)


def infer(desc, d, pmap):
    """Returns (lot, confidence) -- confidence in {'plugin','high','low',None}."""
    if d in PLUGIN_EXCEPT:
        return PLUGIN_EXCEPT[d], "plugin"
    pl = pmap.get(d)
    if pl in PLUGIN_PRIOR:
        return PLUGIN_PRIOR[pl], "plugin"
    low = desc.lower()
    scored = []
    for lot, _, kws in LOTS:
        s = sum(3 if k in low[:220] else 1 for k in kws if k in low)
        if s:
            scored.append((s, lot))
    if not scored:
        return None, None
    scored.sort(reverse=True)
    if len(scored) > 1 and scored[0][0] - scored[1][0] <= 1:
        return scored[0][1], "low"
    return scored[0][1], "high"


def gloss(desc, n=76):
    g = re.split(r"(?<=[a-z])\.\s|\s--\s|\.\s+Use\s|\.\s+Trigger\s", desc)[0]
    g = re.sub(r"^(Use this skill\s+)?", "", g).strip().rstrip(".,|").strip("| ")
    return g if len(g) <= n else g[:n].rsplit(" ", 1)[0] + "..."


def load_map(root="."):
    """Hand-adjudicated lots from intent-map.tsv. Beats keyword inference."""
    p = os.path.join(root, "intent-map.tsv")
    m = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.startswith("#") or not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) >= 2 and f[1].strip():
                m[f[0].strip()] = f[1].strip()
    return m


def load(root="."):
    pmap = plugin_map(root)
    hand = load_map(root)
    out = []
    for p in sorted(glob.glob(os.path.join(root, "*/SKILL.md"))):
        d = os.path.basename(os.path.dirname(p))
        if d in SKIP_DIRS or d.startswith("."):
            continue
        txt, fm, desc, declared = parse(p)
        if d in hand:
            lot, conf = hand[d], "hand"
        else:
            lot, conf = infer(desc, d, pmap)
        out.append(dict(dir=d, path=p, desc=desc, declared=declared,
                        lot=declared or lot or "unsorted", conf=conf,
                        plugin=pmap.get(d, "-"), disambig=False))
    lots = collections.defaultdict(list)
    for s in out:
        lots[s["lot"]].append(s["dir"])
    for s in out:
        s["disambig"] = names_a_sibling(s["desc"], s["dir"], lots[s["lot"]])
    return out


def cmd_catalog(skills, root="."):
    by = collections.defaultdict(list)
    for s in skills:
        by[s["lot"]].append(s)
    L = ["# SKILL CATALOG", "",
         f"Generated {datetime.date.today().isoformat()} by skill-intent-audit.py "
         f"from {len(skills)} SKILL.md files.",
         "DO NOT HAND-EDIT. Regenerate: python3 skill-intent-audit.py catalog", "",
         "Indexed by INTENT -- what you want, not what the skill is called.",
         "A trailing ? means the lot was auto-inferred, not yet declared in frontmatter.", ""]
    for lot, blurb, _ in LOTS + [("unsorted", "no lot inferred -- assign one", [])]:
        rows = by.get(lot, [])
        if not rows:
            continue
        L += [f"## {lot.upper()} -- {blurb}", ""]
        w = max(len(r["dir"]) for r in rows)
        for r in sorted(rows, key=lambda x: x["dir"]):
            mark = "" if r["declared"] else " ?"
            L.append(f"- `{r['dir']}`{mark}{' ' * (w - len(r['dir']))}  {gloss(r['desc'])}")
        L.append("")
    open(os.path.join(root, "CATALOG.md"), "w", encoding="utf-8").write(
        "\n".join(L).encode("ascii", "ignore").decode())
    print(f"wrote CATALOG.md -- {len(skills)} skills across {len(by)} lots")
    return 0


def cmd_check(skills):
    fails, warns = [], []
    by = collections.defaultdict(list)
    for s in skills:
        by[s["lot"]].append(s)
    for lot, rows in sorted(by.items()):
        naked = [r["dir"] for r in rows if not r["disambig"]]
        if len(rows) > 1 and len(naked) > 1:
            fails.append(f"lot '{lot}': {len(rows)} skills, {len(naked)} with no "
                         f"disambiguation clause -> {', '.join(sorted(naked))}")
    un = sorted(s["dir"] for s in skills if not s["declared"])
    if un:
        warns.append(f"{len(un)}/{len(skills)} skills have no declared intent "
                     f"(run: skill-intent-audit.py assign --apply)")
    fat = sorted(((len(s["desc"]), s["dir"]) for s in skills if len(s["desc"]) > WARN_CAP),
                 reverse=True)
    if fat:
        warns.append(f"{len(fat)} descriptions over {WARN_CAP} chars, approaching the "
                     f"1024 silent-failure limit: "
                     + ", ".join(f"{d}={n}" for n, d in fat[:5]))
    for w in warns:
        print("WARN  " + w)
    if not fails:
        print(f"PASS  {len(skills)} skills, every crowded lot is partitioned.")
        return 0
    print("")
    for f in fails:
        print("FAIL  " + f)
    print("\nCrowding is legal. UNPARTITIONED crowding is not: give each skill in a")
    print("shared lot an explicit 'NOT x / use y instead' clause, or merge them.")
    return 1


def cmd_assign(skills, apply=False):
    todo = [s for s in skills if not s["declared"]]
    print(f"{len(todo)} skills to assign  (mode: {'APPLY' if apply else 'DRY RUN'})\n")
    lowconf, unsorted_ = [], []
    for s in sorted(todo, key=lambda x: (x["lot"], x["dir"])):
        flag = {"hand": "", "plugin": "  [plugin prior]",
                "low": "  [LOW CONFIDENCE - review]",
                "high": "  [keyword guess - review]", None: "  [NO MATCH]"}[s["conf"]]
        print(f"  {s['lot']:9s} <- {s['dir']:26s}{flag}")
        if s["conf"] == "low":
            lowconf.append(s["dir"])
        if s["lot"] == "unsorted":
            unsorted_.append(s["dir"])
    if not apply:
        print(f"\n{len(lowconf)} low-confidence, {len(unsorted_)} unsorted. "
              f"Re-run with --apply to write.")
        return 0
    n = 0
    for s in todo:
        if s["lot"] == "unsorted":
            continue
        txt = open(s["path"], encoding="utf-8").read()
        m = re.search(r"^---\n(.*?)\n---", txt, re.S)
        if not m:
            print(f"  SKIP (no frontmatter): {s['dir']}")
            continue
        fm = m.group(1)
        if re.search(r"^\s*intent:", fm, re.M):
            continue
        if re.search(r"^metadata:\s*$", fm, re.M):
            new_fm = re.sub(r"^metadata:\s*$", f"metadata:\n  intent: {s['lot']}",
                            fm, count=1, flags=re.M)
        else:
            new_fm = fm.rstrip() + f"\nmetadata:\n  intent: {s['lot']}"
        open(s["path"], "w", encoding="utf-8").write(
            txt[:m.start()] + "---\n" + new_fm + "\n---" + txt[m.end():])
        n += 1
    print(f"\nwrote intent into {n} SKILL.md files. "
          f"{len(unsorted_)} left unsorted for you to decide: {', '.join(unsorted_) or '-'}")
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    apply = "--apply" in argv
    argv = [a for a in argv if not a.startswith("--")]
    cmd = argv[0] if argv else "catalog"
    root = argv[1] if len(argv) > 1 else "."
    sk = load(root)
    if not sk:
        print(f"no SKILL.md found under {os.path.abspath(root)}")
        sys.exit(2)
    sys.exit({"catalog": lambda: cmd_catalog(sk, root),
              "check": lambda: cmd_check(sk),
              "assign": lambda: cmd_assign(sk, apply)}.get(cmd, lambda: cmd_catalog(sk, root))())
