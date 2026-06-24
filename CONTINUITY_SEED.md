# Continuity Seed -- SKILL MAKER
> Generated: 2026-06-23 19:17
> Session: revamped continuity-seed + reentry with mount-gating; added CLAUDE.md auto session protocol; published to M2.

## Mount Check (READ AND ACT ON THIS FIRST)
Run: ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$'
Required below: "SKILL MAKER". If missing, STOP and ask the user to add it in the Cowork picker.

## Mount Manifest
REQUIRED:
- SKILL MAKER -- the skill-authoring repo; all edits, build, and publish happen here
  -- landmark: build-marketplace.py, publish.sh, continuity-seed/SKILL.md
OPTIONAL:
- (none this session)
NOT mounted this session but needed next time:
- (none -- single-repo session)

## Resume Instructions
Mount "SKILL MAKER". This session's work is shipped and verified; there is no open build. The next
session's real job is to VERIFY the auto-protocol actually fires: start fresh and confirm the agent
runs the mount-check on turn one without being told. If it doesn't fire reliably, build the
SessionStart hook (see Next Steps #2).

## Project Context
- **Repo:** skill-maker (github.com/pinz-byte/skill-maker, HTTPS + gh auth)
- **Branch:** main (clean, pushed -- HEAD 3606d94)
- **Primary folder (picker name):** SKILL MAKER
- **Key files:** continuity-seed/SKILL.md, reentry/SKILL.md, build-marketplace.py, CLAUDE.md

## Current State

### Completed This Session
- continuity-seed: re-homed into the M2 repo (was orphaned -- not tracked, not in any GROUP),
  added Step 1.5 Mount Manifest capture, Step 4 load-time mount gate, fixed rotating-session-path
  bug (record stable picker names), added a full worked-example seed. Added to lfp-core GROUP.
- reentry: added Step 0 mount-check gate (detect mounts, compare to last seed Manifest, stop on
  missing REQUIRED folder), MOUNTS line in the hutch, "mounts gate everything" principle.
- CLAUDE.md: added "Auto session protocol" -- auto mount-check on session start, auto-seed at
  ~70% context / wrap-up. Portable note for other projects.
- Published via ./publish.sh on M2. Verified committed HEAD tree contains all three artifacts;
  working tree clean. lfp-core now 21 skills, 32 total.

### In Progress
- (nothing -- session is at a clean stopping point)

### Blocked / Deferred
- SessionStart hook NOT built. Open question whether Cowork sessions fire Claude Code
  .claude/settings.json hooks. The CLAUDE.md directive is behavioral, not hard-enforced.

## Decisions Made
- Decision: re-home continuity-seed into M2 repo rather than patch the cached copy -- Reason: the
  cache is regenerated on build; a patch there is throwaway. Source must live in the repo to persist.
- Decision: put the hard mount gate in reentry (Step 0), not only in seed prose -- Reason: a seed
  is passive data and cannot force the next session to check; reentry runs as logic on session start.
- Decision: "auto" = CLAUDE.md standing instruction, not a hook (for now) -- Reason: hook firing in
  Cowork is unverified; chose the reliable lever and flagged the hook as the stronger next step.

## Gotchas Discovered
- Gotcha: continuity-seed was running from a stale deployed cache with no repo source (orphaned in
  the M1->M2 rehome) -- Fix: created the canonical source + wired it into GROUPS.
- Gotcha: seeds stored absolute /sessions/<name>/mnt paths that rotate every session and die on load
  -- Fix: record folders by stable picker name + a landmark file.
- Gotcha: reentry SKILL.md has ~272 pre-existing non-ASCII chars (box-art borders, em-dashes) the
  builder strips, so the deployed hutch renders borderless. Pre-existing, not fixed this session.
- Gotcha: THIS M2 session still runs the pre-publish cached skills -- the new behavior only loads in
  a fresh session.

## Uncommitted Changes
(none -- working tree clean, HEAD 3606d94 pushed)

## Next Steps (Ordered)
1. Open a FRESH session and verify the auto mount-check fires on turn one unprompted. That is the
   real acceptance test for this whole effort.
2. If it doesn't fire reliably, build a SessionStart hook in .claude/settings.json that runs the
   mount-check as a shell command and injects the result into context. Confirm whether Cowork
   honors the hook.
3. Optional: ASCII-ify reentry's hutch box-art so the deployed version keeps its borders.
4. Optional: drop the "Auto session protocol" block into other projects' CLAUDE.md (AVT, extractor)
   where the mount errors actually bite.

## Key Code / Config
Mount-detection command (used by both skills and the auto-protocol):
  ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$' | sort -u
Publish (native on M2 only -- sandbox cannot build, no unlink):
  cd ~/Projects/SKILL\ MAKER && ./publish.sh
