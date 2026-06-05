# Distribution detail (on-demand)

_Last verified 2026-06-04._

Skills ship as a **Claude Code plugin marketplace** named `lfp-skills`, carried
over a private GitHub repo (NOT iCloud — iCloud ran ~2 weeks stale silently, so it
was retired 2026-05-29). Git is the transport; the marketplace tree is the payload.

## The pipeline

1. Edit source of truth: each top-level `<skill>/SKILL.md` (+ optional `references/`).
2. `build-marketplace.py` regenerates the committed marketplace tree:
   - `.claude-plugin/marketplace.json`
   - `plugins/<plugin>/.claude-plugin/plugin.json`
   - `plugins/<plugin>/skills/<skill>/SKILL.md`
   Plugins/groups are defined in `GROUPS` inside that script. `plugin.json` omits
   `version` on purpose, so every commit reads as a new version (drives auto-update).
3. `publish.sh` (M1 only) runs the build, commits `skills: rebuild marketplace (date)`,
   and pushes. One command.

```bash
# On M1, after editing any SKILL.md or GROUPS:
cd ~/Documents/Claude/Projects/skill-maker && ./publish.sh
```

## Fail-loud grouping guard (added 2026-06-04)

Every skill dir on disk must be listed in some `GROUPS` plugin. If one isn't,
`build-marketplace.py` **halts** and names it — it will not ship a partial
marketplace. This closes the gap where 6 built skills (`carmatch-intel`, `offload`,
`projectmd-auditor`, `projectmd-optimizer`, `qa-mirror`, `qa-sequence`) were built
but never added to `GROUPS`, so they silently never reached M2/M3. Adding a skill
now means: create its dir AND add it to a GROUP, or the build stops you.

## Marketplace is GitHub-sourced (confirmed 2026-06-04)

`claude plugin marketplace list` shows `lfp-skills -> Source: GitHub
(pinz-byte/skill-maker)`. So `claude` keeps its OWN clone under `~/.claude` and
`claude plugin marketplace update lfp-skills` pulls straight from GitHub. The
local repo in `~/Documents` is the AUTHORING source only — refreshing a consumer
machine does NOT require `git pull` of that repo. The folder name also differs per
machine (M1 `SKILL MAKER`, M2/M3 `skill-maker`); rely on no fixed path.

## Keeping every machine current (M1, M2, M3)

Run once per machine:

```bash
./install-refresh.sh        # from inside the repo; path-agnostic
```

`install-refresh.sh` installs a launchd job (`com.lfp.skill-maker.refresh`) that
daily — and at load — runs `claude plugin marketplace update lfp-skills`, logging
to `~/Library/Logs/com.lfp.skill-maker.refresh.log`. Remove with
`./install-refresh.sh --uninstall`. M1 ALSO benefits (its own Cowork consumes the
marketplace); `publish.sh` additionally runs the update right after pushing.

### TCC gotcha (why the wrapper lives in ~/Library, not the repo)

macOS TCC blocks launchd-spawned processes from executing OR reading anything under
`~/Documents` (`Operation not permitted`). The first cut put the wrapper inside the
repo and failed silently every run. Fix: the wrapper lives in
`~/Library/Application Support/lfp-skill-maker/` and touches only `~/.claude` via
`claude` — never `~/Documents`. Do not move it back into the repo.

## Open question: is per-workspace re-add still required?

`claude plugin marketplace update lfp-skills` is CONFIRMED working (M2, 2026-06-04).
What's still unconfirmed: whether a project then sees a newly published skill
WITHOUT a manual Customize -> Skills re-add. To close this: after a refresh, check
whether `projectmd-auditor` resolves in a project you never touched in the UI.
- If yes: fully automated; delete this section.
- If no: per-workspace re-enable is still needed; document the exact step here.

## Legacy paths (still present, not the live channel)

- `ship-skill.sh <name>` — builds one `.skill`, commits, pushes (per-file model).
- `sync-skills.sh` — `git pull` + lists changed `.skill` files to re-add.
- `deploy-plugins.sh` / iCloud — fully retired.
