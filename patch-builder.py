#!/usr/bin/env python3
"""patch-builder.py -- make build-marketplace.py a lossless, self-verifying transform.

Supersedes fix-plugin-assets.py: this puts the behaviour INSIDE the builder
permanently instead of running a one-shot repair after every build.

Three changes to build-marketplace.py:

  1. STOP STRIPPING NON-ASCII.
     `strip_non_ascii` deletes every char above U+007F. It entered in be47cdd
     (2026-05-29) inside a routine "rebuild marketplace" commit, with no comment
     and no documented reason. It currently destroys 3304 characters across the
     82 published skills -- Spanish accents and em-dashes that carry trigger
     vocabulary ("diseno" for "diseño", "ngulo" for "ángulo", "subttulo" for
     "subtítulo"). Anthropic's own shipped skills carry em-dashes in their
     descriptions and load fine, so the platform does not require ASCII.
     The function is kept as a pass-through so the call sites and any future
     reference stay valid, and reverting is a one-line change.

  2. MIRROR EVERY ASSET SUBDIRECTORY, byte-for-byte.
     The old loop copied SKILL.md + references/ only. Five skills carry other
     subdirs and none survived: cc-session-analyzer/scripts, projectmd-gen/scripts
     (both invoked by relative path from their own SKILL.md -- silent no-ops in
     plugin form), carmatch-intel/deploy, and two evals/ fixture dirs.
     Now: every subdir except the SKIP set, copied with shutil.copytree, so a .py
     is never rewritten through a text transform.

  3. ASSERT FIDELITY AND FAIL LOUDLY.
     After building, every skill's file tree in plugins/ must match its source
     (minus the SKIP set), byte for byte. Any missing or differing file aborts
     the build. Both losses above would have been caught the day they appeared.

Run once, natively, from the SKILL MAKER repo root:

    python3 patch-builder.py
    python3 build-marketplace.py
    ./publish.sh

Idempotent. Backs up to build-marketplace.py.bak5 and refuses to write if the
patched file does not parse.
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

NEW_STRIP = '''SKIP_ASSET_DIRS = {"evals", "__pycache__", ".git", ".pytest_cache", ".DS_Store"}


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
            # Mirror EVERY asset subdir byte-for-byte. The old loop copied only
            # references/ and silently dropped scripts/ and deploy/ -- see
            # fidelity check below, which now fails the build if that recurs.
            for sub in sorted(p for p in src.iterdir() if p.is_dir()):
                if sub.name in SKIP_ASSET_DIRS:
                    continue
                shutil.copytree(sub, dst / sub.name, dirs_exist_ok=True)

    _assert_fidelity(plugins_dir)'''

FIDELITY = '''

def _rel_files(base):
    out = {}
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_ASSET_DIRS]
        for f in filenames:
            p = os.path.join(dirpath, f)
            out[os.path.relpath(p, base)] = p
    return out


def _assert_fidelity(plugins_dir):
    """plugins/ must be a faithful projection of source. Fail loudly if not.

    Added 2026-08-13 after two independent silent losses were found by accident:
    dropped asset subdirs, and 3304 stripped non-ASCII characters. Neither was
    caught by any check. This is that check.
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
                 "Builder changed; patch by hand rather than guessing.")
    src = src.replace(OLD_STRIP, NEW_STRIP, 1)
    changes.append("strip_non_ascii -> pass-through")

    if OLD_COPY not in src:
        sys.exit("ERROR: the per-skill copy block does not match the expected text. "
                 "Nothing written.")
    src = src.replace(OLD_COPY, NEW_COPY, 1)
    changes.append("asset subdirs mirrored byte-for-byte")

    m = re.search(r"^def parse_frontmatter", src, re.M)
    if not m:
        sys.exit("ERROR: could not find an anchor to insert the fidelity check.")
    src = src[:m.start()] + FIDELITY.lstrip("\n") + "\n\n" + src[m.start():]
    changes.append("_assert_fidelity added and wired into the build")

    if "import shutil" not in src:
        src = src.replace("import re", "import re\nimport shutil", 1)
        changes.append("shutil imported")
    if "import os" not in src:
        src = src.replace("import re", "import os\nimport re", 1)
        changes.append("os imported")

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"ERROR: patched file does not parse ({e}). Nothing written.")

    shutil.copy2(BUILD, BUILD + ".bak5")
    open(BUILD, "w", encoding="utf-8").write(src)
    for c in changes:
        print(f"  {c}")
    print("\nBackup: build-marketplace.py.bak5")
    print("\nNEXT:")
    print("  python3 build-marketplace.py")
    print("  ls plugins/lfp-core/skills/cc-session-analyzer/scripts")
    print("  ./publish.sh")
    print("\nIf the build now FAILS on fidelity, that is the check working -- it is")
    print("reporting a loss that was already happening silently. Paste the lines.")
    print("fix-plugin-assets.py becomes unnecessary; delete it.")


if __name__ == "__main__":
    main()
