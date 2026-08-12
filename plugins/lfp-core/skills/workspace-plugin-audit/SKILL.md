---
name: workspace-plugin-audit
description: >-
  Diagnoses a not-found or out-of-date skill in the lfp-skills GitHub marketplace (live
  channel; iCloud is retired). Two failure modes look identical: (1) the plugin was never
  installed on this machine, or (2) it IS installed but pinned to a stale commit, because
  `claude plugin marketplace update` refreshes only the marketplace cache and does NOT bump
  already-installed plugins . Use whenever the user says "skill not found", "unknown skill",
  "isn't uploaded to the system", "plugin missing", "is X installed here", "audit my plugins",
  "which machines have X", "I just published, what needs updating where", or "why doesn't this
  skill work here". NOT auditor-general (reviews builds): this is marketplace install state.
  Also trigger on "still not showing up", "marketplace not refreshed", "it's not picking up
  the new skill", "it works in SKILL MAKER but not here", or right after any publish to
  produce the per-machine update checklist.
metadata:
  intent: audit
---

# Workspace Plugin Audit

The live distribution channel is the `lfp-skills` GitHub marketplace (`pinz-byte/skill-maker`),
installed per machine via `claude plugin install <plugin>@lfp-skills` at user scope. iCloud
(`deploy-plugins.sh`, `.skill` files in Drive) is retired  do not diagnose or recommend it.

The recurring friction is NOT "forgot to add it in this workspace" (the old iCloud-era framing).
It is: a plugin is installed and enabled, the marketplace itself is current, and the skill
inside it is STILL not found or still behaving like an old version  because the installed
plugin is pinned to whatever commit was current the moment it was installed, and nothing
except an explicit per-plugin update bumps that pin.

## What This Skill Does

Diagnoses a not-found or stale skill as one of three things, in this order (cheapest/most
likely first):

## Diagnose, in order

1. **Stale installed version (the common case as of 2026-07-03)**  the plugin IS installed,
   the marketplace IS current, but the installed copy is pinned to an old commit. Check:

   ```bash
   claude plugin list
   # look at the Version hash (e.g. lfp-core@lfp-skills  Version: be47cddbc8ca)
   ```

   That hash is a git commit in `pinz-byte/skill-maker`. If unsure whether it's current,
   just try the fix directly  it's cheap and safe:

   ```bash
   claude plugin update <plugin>@lfp-skills
   # e.g. claude plugin update lfp-core@lfp-skills
   ```

   Restart Claude Code / Cowork after  plugin updates require a restart to take effect.
   `install-refresh.sh` (patched 2026-07-03) now loops this automatically in the daily
   launchd job  but any machine that installed that job BEFORE 2026-07-03 is still
   running the old marketplace-only wrapper until `./install-refresh.sh` is re-run there.

2. **Missing install**  the plugin was never installed on this machine at all.

   ```bash
   claude plugin marketplace list      # is lfp-skills even registered here?
   claude plugin list                  # is the plugin in the installed list?
   claude plugin install <plugin>@lfp-skills
   ```

3. **Packaging / build fault**  the skill was never actually added to a `GROUPS` plugin, or
   `build-marketplace.py`'s fail-loud guard caught something. Check the source repo natively
   (not from a Cowork sandbox  build/publish there is unreliable, see machine-bridge):

   ```bash
   git log --oneline -- <skill-dir>/          # was it ever committed?
   grep -A2 "'<plugin-name>'" build-marketplace.py   # is it listed in GROUPS?
   ```

## Post-publish: produce the per-machine checklist

After publishing new/changed skills, do not stop at "pushed." For each machine (M1/M2/M3),
state whether it needs a fresh `claude plugin install` (never had that plugin) or just an
update (has the plugin, needs the commit bump):

```
Published: project-migrate (added to lfp-core)
Per machine:
  [ ] M1  lfp-core installed? run: claude plugin update lfp-core@lfp-skills
  [ ] M2  publisher machine, already current after ./publish.sh
  [ ] M3  lfp-core installed? run: claude plugin update lfp-core@lfp-skills
```

## Principles

- **The marketplace and the installed plugin are two different things with two different
  freshness states.** `marketplace update` refreshes what's available; `plugin update` (or
  reinstall) is what actually moves an installed plugin forward. Never assume one implies
  the other  this was the exact wrong assumption baked into this project's docs until the
  2026-07-03 incident disproved it.
- **Check the Version hash before guessing.** `claude plugin list` shows the real commit each
  installed plugin is pinned to  compare against `git log -1` in the source repo instead of
  assuming "it's probably fine."
- **iCloud is retired.** Do not send anyone to Customize -> Add Plugin -> iCloud/Claude/Plugins
  or to `deploy-plugins.sh`  that channel no longer exists for this project.
- Pairs with [[machine-bridge]] (native-vs-sandbox build discipline) and `install-refresh.sh`
  (the automated version of step 1, once every machine has re-run it post-2026-07-03).

## Edge Cases

- **Marketplace just published, plugin never installed anywhere yet:** step 2, not step 1 
  there's nothing to bump if it was never installed.
- **`claude plugin update` reports already up to date but the skill still misbehaves:** the
  restart didn't happen yet, or it's actually step 3 (never shipped)  check the Version hash
  moved AND that the skill/plugin name is spelled correctly and really is in that plugin group.
- **User-scope vs per-Cowork-workspace:** everything observed in the 2026-07-03 incident was
  fixed at `claude plugin` user scope (machine-wide), not inside a specific Cowork project's
  Customize panel. Whether an individual Cowork workspace can additionally restrict which
  user-scope plugins it exposes is NOT yet verified either way  if a plugin is confirmed
  current at user scope but still missing in one specific workspace only, treat that as an
  open question, not a settled mechanism, and investigate rather than assuming either model.
