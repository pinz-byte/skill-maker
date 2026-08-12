# Build Pattern (on-demand)

The live distribution channel is the private `lfp-skills` Claude Code plugin
marketplace. Root `<skill>/SKILL.md` directories are canonical; generated
`plugins/` copies and `.claude-plugin/marketplace.json` are the payload.

## Add or change a skill

1. Edit `<skill>/SKILL.md` and optional `<skill>/references/`.
2. Assign every new skill exactly once in `GROUPS` inside
   `build-marketplace.py`.
3. Validate locally:

```bash
python3 build-marketplace.py
```

The builder fails on missing sources, duplicate assignments, ungrouped skills,
invalid frontmatter, descriptions over 1,024 characters, and reserved names.
Validation completes before the last generated marketplace is removed.

## Publish

Publish from M2 only:

```bash
./publish.sh
```

That command rebuilds, stages, commits, pushes, refreshes the marketplace, and
updates this machine's installed `@lfp-skills` plugins. Consumer machines use
the daily job installed by `./install-refresh.sh`.

## Generated-copy verification

Generated skill bodies equal their canonical sources after the builder's
required ASCII normalization. Never edit `plugins/<plugin>/skills/` directly;
the next build replaces those files.

## Legacy per-file channel

`build-skill.py`, `ship-skill.sh`, `sync-skills.sh`, root `.skill` bundles, and
`deploy-plugins.sh` belong to the retired iCloud/per-workspace channel. They are
not the supported build or distribution path and must not be recommended for
new work.
