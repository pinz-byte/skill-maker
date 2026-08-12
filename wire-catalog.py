#!/usr/bin/env python3
"""
wire-catalog.py -- one-shot, idempotent wiring for the intent catalog. 2026-08-12

Does two things and verifies both:

1. CLAUDE.md         adds `@CATALOG.md` beside `@DISPATCH_INBOX.md`, so the intent
                     index loads on turn one of every session. This is the payload --
                     without it the catalog exists but is never read.

2. build-marketplace.py
                     appends a _post_build() hook that REGENERATES CATALOG.md after
                     every build, closing the staleness hole (CATALOG.md went stale
                     within one commit of being created).

DELIBERATELY NOT WIRED: `skill-intent-audit.py check` as a build failure. Seven lots
currently fail on unpartitioned crowding; making that blocking today would break the
publish pipeline to enforce a rule not yet satisfiable. Flip it on -- change
BLOCK_ON_CHECK to True below and re-run -- once `check` exits 0.

Safe to re-run. Prints what it changed and what it found already done.
"""

import re, sys, pathlib

BLOCK_ON_CHECK = False   # flip to True once `skill-intent-audit.py check` exits 0

ROOT = pathlib.Path(__file__).resolve().parent
changed, skipped, failed = [], [], []

HOOK = '''

def _post_build():
    """Regenerate CATALOG.md so the intent index never drifts from source.
    Added 2026-08-12 by wire-catalog.py. See CATALOG.md / intent-map.tsv."""
    import subprocess, sys as _sys
    audit = ROOT / "skill-intent-audit.py"
    if not audit.exists():
        print("  (skill-intent-audit.py absent -- CATALOG.md not regenerated)")
        return
    subprocess.run([_sys.executable, str(audit), "catalog", str(ROOT)], check=False)
    if _BLOCK_ON_CHECK:
        r = subprocess.run([_sys.executable, str(audit), "check", str(ROOT)], check=False)
        if r.returncode != 0:
            raise SystemExit("build blocked: intent partition check failed")
'''

# --- 1. CLAUDE.md ------------------------------------------------------------
p = ROOT / "CLAUDE.md"
if not p.exists():
    failed.append("CLAUDE.md not found")
else:
    txt = p.read_text(encoding="utf-8")
    if "@CATALOG.md" in txt:
        skipped.append("CLAUDE.md already imports @CATALOG.md")
    elif "@DISPATCH_INBOX.md" not in txt:
        failed.append("CLAUDE.md has no @DISPATCH_INBOX.md anchor -- add @CATALOG.md by hand")
    else:
        p.write_text(txt.replace("@DISPATCH_INBOX.md",
                                 "@DISPATCH_INBOX.md\n@CATALOG.md", 1), encoding="utf-8")
        changed.append("CLAUDE.md now imports @CATALOG.md")

# --- 2. build-marketplace.py -------------------------------------------------
p = ROOT / "build-marketplace.py"
if not p.exists():
    failed.append("build-marketplace.py not found")
else:
    txt = p.read_text(encoding="utf-8")
    if "_post_build" in txt:
        skipped.append("build-marketplace.py already has the _post_build hook")
    elif not re.search(r'^if __name__ == "__main__":\s*\n\s+main\(\)', txt, re.M):
        failed.append("build-marketplace.py entrypoint not in the expected shape -- patch by hand")
    else:
        txt = txt.replace('\nif __name__ == "__main__":',
                          f'\n_BLOCK_ON_CHECK = {BLOCK_ON_CHECK}\n{HOOK}\nif __name__ == "__main__":', 1)
        txt = re.sub(r'(^if __name__ == "__main__":\s*\n\s+main\(\))',
                     r'\1\n    _post_build()', txt, count=1, flags=re.M)
        p.write_text(txt, encoding="utf-8")
        changed.append(f"build-marketplace.py regenerates CATALOG.md after build "
                       f"(check blocking = {BLOCK_ON_CHECK})")

# --- report ------------------------------------------------------------------
for c in changed:
    print("CHANGED  " + c)
for s in skipped:
    print("ALREADY  " + s)
for f in failed:
    print("FAILED   " + f)

# --- verify ------------------------------------------------------------------
print("\nverification:")
cm = (ROOT / "CLAUDE.md").read_text(encoding="utf-8") if (ROOT / "CLAUDE.md").exists() else ""
bm = (ROOT / "build-marketplace.py").read_text(encoding="utf-8") if (ROOT / "build-marketplace.py").exists() else ""
ok = True
for label, cond in [("CLAUDE.md imports @CATALOG.md", "@CATALOG.md" in cm),
                    ("build hook present", "_post_build()" in bm),
                    ("CATALOG.md exists", (ROOT / "CATALOG.md").exists())]:
    print(f"  [{'x' if cond else ' '}] {label}")
    ok = ok and cond
print("\nnext: python3 build-marketplace.py   (should regenerate CATALOG.md)")
sys.exit(0 if ok and not failed else 1)
