# skill-maker-builder — SKILL MAKER Workspace Agent

## What this workspace is
A skill and plugin authoring lab for the LFP ecosystem. Produces `.plugin` files that extend
Claude agents across Cowork (M1, M2, M3) and Claude.ai Chat projects. Every skill is a
SKILL.md file packaged into a zip bundle with a specific internal structure.

## Runtime
- No code runtime — pure Markdown + Python packaging scripts
- Deploy: ./publish.sh -> git marketplace, then the desktop 3-store ritual (see .claude/rules/deploy-target.md). iCloud and .skill files are DEAD channels.

## File map

| File/Dir | Purpose |
|---|---|
| `agent-bridge/SKILL.md` | Cross-project mail system skill (v1.2.2) |
| `reentry/SKILL.md` | Session re-entry protocol skill |
| `git-ops/SKILL.md` | Full git autonomy skill |
| `self-audit/SKILL.md` | Self-audit skill with references |
| `*.plugin` | Built plugin bundles ready for install |
| `deploy-plugins.sh` | DEAD -- retired iCloud channel, do not run |
| `reentry-workspace/` | Eval test cases and HTML eval viewer |

## Plugin format — exact structure required

```
plugin-name.plugin  (zip file)
├── .claude-plugin/
│   └── plugin.json         # name, version, description (<=1024 chars), author
└── skills/
    └── [skill-name]/
        └── SKILL.md        # YAML frontmatter + Markdown body
```

plugin.json schema:
```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "Max 1024 characters. No emoji.",
  "author": {"name": "LFP Ecosystem"}
}
```

## SKILL.md format

```markdown
---
name: skill-name
description: >
  Trigger conditions and what this skill does.
  Max 1024 characters total. No emoji characters.
---

# Skill Title

[Skill body in Markdown]
```

## Build command (standard)

```python
import zipfile, json, re
content = open('skills/NAME/SKILL.md').read()
content = re.sub(r'[^\x00-\x7F\n\r\t ]', '', content)  # strip emoji
plugin_json = {"name": "NAME", "version": "X.Y.Z", "description": "...", "author": {"name": "LFP Ecosystem"}}
with zipfile.ZipFile('NAME.plugin', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('.claude-plugin/plugin.json', json.dumps(plugin_json, indent=2))
    zf.writestr('skills/NAME/SKILL.md', content)
```

## Deploy workflow

1. Edit `skills/[name]/SKILL.md`
2. Build: run python3 package script -> produces `[name].plugin`
3. Deploy: `./publish.sh` -> git marketplace + desktop 3-store ritual. NEVER deploy-plugins.sh (DEAD).
4. Install: Cowork -> Customize -> Add Plugin on each machine

## Conventions

- One SKILL.md per skill, in its own directory
- Version bump on every plugin rebuild (semver: patch for fixes, minor for new features)
- Always strip emoji before packaging (Cowork validator rejects non-ASCII)
- Description in plugin.json must match or summarize the SKILL.md frontmatter description
- Inbox UUIDs live in agent-bridge/SKILL.md Inbox Registry — update there first

## Never

- Never commit .plugin files with emoji in SKILL.md (pre-commit hook catches this)
- Never exceed 1024 chars in SKILL.md description frontmatter
- Never package without verifying zip contents (check namelist())
- Never update the inbox registry in one place only — keep SKILL.md and Notion in sync
