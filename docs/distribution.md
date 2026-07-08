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
3. `publish.sh` (M2 only, per the 2026-06-10 rehome -- see MIGRATION_RUNBOOK) runs the
   build, commits `skills: rebuild marketplace (date)`, and pushes. One command.

```bash
# On M2, after editing any SKILL.md or GROUPS:
cd "/Users/lfp/Projects/SKILL MAKER" && ./publish.sh
```

### CORRECTION (2026-07-03): the example path above was wrong and machine-mislabeled

This block previously said "On M1" and pointed at `~/Documents/Claude/Projects/skill-maker`
-- stale on both counts. Forensics from the same-day incident above: `~/Documents/Claude/Projects/skill-maker`
on M2 turned out to be an ABANDONED clone that nobody had touched in ~a month (its reflog
stopped at `f4a3469`, 2026-06-10, while the real marketplace kept advancing daily). The
actual publishing clone the whole time was `/Users/lfp/Projects/SKILL MAKER` -- its reflog
shows unbroken native commits from the 2026-06-10 clone straight through to today
(`106ae49`), including every "rebuild marketplace" commit in between. That path is also
what Cowork mounts as this project's working folder, so edits made in a Cowork session
here and native `./publish.sh` runs both land in the SAME clone -- which is why this path,
not the `~/Documents` one, is the real answer to "where does M2 publish from."

Recommendation, not yet done: decommission `~/Documents/Claude/Projects/skill-maker` (or at
minimum mark it read-only / non-canonical) so a future session doesn't get sent there again
by old muscle memory. Left as a manual decision -- deleting a git working copy isn't done
silently.

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
daily — and at load — runs `claude plugin marketplace update lfp-skills`, then (as
of the 2026-07-03 fix, see CORRECTION above) loops every installed `@lfp-skills`
plugin through `claude plugin update <plugin>@lfp-skills` so installed plugins
cannot silently pin to a stale commit. Logs to
`~/Library/Logs/com.lfp.skill-maker.refresh.log`. Remove with
`./install-refresh.sh --uninstall`. M1 ALSO benefits (its own Cowork consumes the
marketplace); `publish.sh` additionally runs the update right after pushing.

**Machines that installed the job before 2026-07-03 are running the OLD wrapper**
(marketplace-only, no plugin bump) until `./install-refresh.sh` is re-run there —
re-running it is safe/idempotent and simply rewrites the wrapper file.

### TCC gotcha (why the wrapper lives in ~/Library, not the repo)

macOS TCC blocks launchd-spawned processes from executing OR reading anything under
`~/Documents` (`Operation not permitted`). The first cut put the wrapper inside the
repo and failed silently every run. Fix: the wrapper lives in
`~/Library/Application Support/lfp-skill-maker/` and touches only `~/.claude` via
`claude` — never `~/Documents`. Do not move it back into the repo.

## CORRECTION (2026-07-03): `marketplace update` does NOT bump installed plugins

The 2026-06-04 claim below ("re-add is NOT required") is **wrong** and is kept only
as a record of what was believed. Live incident on M3, 2026-07-03: `lfp-skills` was
registered, `claude plugin marketplace update lfp-skills` ran and reported success,
yet `project-migrate` (added to `lfp-core` on 2026-06-10) still errored `Unknown
skill`. Root cause: `claude plugin list` showed `lfp-core@lfp-skills` and
`lfp-thinkers@lfp-skills` both pinned at commit `be47cddbc8ca` — the marketplace
rebuild from **2026-05-29**, 52 commits and 5+ weeks behind HEAD.

`claude plugin marketplace update <marketplace>` only refreshes the marketplace's
own metadata/cache (what versions exist). It does **not** touch plugins already
installed from it — those stay pinned to the commit that was current at install
time until explicitly bumped:

```bash
claude plugin update <plugin>@lfp-skills
# e.g. claude plugin update lfp-core@lfp-skills
```

This fixed it on M3 in one shot (`be47cddbc8ca` -> `106ae4931f57`, matching HEAD;
requires a restart of Claude Code / Cowork to take effect). `install-refresh.sh`
was patched the same day to run this update loop automatically — see below. Until
every machine re-runs `./install-refresh.sh` to pick up the patched wrapper, this
class of failure can recur silently on any machine whose plugins were installed
before a given skill/fix existed.

### Original (retired) claim, kept for context

~~Settled: after `claude plugin marketplace update lfp-skills`, a project surfaces
a newly published skill WITHOUT any Customize -> Skills re-add. Verified by
invoking `/projectmd-auditor` in an M2 project never touched in the UI — it
resolved. So the chain is fully hands-off: publish on M1, the daily launchd job
refreshes each machine, and skills become live in every workspace with no manual UI
step.~~ This held for whatever was tested on 2026-06-04 but does not hold in
general — plugin version pinning is real and the M3 incident above is reproducible
evidence against it.

## Legacy paths (still present, not the live channel)

- `ship-skill.sh <name>` — builds one `.skill`, commits, pushes (per-file model).
- `sync-skills.sh` — `git pull` + lists changed `.skill` files to re-add.
- `deploy-plugins.sh` / iCloud — fully retired.
