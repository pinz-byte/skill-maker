# SKILL MAKER — Claude Project Context

Skill and plugin authoring lab for the LFP ecosystem. Produces `.plugin` files that extend
Claude agents across Cowork (M1, M2, M3) and Claude.ai Chat projects.

## Deployed Plugins

| Plugin | Version | Status | Purpose |
|---|---|---|---|
| `agent-bridge` | 1.2.2 | deployed | Cross-project Notion inbox messaging system |
| `git-ops` | current | deployed | Full Git lifecycle autonomy for build agents |
| `reentry` | current | deployed | Session re-entry and context reconstruction |
| `self-audit` | 1.0.0 | deployed | Pre-delivery self-auditing protocol |
| `critical-thinker` | 1.0.0 | deployed | Blunt, unfiltered critical thinking companion |

## Key Commands

```bash
# Deploy all plugins to iCloud (M2/M3 pick up on sync)
bash "/sessions/relaxed-funny-pasteur/mnt/SKILL MAKER/deploy-plugins.sh"

# Install on M2/M3: Cowork -> Customize -> Add Plugin
# Source: iCloud Drive -> Claude -> Plugins
```

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

# Deploy all skills to iCloud
bash deploy-plugins.sh
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
- Run `deploy-plugins.sh` after every build — never copy individual files manually

## Git

```bash
# Pre-commit hook is live — validates SKILL.md and .plugin structure before every commit
# Hook location: .git/hooks/pre-commit (symlinked from .claude/hooks/pre-commit.sh)
git add -A && git commit -m "feat(self-audit): add self-audit plugin v1.0.0"
```
