# SKILL MAKER — Claude Project Context

Skill authoring lab for the LFP ecosystem. Produces `.skill` files that extend Claude agents
across Cowork (M1, M2, M3) and Claude.ai Chat projects.

## Distribution — private git remote (M1/M2/M3 parity)

Skills are distributed via a private GitHub repo, NOT iCloud. iCloud sync proved unreliable
(M2 ran ~2 weeks stale, silently). Git is the source of truth: deterministic, versioned,
inspectable. (Established 2026-05-29.)

- Remote: `git@github.com:pinz-byte/skill-maker.git` (private; HTTPS form works too)
- M1 is the source of truth — this is where skills are authored and built.
- After building a skill on M1: `git add -A && git commit -m "..." && git push`
- On M2/M3: `cd ~/Documents/Claude/Projects/skill-maker && ./sync-skills.sh`
  (runs `git pull` and lists exactly which `.skill` files changed so you know what to re-add)
- Install per workspace: Cowork -> Customize -> Skills -> + -> browse to the repo folder ->
  select the `.skill` -> confirm the toggle is ON.

Per-workspace install is manual and irreducible: git distributes the FILES across machines;
each Cowork workspace still adds + enables each skill separately (Cowork isolates plugins per
project on purpose). iCloud and `deploy-plugins.sh` are legacy — superseded by git.

## File Structure

```
SKILL MAKER/
├── CLAUDE.md                        # this file
├── deploy-plugins.sh                # deploy all .plugin files to iCloud
├── [name]/SKILL.md                  # skill source (editable)
├── [name].plugin                    # built bundle (zip, install this)
├── [name].skill                     # alternate format (same content)
└── .claude/
    ├── rules/plugin-packaging.md    # packaging rules (zip structure, emoji stripping)
    ├── rules/skill-authoring.md     # SKILL.md format and trigger language rules
    ├── rules/inbox-registry.md
    ├── rules/deploy-target.md       # iCloud deploy target and deploy-plugins.sh usage      # Notion inbox UUIDs for agent-bridge routing
    ├── agents/skill-maker-builder.md # workspace agent context
    └── hooks/pre-commit.sh          # validates SKILL.md and .plugin before commit
```

## Build Pattern

Every skill produces ONE output file: `name.skill`

The `.plugin` format is deprecated — Cowork's validator rejects it. Use `.skill` only.

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

## Version Bump Rules

- **Patch** (1.0.x): wording fixes, description tweaks
- **Minor** (1.x.0): new sections, new capability, new reference files
- **Major** (x.0.0): breaking changes to message format or trigger interface

## Critical Rules

- Always strip emoji before packaging — Cowork rejects non-ASCII silently
- Description in plugin.json <= 1024 chars (hard limit, silent failure)
- Verify zip contents before deploying: `python3 -c "import zipfile; print(zipfile.ZipFile('x.plugin').namelist())"`
- Inbox UUIDs in `rules/inbox-registry.md` and `agent-bridge/SKILL.md` must stay in sync
- Commit + push after every build — git is the distribution channel (not iCloud)
- Install is per-workspace and manual; updating a skill needs a remove + re-add in each workspace
- Avoid duplicate installs: add a skill from ONE folder per machine (the git clone), not also from iCloud

## Git

```bash
# Pre-commit hook is live — validates SKILL.md and .plugin structure before every commit
# Hook location: .git/hooks/pre-commit (symlinked from .claude/hooks/pre-commit.sh)
git add -A && git commit -m "feat(self-audit): add self-audit plugin v1.0.0"
```
