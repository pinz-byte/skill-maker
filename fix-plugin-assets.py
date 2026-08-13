#!/usr/bin/env python3
"""fix-plugin-assets.py -- one-shot patch for build-marketplace.py.

Defect found by dedupe-check 2026-08-13: the plugin builder copies ONLY
SKILL.md + references/. Every other subdirectory is silently dropped, so any
skill that shells out to its own script ships broken inside a plugin:

    cc-session-analyzer  ->  scripts/analyze_sessions.py   (SKILL.md L40, L45)
    projectmd-gen        ->  scripts/scan_project.py       (SKILL.md L39)
    carmatch-intel       ->  deploy/{getIntel.js,opsSnapshot.js,DEPLOY.md}

Those two skills work today only because the standalone ACCOUNT copy still
carries the script. Deleting the standalone copy before this patch lands
turns both into silent no-ops.

This rewrites the copy loop to mirror every subdirectory except EXCLUDE_DIRS,
stripping non-ASCII from .md/.txt only and copying everything else byte-exact
(stripping a .py would corrupt it).

Run natively on M2:
    cd "$HOME/Projects/SKILL MAKER" && python3 fix-plugin-assets.py
Then verify, then ./publish.sh
"""
import pathlib
import shutil
import sys

TARGET = pathlib.Path("build-marketplace.py")

OLD = '''            refs = src / "references"
            if refs.is_dir():
                for f in refs.iterdir():
                    if f.is_file():
                        rdst = dst / "references"
                        rdst.mkdir(exist_ok=True)
                        (rdst / f.name).write_text(strip_non_ascii(f.read_text()))
'''

NEW = '''            # Mirror every asset subdir, not just references/. Skills that shell
            # out to scripts/ shipped broken for months because this loop was
            # references-only -- see fix-plugin-assets.py for the evidence.
            EXCLUDE_DIRS = {"evals", "__pycache__", ".git"}
            STRIP_EXT = {".md", ".txt"}
            for sub in sorted(p for p in src.iterdir() if p.is_dir()):
                if sub.name in EXCLUDE_DIRS:
                    continue
                for f in sorted(sub.rglob("*")):
                    if not f.is_file():
                        continue
                    out = dst / f.relative_to(src)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    if f.suffix.lower() in STRIP_EXT:
                        out.write_text(strip_non_ascii(f.read_text()))
                    else:
                        shutil.copy2(f, out)
'''


def main():
    if not TARGET.is_file():
        sys.exit("run this from the SKILL MAKER repo root -- build-marketplace.py not found")
    text = TARGET.read_text()
    if "EXCLUDE_DIRS" in text:
        print("already patched -- no change")
        return 0
    if text.count(OLD) != 1:
        sys.exit("copy loop not found verbatim (%d matches) -- patch by hand, do not force"
                 % text.count(OLD))
    if "import shutil" not in text:
        sys.exit("build-marketplace.py does not import shutil -- add it first")
    TARGET.write_text(text.replace(OLD, NEW))
    print("patched build-marketplace.py -- asset subdirs now mirror into plugins")
    print("next: python3 build-marketplace.py && ls plugins/lfp-core/skills/cc-session-analyzer/scripts")
    print("then: ./publish.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
