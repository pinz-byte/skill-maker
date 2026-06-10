# Continuity Seed -- SKILL MAKER rehome M1 -> M2
Updated: 2026-06-10. Load this in the FIRST Cowork session on M2, then keep it as a historical record.

## What this is
SKILL MAKER's canonical home moved from M1 to M2 on 2026-06-10, executed via the
`project-migrate` skill (its first live run -- the skill was authored for this).

## State at handoff
- Marketplace: 3 plugins, 29 skills. `project-migrate` is new, in `lfp-core`.
- Distribution: GitHub-sourced marketplace `lfp-skills` (repo `pinz-byte/skill-maker`).
  publish.sh = rebuild + commit + push + self-refresh. install-refresh.sh = daily
  consumer refresh (already on all 3 machines). Both scripts are machine-agnostic.
- All "M1 is publisher" invariants in CLAUDE.md, publish.sh comments,
  inbox-registry.md, and workspace-plugin-audit were flipped to M2 in the
  migration commit.
- M1 agent memory was thin at migration time: only `github-account`
  (git username `pinz-byte`, used for skill-maker + carmatch-ai remotes).
  Recreate that one memory on M2; nothing else was load-bearing.

## First M2 session checklist
1. Verify push access: `gh auth status` must show pinz-byte (transport is
   HTTPS + gh keyring, NOT SSH), then one trivial commit + push.
2. Run `./publish.sh` end-to-end once -- this is the proof M2 is the publisher.
3. Recreate the `github-account` memory.
4. Optional: `./automation/install-automation.sh publish` if you want M2 to
   auto-publish every 5 min like M1 did. If not, publish stays manual.
5. Confirm M1 was decommissioned (see MIGRATION_RUNBOOK in repo root).

## Known gotchas carried over
- Skill descriptions <= 1024 chars; non-ASCII stripped at build; never name a
  skill with the reserved word; never hand-edit agent-bridge's registry table.
- Every on-disk skill must be in GROUPS or the build fails loud (by design).
- launchd wrappers must live in ~/Library, never ~/Documents (TCC).
