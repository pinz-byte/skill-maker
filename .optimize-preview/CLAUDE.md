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

- Distribution = private git (`git@github.com:pinz-byte/skill-maker.git`), NOT
  iCloud. M1 is source of truth. iCloud + `deploy-plugins.sh` are legacy.
- Output format: `.skill` only. `.plugin` is deprecated (Cowork rejects it).
- Strip non-ASCII before packaging -- Cowork rejects it silently.
- Skill description <= 1024 chars (hard limit, silent failure).
- Skill name must NOT contain "claude" (Cowork reserved word).
- Commit + push after every build -- git is the distribution channel.
- Install is per-workspace + manual (remove + re-add to update). Add from ONE
  folder per machine, not also from iCloud.
- Inbox UUIDs in `.claude/rules/inbox-registry.md` and `agent-bridge/SKILL.md`
  must stay in sync.

## On-demand references (read the file only when the task needs it)

- Build steps, manual zip, git commands: `.claude/build-pattern.md`
- M2/M3 sync + per-workspace install detail: `.claude/distribution.md`
- File tree + version-bump rules: `.claude/file-structure.md`
