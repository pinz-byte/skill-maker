<!-- DESTINATION: .claude/build-pattern.md -->
# Build Pattern (on-demand)

Every skill produces ONE output file: `name.skill`. The `.plugin` format is
deprecated -- Cowork's validator rejects it. Use `.skill` only.

```bash
# Build a skill
python3 build-skill.py <skill-name>

# Distribute: commit + push to the private remote (M2/M3 pull via sync-skills.sh)
git add -A && git commit -m "feat(<skill>): ..." && git push
```

Or manually:

```python
import zipfile, re

NAME = "my-skill"

def strip_non_ascii(s):
    return re.sub(r'[^\x00-\x7F\n\r\t ]', '', s)

skill_md = strip_non_ascii(open(f'{NAME}/SKILL.md').read())

with zipfile.ZipFile(f'{NAME}.skill', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr(f'{NAME}/SKILL.md', skill_md)
    # add reference files if needed:
    # zf.writestr(f'{NAME}/references/ref.md', ref_md)
```

Install: Cowork -> Customize -> Skills -> + -> select `name.skill`

## Git

```bash
# Pre-commit hook is live — validates SKILL.md and .plugin structure before every commit
# Hook location: .git/hooks/pre-commit (symlinked from .claude/hooks/pre-commit.sh)
git add -A && git commit -m "feat(self-audit): add self-audit plugin v1.0.0"
```

## Packaging verification

- Verify zip contents before deploying:
  `python3 -c "import zipfile; print(zipfile.ZipFile('x.skill').namelist())"`
