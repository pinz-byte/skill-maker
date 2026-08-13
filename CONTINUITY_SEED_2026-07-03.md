# Continuity Seed -- SKILL MAKER
> Generated: 2026-07-03 10:20
> Session: VMC's agent-bridge concurrency patch reviewed, canonized, published (c6b6dbe); legacy .skill channel purged from git tracking.

## Mount Check (READ AND ACT ON THIS FIRST)
Run: ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$'
Required below: "SKILL MAKER". If missing, STOP and ask the user to add it in the Cowork picker.

## Mount Manifest
REQUIRED:
- SKILL MAKER -- the skill-authoring repo; all edits, build, and publish happen here
  -- landmark: build-marketplace.py, publish.sh, agent-bridge/SKILL.md
OPTIONAL:
- (none this session)
NOT mounted this session but needed next time:
- (none identified)

## Resume Instructions
Everything from the VMC patch cycle is CLOSED (published + pushed in c6b6dbe, 2026-07-03 10:19).
No in-flight work. Next session starts fresh from the Next Steps backlog below -- item 1 is
verifying the patch propagated to M1/M3 (especially VMC on M3, the patch author).

## Project Context
- **Repo:** pinz-byte/skill-maker (private GitHub, HTTPS + gh keyring; M2 is sole publisher)
- **Branch:** main (in sync with origin/main)
- **Primary folder (picker name):** SKILL MAKER
- **Key files:** agent-bridge/SKILL.md, build-marketplace.py, publish.sh, .claude/rules/inbox-registry.md, SKILL_PROPOSALS_2026-07-02.md

## Current State

### Completed This Session
- Processed VMC's inbox message (agent-bridge concurrency patch, 4 changes): APPROVED, canonized
  onto the 427-line canonical SKILL.md (VMC's base was a stale 255-line copy). SEND Step 0
  (check own inbox first), RECEIVE Step 4 immediate per-message READ marking, new RECEIVE Step 6
  re-fetch-before-report gate (old Step 6 -> Step 7), new principle "Assume concurrency, not turns".
- Marked VMC's message READ; sent full response to VMC inbox (no response expected back).
- Root cause of VMC's stale copy found: legacy .skill channel -- 27 .skill files were tracked in
  the repo root, agent-bridge.skill among them at the old 255-line body.
- Legacy purge: git rm --cached *.skill + "*.skill" in .gitignore (files remain on disk, untracked).
- Hygiene gate run: TEAM_ONBOARDING.md dated (2026-07-02); secret scan on team-toolkit files clean.
- Published: commit c6b6dbe (2026-07-03 10:19) -- agent-bridge patch, auditor-general description
  compression, SKILL_PROPOSALS_2026-07-02.md, TEAM_ONBOARDING.md, build-team-toolkit.py,
  docs/team-toolkit-publish.md, .gitignore (+team-toolkit/, +*.skill), .skill purge. Pushed.

### In Progress
- (nothing)

### Blocked / Deferred
- CONTINUITY_SEED.md bare-name advisory: tracked under bare name, but CLAUDE.md auto session
  protocol references that exact name. Renaming requires a CLAUDE.md update in the same commit.
  POPs' call, non-urgent.

## Decisions Made
- Decision: do NOT commit/install VMC's packaged agent-bridge.skill -- Reason: built on stale
  255-line base; canonical repo patch supersedes it. POPs should discard his copy.
- Decision: canonize at parity with VMC's verified patch; leave OUT the "verified against fresh
  fetch at [HH:MM]" template line -- Reason: ship what was production-verified; that line is the
  designated fix IF the false-pending failure recurs post-patch.
- Decision: purge legacy .skill files from git tracking in the same publish -- Reason: the legacy
  channel was actively distributing the stale skill body that caused the VMC incident.
- Decision: no per-workspace reinstall checklist for the patch -- Reason: marketplace daily
  auto-refresh propagates with no per-workspace re-add (confirmed 2026-06-04).

## Gotchas Discovered
- Gotcha: sandbox git commands on this repo create .git/index.lock the sandbox cannot unlink,
  blocking native publish.sh -- Fix: native `rm -f .git/index.lock`; from sandbox always use
  `git --no-optional-locks` read-only commands. Saved to persistent memory (sandbox-git-lock).
- Gotcha: `claude plugin marketplace update lfp-skills` reports success even when it refreshes to
  an old commit -- a green update is NOT proof the new version propagated. Verify against git log.
- Gotcha: user pasted stale terminal scrollback that looked like a fresh run -- verify claimed
  command execution against filesystem/git state, not against the paste.

## Uncommitted Changes
CONTINUITY_SEED.md (this file) + CONTINUITY_SEED_2026-06-23.md (archive) -- will ride the next publish.

## Next Steps (Ordered)
1. Verify patch propagation on M1/M3: `claude plugin marketplace update lfp-skills` there, or wait
   for the daily refresh; confirm VMC's workspace surfaces the new agent-bridge (Step 0 present).
2. Remind POPs to discard VMC's agent-bridge.skill artifact (lives outside this repo, M3/VMC side).
3. Pick next build from SKILL_PROPOSALS_2026-07-02.md (skill-miner backlog, 5 clusters).
4. Optional: resolve the CONTINUITY_SEED.md bare-name advisory (rename + CLAUDE.md update together).

## Key Code / Config
- Publish (native M2 terminal only, never sandbox):
  `cd "/Users/lfp/Projects/SKILL MAKER" && ./publish.sh`
- VMC inbox UUID (for bridge replies): 360da327-abb1-81bf-80d5-d910c59b9476
- SKILL MAKER inbox UUID: 360da327-abb1-8196-b98d-cfc86bbe0ec6
