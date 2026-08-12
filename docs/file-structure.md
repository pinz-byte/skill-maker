# File structure and versioning (on-demand)

```text
SKILL MAKER/
|-- CLAUDE.md                         # Claude/Cowork project context
|-- AGENTS.md                         # Codex project context
|-- <skill>/SKILL.md                  # canonical skill source
|-- <skill>/references/               # optional canonical references
|-- build-marketplace.py              # validates and generates marketplace
|-- publish.sh                        # M2-only build, commit, push, refresh
|-- install-refresh.sh                # per-machine installed-plugin updater
|-- .claude-plugin/marketplace.json   # generated marketplace manifest
|-- plugins/<plugin>/                 # generated LFP plugin payloads
|-- team-skills/                      # team-only canonical sources
|-- build-team-toolkit.py             # generates curated Subastop catalog
|-- team-toolkit/                     # ignored, independent generated repo
|-- docs/                             # on-demand operational references
`-- .claude/                          # Cowork rules, hooks, and registry
```

Root `.skill` files and `build-skill.py`, `ship-skill.sh`, `sync-skills.sh`, and
`deploy-plugins.sh` are legacy artifacts. They are not canonical and are not the
live distribution channel.

## Source-of-truth rules

- Edit only root `<skill>/SKILL.md` and its `references/`.
- Assign every canonical skill exactly once in `build-marketplace.py::GROUPS`.
- Treat `plugins/` as generated output; never repair drift there by hand.
- Treat `team-toolkit/` as an independent generated marketplace, not a second
  canonical copy.
- Marketplace versions are git commits; plugin manifests intentionally omit a
  manual semantic version.

## Change classification

- Wording or trigger clarification: small catalog change.
- New behavior, section, or reference: capability change.
- Changed message contract or routing semantics: breaking change requiring
  explicit migration notes.

The live version identifier is the git commit hash surfaced by
`claude plugin list`, not a version number embedded in `SKILL.md`.
