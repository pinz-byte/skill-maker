#!/usr/bin/env python3
"""fix-builder-losses.py -- make build-marketplace.py lossless and self-verifying.

Third attempt. Supersedes fix-plugin-assets.py, patch-builder.py and
harden-builder.py -- delete all three after this runs.

What went wrong before, so it is on the record:
  * patch-builder.py mirrored SUBDIRECTORIES only, so it still dropped loose
    top-level files (qa-mirror/QA_MIRROR_SETUP.md, qa-sequence/QA_SEQUENCE_SETUP.md,
    both named in their own skill descriptions), and its fidelity check did not
    exclude junk, so it would have failed the build on 5 tracked SKILL.md.bak*
    files and 2 .DS_Store.
  * harden-builder.py fixed both of those but appended the _assert_fidelity CALL
    to the end of the copy block at 4-space indent. The copy block sits inside
    `for skill in skills:` inside `for plugin, ... in GROUPS.items():`, and the
    line immediately after it -- marketplace["plugins"].append(...) -- is at
    8-space indent. Dedenting mid-loop produced `unexpected indent`. The guard
    caught it and wrote nothing.

Here the call is inserted separately, anchored just before marketplace.json is
written (after both loops close), reusing that anchor's own indentation instead
of assuming one.

Three changes to build-marketplace.py:

  1. STOP STRIPPING NON-ASCII. `strip_non_ascii` deletes every char above U+007F.
     It entered in be47cdd (2026-05-29) inside a routine "rebuild marketplace"
     commit with no comment and no stated reason, and currently destroys 3304
     characters across the 82 published skills -- Spanish accents and em-dashes
     carrying trigger vocabulary. Anthropic's own shipped skills carry em-dashes
     in their descriptions and load fine. Kept as a pass-through; reverting is
     one line.

  2. MIRROR EVERY ASSET byte-for-byte -- subdirectories AND loose files.
     Measured loss today: 15 files absent from plugins/, 8 of them real assets.

  3. ASSERT FIDELITY AND FAIL LOUDLY, sharing ONE skip predicate with the copy
     loop so the two can never disagree -- writing them separately is what let
     the original loss survive three months.

Run once, natively, from the SKILL MAKER repo root:

    python3 fix-builder-losses.py
    python3 build-marketplace.py

Do NOT chain ./publish.sh on the same line: if the patch aborts, publish would
run the old builder and ship anyway, which is what happened on the last attempt.

Idempotent. Backs up to build-marketplace.py.bak7 and writes nothing unless the
result parses AND both the definition and the call site are present.
"""
import ast
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
BUILD = os.path.join(ROOT, "build-marketplace.py")

OLD_STRIP = '''def strip_non_ascii(s: str) -> str:
    return re.sub(r"[^\\x00-\\x7F\\n\\r\\t ]", "", s)'''

NEW_STRIP = '''# Shared by the copy loop AND the fidelity check below. One rule, one place --
# writing them separately is what let a silent loss survive three months.
SKIP_DIRS = {"evals", "__pycache__", ".git", ".pytest_cache", "node_modules"}
SKIP_FILE_GLOBS = ("*.bak", "*.bak[0-9]", "*.bak[0-9][0-9]", ".DS_Store", "*.pyc",
                   "*.swp", "Thumbs.db")


def _skip_dir(name):
    return name in SKIP_DIRS


def _skip_file(name):
    import fnmatch
    return any(fnmatch.fnmatch(name, g) for g in SKIP_FILE_GLOBS)


def strip_non_ascii(s: str) -> str:
    """Pass-through since 2026-08-13. Kept so call sites stay valid.

    This used to delete every char above U+007F. It entered in be47cdd
    (2026-05-29) with no comment and no stated reason, and silently destroyed
    3304 characters across the catalog -- Spanish accents and em-dashes that
    carry trigger vocabulary. Anthropic's own skills ship em-dashes in their
    descriptions and load fine, so the platform does not require ASCII.
    To restore the old behaviour, put the re.sub back on the next line.
    """
    return s'''

OLD_COPY = '''            (dst / "SKILL.md").write_text(strip_non_ascii((src / "SKILL.md").read_text()))
            refs = src / "references"
            if refs.is_dir():
                for f in refs.iterdir():
                    if f.is_file():
                        rdst = dst / "references"
                        rdst.mkdir(exist_ok=True)
                        (rdst / f.name).write_text(strip_non_ascii(f.read_text()))'''

# NOTE: ends at the same indent level it started. No dedent here -- the next
# line in the file is marketplace["plugins"].append(...) at 8 spaces.
NEW_COPY = '''            (dst / "SKILL.md").write_text(strip_non_ascii((src / "SKILL.md").read_text()))
            # Mirror every asset byte-for-byte: subdirs AND loose top-level files.
            # The old loop copied references/ only and silently dropped scripts/,
            # deploy/ and *_SETUP.md. _assert_fidelity fails the build if that recurs.
            for item in sorted(src.iterdir()):
                if item.name == "SKILL.md":
                    continue
                if item.is_dir():
                    if _skip_dir(item.name):
                        continue
                    shutil.copytree(
                        item, dst / item.name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(*SKIP_FILE_GLOBS, *SKIP_DIRS))
                elif item.is_file() and not _skip_file(item.name):
                    shutil.copy2(item, dst / item.name)'''

