---
name: workspace-plugin-audit
description: >
  Closes the per-workspace plugin install gap. Each Cowork workspace/project is an isolated
  agent with its own plugin list — there is no install-once-works-everywhere. After a skill
  is built and deployed to iCloud, it still must be added manually in every workspace that
  needs it, which produces the recurring "that skill isn't uploaded to the system" / "skill
  not found" surprise when the user tries a new skill in a different project. Use this skill
  whenever the user says "skill not found", "isn't uploaded to the system", "plugin missing
  in this workspace", "is critical-thinker installed here", "audit my plugins", "which
  workspaces have X", "I just deployed, what do I install where", or "why doesn't this skill
  work in this project". Also trigger right after any skill deploy to iCloud, to produce the
  per-workspace reinstall checklist. Fire on casual variations like "the skill isn't showing
  up" or "it works in SKILL MAKER but not here".
---

# Workspace Plugin Audit

Cowork plugins are per-workspace by design. Installing a plugin in SKILL MAKER does NOT make
it available in APEX DESK, CarMatch, or any other project on the same machine. iCloud is the
distribution mechanism (the file is available to install), not auto-install (it does not turn
itself on anywhere). The recurring friction: a freshly deployed skill works where it was
built, then "isn't uploaded to the system" the first time it is tried in another workspace.

## What This Skill Does

Turns "deployed to iCloud" into an explicit "install it here, here, and here" checklist, and
diagnoses a not-found skill as either a packaging fault or a simple missing install.

## Diagnose: packaging fault vs missing install

When a skill reports not-found, it is one of two things. Check packaging FIRST (fast), because
if the package is bad, installing it anywhere fails the same way.

1. **Packaging fault** — bad zip structure, non-ASCII/emoji in the file, or description over
   1024 chars. Verify the built `.skill`:

   ```bash
   cd "$HOME/Documents/Claude/Projects/SKILL MAKER"
   python3 -c "import zipfile; print(zipfile.ZipFile('<name>.skill').namelist())"
   # must show <name>/SKILL.md
   ```

   Confirm it is in iCloud:

   ```bash
   ls "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Claude/Plugins/" | grep <name>
   ```

   If the package is clean and present in iCloud, it is not a packaging fault — go to #2.

2. **Missing install (the common case)** — the plugin simply was not added in THIS workspace.
   Each project agent has its own plugin set. Fix: in the workspace that needs it,
   **Customize -> Add Plugin** (or Skills -> +), browse iCloud Drive -> Claude -> Plugins ->
   `<name>.skill`, install. Active immediately after.

## Post-deploy: produce the per-workspace checklist

After deploying skills to iCloud, do not stop at "deployed." List the active workspaces and
state which ones still need the new skill installed. Known workspaces span M1/M2/M3 (e.g.
SKILL MAKER, APEX DESK, CarMatch, Herald/VMC, and others). Output a concrete checklist:

```
Deployed: herald-config-doctor, machine-bridge, gcp-iam-resolver, workspace-plugin-audit
Install per workspace (Customize -> Add Plugin -> iCloud/Claude/Plugins):
  [ ] SKILL MAKER (M1)
  [ ] APEX DESK (M1)
  [ ] CarMatch (M2)
  [ ] Herald / VMC feed (M3)
  ...one line per workspace that should carry the skill
```

Recommend doing the pass while the iCloud folder is fresh, rather than rediscovering the gap
one workspace at a time later.

## Principles

- **iCloud distributes, it does not install.** Availability in the Plugins folder is necessary
  but not sufficient; each workspace installs separately.
- **Check packaging before install.** A bad package fails identically everywhere — verify the
  zip and description length once before sending the user to click through installs.
- **Different agents, different capabilities — on purpose.** Per-workspace isolation is a
  feature (you can give agents different tools); the fix is a checklist, not a complaint.
- Pairs with [[machine-bridge]] (the iCloud deploy must use the self-resolving script so the
  file actually lands) and the project deploy-plugins.sh.

## Edge Cases

- **iCloud not synced yet:** the file may take seconds-to-minutes to appear on M2/M3. If it is
  missing in the Plugins folder on another machine, wait for sync before assuming a deploy
  failure.
- **Broken alias instead of a real file:** if iCloud shows an alias/placeholder rather than a
  real `.skill`, the deploy wrote a dead path — re-run the self-resolving deploy script (see
  [[machine-bridge]] failure mode 1).
- **Stale version installed:** re-installing over an old version may require removing the old
  plugin entry first if the workspace caches it.
