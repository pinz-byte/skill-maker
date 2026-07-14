#!/usr/bin/env python3
"""
preflight.py -- SKILL MAKER publish pre-flight + native publish runner.

Read-only checks always run. Write actions (transliteration, ./publish.sh) only
happen when NOT running inside the Cowork sandbox mount -- the sandbox mount
blocks unlink/rmtree and .git/index.lock writes in this repo, so
build-marketplace.py and publish.sh must run natively on M2.

Usage:
    python3 skillmaker-publish/references/preflight.py            # check only
    python3 skillmaker-publish/references/preflight.py --fix       # + transliterate non-ASCII in place
    python3 skillmaker-publish/references/preflight.py --publish   # + run ./publish.sh (native only)
"""
import re
import sys
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # references/ -> skillmaker-publish/ -> repo root
BUILD_MP = ROOT / "build-marketplace.py"
SANDBOXED = str(ROOT).startswith("/sessions/")


def load_build_marketplace_globals():
    """Exec build-marketplace.py up to `def main():` to get the live GROUPS /
    strip_non_ascii / parse_frontmatter without duplicating them here -- avoids
    drift if build-marketplace.py changes."""
    src = BUILD_MP.read_text()
    head = src.split("def main():")[0]
    ns = {"__file__": str(BUILD_MP)}
    exec(compile(head, str(BUILD_MP), "exec"), ns)
    return ns


def transliterate(s: str) -> str:
    # Unicode escapes, not literal chars -- this file ships as a skill reference
    # and must itself be pure ASCII, or build-marketplace.py's strip_non_ascii
    # would silently delete these literals and turn this function into a no-op.
    s = s.replace("\u2014", " - ").replace("\u2013", "-")   # em dash, en dash
    s = s.replace("\u2018", "'").replace("\u2019", "'")     # curly single quotes
    s = s.replace("\u201c", '"').replace("\u201d", '"')     # curly double quotes
    s = s.replace("\u00bf", "").replace("\u00a1", "")       # inverted ? !
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"[^\x00-\x7F]", "", s)
    return s