FIDELITY = '''

def _rel_files(base):
    out = {}
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if not _skip_dir(d)]
        for f in filenames:
            if _skip_file(f):
                continue
            p = os.path.join(dirpath, f)
            out[os.path.relpath(p, base)] = p
    return out


def _assert_fidelity(plugins_dir):
    """plugins/ must be a faithful projection of source. Fail loudly if not.

    Added 2026-08-13 after two independent silent losses were found by accident:
    dropped asset files, and 3304 stripped non-ASCII characters. Neither was
    caught by any check. This is that check. It uses the same _skip_dir /
    _skip_file predicates as the copy loop, so the two cannot disagree.
    """
    missing, differing = [], []
    for pdir in sorted(plugins_dir.iterdir()):
        sdir = pdir / "skills"
        if not sdir.is_dir():
            continue
        for skill in sorted(sdir.iterdir()):
            src = ROOT / skill.name
            if not src.is_dir():
                continue
            want = _rel_files(str(src))
            got = _rel_files(str(skill))
            for rel, spath in want.items():
                gpath = got.get(rel)
                if gpath is None:
                    missing.append(f"{pdir.name}/{skill.name}/{rel}")
                    continue
                with open(spath, "rb") as a, open(gpath, "rb") as b:
                    if a.read() != b.read():
                        differing.append(f"{pdir.name}/{skill.name}/{rel}")
    if missing or differing:
        for m in missing:
            print(f"  MISSING in plugins/: {m}")
        for d in differing:
            print(f"  DIFFERS from source: {d}")
        raise SystemExit(
            f"build blocked: plugins/ is not a faithful projection of source "
            f"({len(missing)} missing, {len(differing)} differing)."
        )
    print("  fidelity OK -- every source file reproduced byte-for-byte in plugins/")
'''


def main():
    if not os.path.isfile(BUILD):
        sys.exit("ERROR: run this from the SKILL MAKER repo root.")
    src = open(BUILD, encoding="utf-8").read()

    if "Pass-through since 2026-08-13" in src:
        sys.exit("Already patched. Nothing to do.")

    changes = []

    if OLD_STRIP not in src:
        sys.exit("ERROR: strip_non_ascii does not match the expected text. "
                 "Nothing written.")
    src = src.replace(OLD_STRIP, NEW_STRIP, 1)
    changes.append("strip_non_ascii -> pass-through; SKIP predicates added")

    if OLD_COPY not in src:
        sys.exit("ERROR: the per-skill copy block does not match the expected text. "
                 "Nothing written.")
    src = src.replace(OLD_COPY, NEW_COPY, 1)
    changes.append("assets mirrored byte-for-byte (subdirs AND loose files)")

    m = re.search(r"^def parse_frontmatter", src, re.M)
    if not m:
        sys.exit("ERROR: no anchor for the fidelity definition. Nothing written.")
    src = src[:m.start()] + FIDELITY.lstrip("\n") + "\n\n" + src[m.start():]
    changes.append("_assert_fidelity defined")

    # The call goes AFTER both loops close, just before marketplace.json is
    # written -- so a loss aborts the build before the manifest is updated.
    # Reuse the anchor's own indentation instead of assuming it.
    call = re.search(r'^([ \t]*)mp_dir = ROOT / "\.claude-plugin"', src, re.M)
    if not call:
        sys.exit("ERROR: no anchor for the fidelity call. Nothing written.")
    indent = call.group(1)
    src = (src[:call.start()]
           + f"{indent}_assert_fidelity(plugins_dir)\n\n"
           + src[call.start():])
    changes.append(f"_assert_fidelity called at indent {len(indent)} before marketplace.json")

    for mod in ("os", "shutil"):
        if not re.search(rf"^import {mod}$", src, re.M):
            src = src.replace("import re", f"import {mod}\nimport re", 1)
            changes.append(f"{mod} imported")

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"ERROR: patched file does not parse ({e}). Nothing written.")

    defined = any(isinstance(n, ast.FunctionDef) and n.name == "_assert_fidelity"
                  for n in ast.walk(tree))
    called = sum(1 for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_assert_fidelity")
    if not defined or called != 1:
        sys.exit(f"ERROR: post-check failed (defined={defined}, call sites={called}). "
                 "Nothing written.")
    changes.append("post-check: defined once, called exactly once")

    shutil.copy2(BUILD, BUILD + ".bak7")
    open(BUILD, "w", encoding="utf-8").write(src)
    for c in changes:
        print(f"  {c}")
    print("\nBackup: build-marketplace.py.bak7")
    print("\nExpected on the next build: 8 assets restored --")
    print("  cc-session-analyzer/scripts/analyze_sessions.py")
    print("  projectmd-gen/scripts/scan_project.py")
    print("  qa-mirror/QA_MIRROR_SETUP.md")
    print("  qa-sequence/QA_SEQUENCE_SETUP.md")
    print("  carmatch-intel/deploy/{getIntel.js,opsSnapshot.js,DEPLOY.md}")
    print("...and 3304 non-ASCII characters back in the published descriptions.")
    print("\nNEXT -- run the build ALONE first, do not chain publish:")
    print("  python3 build-marketplace.py")


if __name__ == "__main__":
    main()
