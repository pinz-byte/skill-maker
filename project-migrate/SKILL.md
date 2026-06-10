---
name: project-migrate
description: >
  Migrates a Cowork project from one machine to another (M1/M2/M3) without losing
  the state that does not travel with files. Git is the transport; the real work is
  the non-portable state inventory: agent memory, launchd jobs, credentials, registry
  rows, source-of-truth invariants. Two modes: REHOME (target becomes canonical,
  source decommissioned) and SATELLITE (clone for occasional work, source stays
  canonical). Use this skill whenever the user says "migrate this project",
  "move [project] to M2/M1/M3", "rehome this project", "transfer project to another
  machine", "this project should live on", "make M2 the home of", "clone this project
  on", "project migration", or names two machines alongside a move verb. Also trigger
  on "switch machines", "M1 to M2", "decommission this machine's copy", or casual
  variations like "let's move this over to the other Mac". Scope: Cowork projects
  with a filesystem only -- Chat-hosted projects have nothing to move.
---

# Project Migrate -- Machine-to-Machine Cowork Project Migration

Moves a Cowork project between machines (M1/M2/M3) as a disciplined protocol, not
an ad-hoc copy. The file transfer is the trivial 20%. The 80% that ad-hoc moves
lose every time: agent memory, launchd jobs, credentials, ecosystem registry rows,
and "publish from X only" invariants. This skill encodes the full inventory so no
migration silently drops state.

## Phase 0 -- Classify (always first)

Answer three questions before touching anything:

1. **Transport class.** Git repo with private remote (best case) / git repo with no
   remote (create one on `pinz-byte` first) / loose folder (init git + private remote
   first -- git is the only approved transport; never iCloud or raw copy).
2. **Mode.** REHOME = target becomes the canonical machine and sole publisher;
   source gets decommissioned. SATELLITE = target gets a working clone; source stays
   canonical; pull-before-work discipline applies. If the user has not said which,
   ASK -- the two modes diverge at Phase 4.
3. **Does this project publish something?** If the project is itself a distribution
   hub (marketplace, deploy scripts, scheduled publishers), all migration-related
   edits MUST be published from the SOURCE machine before handoff, because the
   source is still the only authorized publisher until the migration completes.

## Phase 1 -- Pre-flight on SOURCE

- Git state clean: commit or stash everything, push. `git status` must be empty.
- Generate a continuity seed (use the continuity-seed skill) and COMMIT IT TO THE
  REPO -- it is the only way agent context crosses machines.
- Inventory non-portable state. Walk this list explicitly and record findings:
  - Cowork agent memory (MEMORY.md + memory files) -- per-machine, per-space.
    Does NOT travel. Export anything load-bearing into the committed seed.
  - launchd jobs / cron referencing this project (check `~/Library/LaunchAgents`).
  - Credentials: SSH keys, gcloud auth, API keys in env or Keychain. NEVER move
    these through git. List what the target machine must already have.
  - Hardcoded machine paths in scripts (grep for `/Users/`, session paths,
    machine names). Sandbox session paths are always stale -- see machine-bridge.
  - Per-workspace plugin installs and MCP connectors (see workspace-plugin-audit).
  - Scheduled Cowork tasks tied to the source workspace.
- Verify the TARGET machine has push access to the remote before starting --
  and check the remote's ACTUAL protocol first (`git remote -v`), do not assume:
  SSH remote -> `ssh -T git@github.com` on target; HTTPS remote -> `gh auth
  status` (keyring) or a working credential helper on target. Testing the wrong
  protocol produces a false alarm (learned on this skill's first live run).
  This is the most common silent blocker.

## Phase 2 -- Transfer

- On target: `git clone <remote>` into the machine's Cowork projects folder.
- Mount the folder as a Cowork project. Confirm CLAUDE.md and `.claude/rules/`
  load (they travel with the repo -- free).

## Phase 3 -- Rebuild on TARGET

- First session: load the committed continuity seed; rebuild agent memory from it.
- Re-run idempotent setup scripts the project ships (installers, refresh jobs).
- Recreate launchd/cron jobs found in Phase 1 inventory.
- Verify credentials work: one real operation per credential class (a git push of
  a trivial commit, a gcloud call, etc.). Do not assume.
- Reinstall per-workspace plugins the project depends on.

## Phase 4 -- Update the ecosystem (REHOME only)

- Edit the project's CLAUDE.md invariants: every mention of the old machine as
  canonical/publisher flips to the new machine.
- Update `.claude/rules/inbox-registry.md` host column for this project, then run
  the regeneration path (never hand-edit generated tables).
- Grep the repo and ecosystem docs for the old machine's name; update stragglers.
- Publish/push all of the above. Per Phase 0.3: if the project is a distribution
  hub, this publish happens FROM THE SOURCE machine -- it is the source's last act.

## Phase 5 -- Decommission SOURCE (REHOME only)

- Either delete the source working copy, or leave it with a `READ-ONLY MIRROR --
  canonical is <machine>` line at the top of its CLAUDE.md.
- Remove or repoint source-machine launchd jobs that acted on the project.
- Two publishers = split-brain. This phase is not optional in REHOME mode.

## Phase 6 -- Verify

On the target, prove each of these; do not declare done on assumption:

- Repo builds / scripts run.
- One end-to-end publish or deploy succeeds from the target.
- Agent answers a project-history question correctly from the seed.
- Registries (inbox, marketplace, docs) all name the new host.
- Source machine can no longer accidentally publish (REHOME).

## Principles

- Git is the only transport. A project that cannot be cloned is not migratable --
  fix that first.
- The non-portable state inventory IS the migration. Skipping Phase 1's list is
  how state dies silently.
- One canonical machine per project at any moment. The handoff is atomic: until
  Phase 4 publishes, the source is canonical; after, the target is.
- Registry and invariant updates are part of the migration, not a follow-up task.
- Credentials never travel through the repo. The target earns its own.

## Edge Cases

- Project migrates its own distribution channel (e.g. the skill-maker marketplace):
  publish every migration edit from the source FIRST, verify consumers refreshed,
  then hand off publishing rights. The skill you are reading propagated this way.
- Loose folder with no git history worth keeping: `git init`, single initial
  commit, private remote, then proceed -- do not migrate uncommitted history.
- SATELLITE mode later upgraded to REHOME: rerun from Phase 4; Phases 1-3 are
  already done.
- Target machine missing the `claude` CLI or SSH keys: stop and resolve before
  Phase 2; nothing downstream works without them.
