#!/usr/bin/env python3
"""
build-skill.py — canonical skill builder for SKILL MAKER
Usage: python3 build-skill.py <skill-name>

Produces: <skill-name>.skill (the only install format)
Strips non-ASCII, verifies output, deploys to iCloud.
"""
import zipfile, re, sys, subprocess
from pathlib import Path

def strip_non_ascii(s):
    return re.sub(r'[^\x00-\x7F\n\r\t ]', '', s)

def build(name):
    skill_dir = Path(name)
    if not skill_dir.exists():
        print(f"ERROR: {name}/ directory not found")
        sys.exit(1)

    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        print(f"ERROR: {name}/SKILL.md not found")
        sys.exit(1)

    skill_md = strip_non_ascii(skill_md_path.read_text())

    # Check description length from frontmatter
    import re as re2
    desc_match = re2.search(r'description:\s*>\s*\n((?:  .+\n)+)', skill_md)
    if desc_match:
        desc = desc_match.group(1).replace('  ', '').replace('\n', ' ').strip()
        if len(desc) > 1024:
            print(f"WARNING: description is {len(desc)} chars (limit 1024)")

    # Collect reference files if any
    refs_dir = skill_dir / "references"

    output = f"{name}.skill"
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{name}/SKILL.md", skill_md)
        if refs_dir.exists():
            for ref in refs_dir.iterdir():
                if ref.is_file():
                    content = strip_non_ascii(ref.read_text())
                    zf.writestr(f"{name}/references/{ref.name}", content)
                    print(f"  + references/{ref.name}")

    # Verify
    with zipfile.ZipFile(output) as zf:
        files = zf.namelist()

    print(f"Built: {output}")
    print(f"Contents: {files}")
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 build-skill.py <skill-name>")
        sys.exit(1)
    name = sys.argv[1]
    build(name)
    print(f"\nDone. Install {name}.skill via Cowork -> Customize -> Skills -> +")
