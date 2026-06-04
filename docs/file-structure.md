# File structure + version bump (on-demand)

```
SKILL MAKER/
├── CLAUDE.md                        # root context (ALWAYS tier)
├── deploy-plugins.sh                # legacy: deploy .plugin files to iCloud
├── [name]/SKILL.md                  # skill source (editable)
├── [name].skill                     # built bundle (install this)
├── docs/                            # on-demand context (read when needed)
│   ├── build-pattern.md             # build steps + git
│   ├── distribution.md              # M2/M3 sync + install detail
│   └── file-structure.md            # this file
└── .claude/                         # AUTO-LOADED by Cowork every session
    ├── rules/plugin-packaging.md    # packaging rules (zip structure, emoji stripping)
    ├── rules/skill-authoring.md     # SKILL.md format and trigger language rules
    ├── rules/inbox-registry.md      # Notion inbox UUIDs for agent-bridge routing
    ├── rules/deploy-target.md       # iCloud deploy target (legacy)
    ├── agents/skill-maker-builder.md # workspace agent context
    └── hooks/pre-commit.sh          # validates SKILL.md before commit
```

Note: `.claude/` auto-loads every session, so on-demand content lives in `docs/`
(not auto-loaded) and is referenced from CLAUDE.md by plain-path pointer.

## Version bump rules

- Patch (1.0.x): wording fixes, description tweaks
- Minor (1.x.0): new sections, new capability, new reference files
- Major (x.0.0): breaking changes to message format or trigger interface
