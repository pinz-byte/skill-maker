#!/usr/bin/env python3
"""harden-builder.py -- make build-marketplace.py a lossless, self-verifying transform.

Supersedes BOTH fix-plugin-assets.py and patch-builder.py. Delete those two after
this runs; three mechanisms competing for one job is how the original loss hid.

patch-builder.py was audited and failed on two counts, both fixed here:
  * it mirrored SUBDIRECTORIES only, so it still dropped loose top-level files --
    qa-mirror/QA_MIRROR_SETUP.md and qa-sequence/QA_SEQUENCE_SETUP.md, both named
    in their own skill descriptions.
  * its fidelity assertion did not exclude junk, so it would have failed the build
    on 5 tracked SKILL.md.bak* files and 2 .DS_Store -- seven false positives.

Root cause of that second defect: the copy rule and the check rule were written
twice. Here they share ONE predicate pair (_skip_dir / _skip_file) so they cannot
drift apart again.

Three changes to build-marketplace.py:

  1. STOP STRIPPING NON-ASCII.
     `strip_non_ascii` deletes every char above U+007F. It entered in be47cdd
     (2026-05-29) inside a routine "rebuild marketplace" commit, with no comment
     and no stated reason. It currently destroys 3304 characters across the 82
     published skills -- Spanish accents and em-dashes carrying trigger vocabulary
     ("diseo" for "diseno", "ngulo" for "angulo", "voz tcnica"). Anthropic's own
     shipped skills carry em-dashes in their descriptions and load fine, so the
     platform does not require ASCII. Kept as a pass-through: reverting is one line.

  2. MIRROR EVERY ASSET, byte-for-byte -- subdirectories AND loose files.
     Measured loss before this patch: 15 files absent from plugins/, of which 8
     are real assets (2 scripts/, 3 carmatch-intel/deploy/, 2 *_SETUP.md, and
     one more) and 7 are junk that should never have been tracked.

  3. ASSERT FIDELITY AND FAIL LOUDLY.
     After building, every non-junk source file must appear in plugins/ byte for
     byte. Both losses above would have been caught the day they appeared.

Run once, natively, from the SKILL MAKER repo root:

    python3 harden-builder.py
    python3 build-marketplace.py
    ./publish.sh

Idempotent. Backs up to build-marketplace.py.bak6 and refuses to write if the
result does not parse.
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

NEW_COPY = '''            (dst / "SKILL.md").write_text(strip_non_ascii((src / "SKILL.md").read_text()))
            # Mirror every asset byte-for-byte: subdirs AND loose top-level files.
            # The old loop copied references/ only and silently dropped scripts/,
            # deploy/ and *_SETUP.md. _assert_fidelity now fails the build if that
            # ever recurs.
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
                    shutil.copy2(item, dst / item.name)

    _assert_fidelity(plugins_dir)'''

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
        sys.exit("Already patched (by this or by patch-builder.py). "
                 "If patch-builder.py ran, restore build-marketplace.py.bak5 first.")

    changes = []
    if OLD_STRIP not in src:
        sys.exit("ERROR: strip_non_ascii does not match the expected text. "
                 "Builder changed; patch by hand rather than guessing. Nothing written.")
    src = src.replace(OLD_STRIP, NEW_STRIP, 1)
    changes.append("strip_non_ascii -> pass-through; SKIP predicates added")

    if OLD_COPY not in src:
        sys.exit("ERROR: the per-skill copy block does not match the expected text. "
                 "Nothing written.")
    src = src.replace(OLD_COPY, NEW_COPY, 1)
    changes.append("assets mirrored byte-for-byte (subdirs AND loose files)")

    m = re.search(r"^def parse_frontmatter", src, re.M)
    if not m:
        sys.exit("ERROR: could not find an anchor to insert the fidelity check.")
    src = src[:m.start()] + FIDELITY.lstrip("\n") + "\n\n" + src[m.start():]
    changes.append("_assert_fidelity added and wired in, sharing the SKIP predicates")

    for mod in ("os", "shutil"):
        if not re.search(rf"^import {mod}$", src, re.M):
            src = src.replace("import re", f"import {mod}\nimport re", 1)
            changes.append(f"{mod} imported")

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"ERROR: patched file does not parse ({e}). Nothing written.")

    shutil.copy2(BUILD, BUILD + ".bak6")
    open(BUILD, "w", encoding="utf-8").write(src)
    for c in changes:
        print(f"  {c}")
    print("\nBackup: build-marketplace.py.bak6")
    print("\nExpected on the next build: 8 assets restored --")
    print("  cc-session-analyzer/scripts/analyze_sessions.py")
    print("  projectmd-gen/scripts/scan_project.py")
    print("  qa-mirror/QA_MIRROR_SETUP.md")
    print("  qa-sequence/QA_SEQUENCE_SETUP.md")
    print("  carmatch-intel/deploy/{getIntel.js,opsSnapshot.js,DEPLOY.md}")
    print("...and 3304 non-ASCII characters back in the published descriptions.")
    print("\nNEXT:")
    print("  python3 build-marketplace.py")
    print("  ./publish.sh")
    print("\nThen delete the superseded one-shots: fix-plugin-assets.py, patch-builder.py")


if __name__ == "__main__":
    main()
