# SKILL MAKER — Project Context

@DISPATCH_INBOX.md

Skill authoring lab for the LFP ecosystem. Produces `.skill` files that extend
Claude agents across Cowork (M1/M2/M3) and Claude.ai Chat.

## Behavior rules

1. Think before coding. Don't assume -- state assumptions; if ambiguous, ask or
   present options instead of picking silently. If unclear, stop and name it.
   Flag a simpler approach when one exists.
2. Simplicity first. Minimum that solves the problem. No speculative features,
   abstractions for single-use code, or unrequested flexibility.
3. Surgical changes. Touch only what the request requires. Don't refactor
   adjacent working code; remove only orphans your change created.
4. Goal-driven execution. Define a verifiable success criterion before coding,
   then loop until it passes.

<!-- Add project-specific behavior rules below this line. -->

## Invariants (every session)

- Distribution channel = a **Claude Code plugin marketplace** (`lfp-skills`),
  not loose files. `build-marketplace.py` generates `.claude-plugin/marketplace.json`
  + the `plugins/` tree from each `<skill>/SKILL.md`. `publish.sh` rebuilds +
  commits + pushes it. Private git (`git@github.com:pinz-byte/skill-maker.git`)
  is the transport; M1 is source of truth. iCloud + `deploy-plugins.sh` are legacy.
- Every skill MUST be assigned to a plugin in `GROUPS` (build-marketplace.py).
  The builder now **fails loud** if any on-disk skill is ungrouped -- this is the
  guard against the 2026-06-04 gap where 6 built skills silently never propagated.
  Adding a new skill = drop its dir + add it to a GROUP, or the build halts.
- Publish from M1 only: `./publish.sh` (rebuild + commit + push, one command).
- M2/M3 stay current via `./install-refresh.sh` (run once per machine): a daily
  launchd job that does `git pull` + `claude plugin marketplace update lfp-skills`.
  Whether a per-workspace re-add is STILL required on top of marketplace
  auto-update is unconfirmed as of 2026-06-04 -- verify via the refresh log before
  trusting auto-update alone. The older per-`.skill` path (`ship-skill.sh` /
  `sync-skills.sh`) still exists but the marketplace is the live channel.
- Strip non-ASCII before packaging -- Cowork rejects it silently (builder does this).
- Skill description <= 1024 chars (hard limit, silent failure).
- Skill name must NOT contain "claude" (Cowork reserved word). NB: the skill is
  `projectmd-auditor`, NOT "claudemd-auditor".
- Inbox UUIDs in `.claude/rules/inbox-registry.md` and `agent-bridge/SKILL.md`
  must stay in sync.

## On-demand references (read the file only when the task needs it)

- Build steps, manual zip, git commands: `docs/build-pattern.md`
- M2/M3 sync + per-workspace install detail: `docs/distribution.md`
- File tree + version-bump rules: `docs/file-structure.md`