def changed_files():
    """Files git considers new/modified (staged or not) -- used to scope the
    non-ASCII check so pre-existing legacy content doesn't block today's
    publish over issues nobody asked to fix right now."""
    try:
        out = subprocess.run(
            ["git", "--no-optional-locks", "status", "--porcelain"],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
        paths = set()
        for line in out.stdout.splitlines():
            # porcelain format: "XY path" (or "XY orig -> new" for renames)
            path = line[3:].split(" -> ")[-1].strip()
            if path:
                paths.add((ROOT / path).resolve())
        return paths
    except Exception:
        return set()


def run_checks(ns, fix=False):
    GROUPS = ns["GROUPS"]
    parse_frontmatter = ns["parse_frontmatter"]

    problems = []
    warnings = []
    changed = changed_files()
    all_skills = [s for _, (_, skills) in GROUPS.items() for s in skills]

    missing = [s for s in all_skills if not (ROOT / s / "SKILL.md").exists()]
    if missing:
        problems.append(f"missing SKILL.md: {missing}")

    dupes = sorted({s for s in all_skills if all_skills.count(s) > 1})
    if dupes:
        problems.append(f"skill(s) listed in more than one GROUP: {dupes}")

    on_disk = {d.name for d in ROOT.iterdir()
               if d.is_dir() and (d / "SKILL.md").exists() and d.name != "plugins"}
    ungrouped = sorted(on_disk - set(all_skills))
    if ungrouped:
        problems.append(f"ungrouped skill(s) (won't propagate): {ungrouped}")

    for skill in all_skills:
        skill_md = ROOT / skill / "SKILL.md"
        if not skill_md.exists():
            continue
        meta = parse_frontmatter(skill_md)
        name = str(meta.get("name", skill))
        desc = str(meta.get("description", ""))
        if len(desc) > 1024:
            problems.append(f"{skill}: description is {len(desc)} chars (limit 1024)")
        if "claude" in name.lower():
            problems.append(f"{skill}: name '{name}' contains reserved word 'claude'")

    # Non-ASCII scan: build-marketplace.py DELETES non-ASCII bytes rather than
    # transliterating them (e.g. accented "metodo" -> "mtodo", ene "senal" ->
    # "seal", an actual English word). Blocking on this repo-wide would stall
    # every publish on ~20 pre-existing files nobody asked to fix today, so it
    # only HARD-BLOCKS for files git shows as new/modified right now; anything
    # else is a non-blocking warning (visible, not gating).
    non_ascii_files = []
    for skill in on_disk:
        refs_dir = ROOT / skill / "references"
        candidates = [ROOT / skill / "SKILL.md"]
        if refs_dir.is_dir():
            candidates += [f for f in refs_dir.glob("*") if f.is_file()]
        for f in candidates:
            if not f.is_file():
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            bad = [c for c in text if ord(c) > 127]
            if bad:
                non_ascii_files.append((f, len(bad)))

    if non_ascii_files:
        if fix:
            for f, _ in non_ascii_files:
                f.write_text(transliterate(f.read_text()), encoding="ascii")
            print(f"Transliterated {len(non_ascii_files)} file(s) to ASCII:")
            for f, n in non_ascii_files:
                print(f"    {f.relative_to(ROOT)}: {n} non-ASCII char(s) removed")
        else:
            blocking = [(f, n) for f, n in non_ascii_files if f.resolve() in changed]
            legacy = [(f, n) for f, n in non_ascii_files if f.resolve() not in changed]

            if blocking:
                problems.append(
                    f"{len(blocking)} newly-changed file(s) contain non-ASCII bytes "
                    "that build-marketplace.py will silently DELETE (not "
                    "transliterate) on publish -- rerun with --fix to transliterate "
                    "them to clean ASCII first:"
                )
                for f, n in blocking:
                    problems.append(f"    {f.relative_to(ROOT)}: {n} non-ASCII char(s)")

            if legacy:
                warnings.append(
                    f"{len(legacy)} pre-existing file(s) also contain non-ASCII bytes "
                    "(not blocking -- not part of this change, but they're being "
                    "silently mangled by every publish too; --fix will clean these "
                    "up as well if you want):"
                )
                for f, n in legacy:
                    warnings.append(f"    {f.relative_to(ROOT)}: {n} non-ASCII char(s)")

    return problems, warnings


def git_status():
    try:
        out = subprocess.run(
            ["git", "--no-optional-locks", "status", "--short"],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip()
    except Exception as e:
        return f"(git status failed: {e})"


def run_publish():
    """Native only. Runs ./publish.sh, auto-recovering once from the known
    stale index.lock left by sandbox git commands."""
    def _run():
        return subprocess.run(["./publish.sh"], cwd=ROOT, text=True, capture_output=True)

    result = _run()
    if result.returncode != 0 and "index.lock" in (result.stderr + result.stdout):
        lock = ROOT / ".git" / "index.lock"
        print(f"Stale index.lock detected, removing {lock} and retrying...")
        lock.unlink(missing_ok=True)
        result = _run()

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


def main():
    fix = "--fix" in sys.argv
    do_publish = "--publish" in sys.argv

    ns = load_build_marketplace_globals()
    problems, warnings = run_checks(ns, fix=fix)

    print(f"Environment: {'SANDBOXED (Cowork agent mount)' if SANDBOXED else 'NATIVE (M2 terminal)'}")
    print(f"Repo root: {ROOT}\n")

    if warnings:
        print("PRE-FLIGHT: non-blocking warnings\n")
        for w in warnings:
            print(f"  ! {w}")
        print()

    if problems:
        print("PRE-FLIGHT: problems found\n")
        for p in problems:
            print(f"  - {p}")
        if not fix:
            print("\n(non-ASCII issues, if any, can be auto-fixed with --fix)")
        print("\nFix the issues above, then re-run.")
        sys.exit(1)

    print("PRE-FLIGHT: clean -- GROUPS/description/name/ASCII checks all pass.\n")

    status = git_status()
    print("git status:")
    print(status if status else "  (clean -- nothing staged)")
    print()

    if not status:
        print("Nothing to publish.")
        return

    if SANDBOXED:
        print("Sandboxed session -- cannot git-write or unlink in this repo "
              "(known limitation). Hand this off:\n")
        print('  cd "/Users/lfp/Projects/SKILL MAKER"')
        print("  ./publish.sh\n")
        print("If it fails with 'Unable to create index.lock: File exists', run:")
        print('  rm -f "/Users/lfp/Projects/SKILL MAKER/.git/index.lock" && ./publish.sh')
        return

    if not do_publish:
        print("Native session, pre-flight clean. Re-run with --publish to actually")
        print("publish, or run ./publish.sh directly.")
        return

    print("Publishing...\n")
    run_publish()


if __name__ == "__main__":
    main()
