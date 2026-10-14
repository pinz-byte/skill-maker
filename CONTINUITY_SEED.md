# Continuity Seed -- SKILL MAKER
> Generated: 2026-10-14 17:50 (America/Lima)
> Session: shipped `five-steps` (Musk's algorithm as a skill), rewrote the `lfp-roundtable` mod
> to land ONE verdict message in the chat, rescued two orphan skills from M2 (`cost-gate`,
> `infra-audit`), consolidated M2 to ONE publisher folder, refreshed M1/M2/M3 CLIs to `dd9be27`.
> Found the Cowork ACCOUNT store stuck at the `d3010d3` snapshot (46 lfp-core skills vs 49 on
> main) with the desktop app failing "Couldn't check for updates". PR #2 open with the fix.

## Mount Check (READ AND ACT ON THIS FIRST)
Run: ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$'
REQUIRED below is "SKILL MAKER". If missing, STOP and ask the user to add it in the Cowork picker.
Do NOT proceed on partial mounts. (A cloud session whose working dir IS the repo clone satisfies it.)

## Mount Manifest
REQUIRED:
- SKILL MAKER -- the skill/marketplace source of truth. On M2 this is ~/Projects/SKILL MAKER
  (the Cowork-mounted folder; ~/Documents/Claude/Projects/skill-maker was retired 2026-10-14).
  -- landmarks: build-marketplace.py, publish.sh, .claude-plugin/marketplace.json, CATALOG.md
OPTIONAL:
- (none this session)
NOT mounted this session but needed next time:
- (none identified)

## Resume Instructions
Mount "SKILL MAKER". main is at dd9be27. PR #2 (branch claude/busy-allen-tqhm01) is OPEN and
mergeable: history-derived plugin versions + the cost-gate catalog fix + this seed. Start at
Next Step 1 (merge PR #2, publish from M2), then Next Step 2 (the account-store refresh).
Do not re-diagnose the clones on M2 -- it is fully mapped in Decisions and Gotchas.

## Project Context
- **Repo:** https://github.com/pinz-byte/skill-maker.git (private; HTTPS on M1/M2, SSH on M3)
- **Branch:** main at dd9be27; PR #2 head on claude/busy-allen-tqhm01
- **Primary folder (picker name):** SKILL MAKER
- **Key files:** build-marketplace.py, publish.sh, skill-intent-audit.py, five-steps/SKILL.md,
  mods/lfp-roundtable/hooks/register.tsx, .claude/rules/deploy-target.md

## Current State

### Completed This Session
- `five-steps` skill (lfp-thinkers, REASON lot): Musk's five-step algorithm strictly in order,
  reverse-order detector, one-table verdict. Shipped as a SKILL, not a hook/mod: mods and
  function hooks run in Claude Code only; the algorithm is judgment, not an invariant.
- `lfp-roundtable` mod rewritten: pane deleted; `/roundtable [seat|todos] <foco>` forks the
  seats in parallel and lands ONE digest in the chat via $.prompt.submit; focus is REQUIRED;
  no table state. 8 tests pass (claude plugin test). Fixed: seats stuck "trabajando en el
  chat" forever, focus dropped by "Otra vez" / "Mesa completa", one-by-one carry-over.
- M2 consolidated: three clones found; `~/Projects/SKILL MAKER` (Cowork-mounted) is the ONLY
  publisher; 22 dirty entries there were REAL unpublished work (cost-gate, infra-audit,
  dependency-audit regroup to lfp-core, 3 SKILL.md edits, APEX_BOOK_MOD_BRIEF) -- rescued and
  published as 401ab2e; CLAUDE.md invariant updated in dd9be27. Documents clone renamed in
  place to `_retired_skill-maker_2026-10-14` (iCloud-evicted; never hash it).
- CLIs: M1 (8 plugins), M2 (all), M3 (7 plugins) at dd9be27. Zombie `.plugin` files on M1
  deleted (they broke the build's dead-channel guard).
- VERIFIED LIVE via Claude in Chrome on claude.ai: `/five` shows five-steps (Lfp thinkers).
  The account store has it. `/cost` does NOT show cost-gate: store snapshot is `d3010d3`.
- PR #2 (open): (a) plugin.json/marketplace.json carry `version: 1.N.0`, N = commits touching
  that plugin's sources (+ builder); deterministic across rebuilds; validator warnings gone.
  (b) cost-gate had `intent: gate` (not a lot) and was silently absent from CATALOG.md;
  fixed to `audit`; skill-intent-audit.py now FAILS the build on an unknown lot.

### In Progress
- PR #2 awaiting merge: https://github.com/pinz-byte/skill-maker/pull/2
- Account store refresh: desktop app marketplace "Check for updates" fails with the toast
  "Couldn't check for updates. Try again." Payload verified clean (marketplace.json identical
  to the snapshot that ingested fine; 89 frontmatters strict-YAML valid; validate passes).

### Blocked / Deferred
- Desktop app: the marketplace-level refresh control was not found in the current UI
  (Yours/Discover tabs; plugin page shows only Update + "..." with Remove/Edit/Duplicate).
  Docs name "Check for updates" and "Sync automatically" on the marketplace (Cowork guide)
  but not where they sit. The WEB UI (claude.ai Customize > Plugins) has NO refresh control
  at all (verified by Claude in Chrome). App build 2.31226.0 (2026-10-08) fixed "marketplace
  refreshes sometimes failing" -- update the app first.
- `lfp-pm` (pm-live) is NOT installed in the account store (listed under skill-maker source as
  not installed). The GROUPS comment says it was created to replace the stale `pm`; the
  replacement never happened. Install it from Discover or decide it is not wanted.
- "Lfp design (Local uploads)" in Yours is a hand-uploaded duplicate of marketplace lfp-design:
  duplication debt; remove once the marketplace copy is confirmed loading.
- M3's repo clone sits inside iCloud Documents (mirrored on M2 as "Documents - LFP-M3");
  .git in iCloud is a corruption hazard. M3 is a consumer; it needs no clone.
- Three Carta natal OS worktrees pin old lfp-core/lfp-thinkers at project scope; delete those
  project-scope pins so user scope (daily job) serves them.
- M3 fetches the marketplace via SSH while the invariant says HTTPS; works today, rotate-risk.

## Decisions Made
- Decision: Musk's algorithm ships as a skill, not a hook/mod -- Reason: coverage (mods/hooks
  are Claude Code only) and shape (judgment, not a checkable invariant); roundtable mod already
  consumes thinker skills as seats.
- Decision: roundtable pane deleted, one digest to chat -- Reason: the pane was the primitive
  that killed the value; each /roundtable call is one task, nothing to close.
- Decision: ONE publisher folder on M2 = the Cowork-mounted one -- Reason: authoring and
  publishing in different folders is how two skills sat unpublished for weeks.
- Decision: account plugin store is per-ACCOUNT -- Reason: proven again today: web, desktop and
  this cloud session all read the same d3010d3 snapshot. One refresh, any machine.
- Decision: plugin manifests carry a history-derived version -- Reason: Cowork's sync model
  keys on a "version bump" (support article 13837433); the CLI pins by commit and ignores it.

## Gotchas Discovered
- Gotcha: `*.plugin` zombies are gitignored, survive fast-forwards invisibly, and the builder's
  dead-channel guard halts publish.sh BEFORE commit -- Fix: `find . -maxdepth 1 -name '*.plugin' -delete`.
- Gotcha: `git status` on an iCloud-evicted clone hangs for minutes (321 dataless files) --
  Fix: never hash it; `git ls-files --others --exclude-standard` lists untracked without reads;
  rename in place, do not move out of iCloud.
- Gotcha: "HEAD is an ancestor of main" proves commits, NOT uncommitted edits to tracked files
  (a Sep-17 projectmd-optimizer pass lived only in the retired clone) -- Fix: diff before retiring.
- Gotcha: `metadata.intent` outside LOTS silently drops the skill from CATALOG.md while the build
  says PASS -- Fix: in PR #2 the check fails loud.
- Gotcha: the desktop app's "v5 / updated N hours ago" is the store's OWN counter; it does not
  read plugin.json versions (none existed). lfp-core 46 skills = d3010d3; main has 49.
- Gotcha: $.prompt.submit from a mod lands as "The lfp-roundtable plugin sent a message";
  if Claude reads but does not integrate the digest, set `asUser: true` (one line).
- Gotcha: zsh aborts a pasted line on an unmatched glob (`no matches found`); a polluted
  clipboard prepends junk to `claude` -- paste lines starting at the command.

## Uncommitted Changes
- None. Everything is on main (dd9be27) or on PR #2's branch.

## Next Steps (Ordered)
1. Merge PR #2. On M2, `~/Projects/SKILL MAKER`: `git pull && ./publish.sh` (commits one
   lfp-core version bump). M1/M3: the consumer refresh line or the daily job.
2. Account store: update the desktop app to >= 2.31226.0, then retry Update on Lfp core (now
   that manifests carry versions). If still failing: `+ Add` > "Add marketplace" with
   `pinz-byte/skill-maker` (idempotent if already added) and look for "Check for updates" /
   "Sync automatically" there. Last resort: Remove + re-add one small plugin (lfp-labs) as canary.
3. Install `lfp-pm` in the account store or decide it is not wanted; remove "Lfp design (Local
   uploads)" once marketplace lfp-design loads in a fresh session.
4. First real `/five-steps` pass: the publish chain itself (deploy-target.md's three-store ritual).
5. Verify `/roundtable todos <foco>` in a fresh Claude Code session on M1; flip `asUser` if needed.
6. On M3: retire the iCloud clone; consumer refresh only.

## Key Code / Config
- Consumer refresh (any machine): `claude plugin marketplace update lfp-skills && claude plugin list 2>&1 | grep -oE '[A-Za-z0-9_-]+@lfp-skills' | sort -u | while read -r p; do claude plugin update "$p"; done`
- Builder version rule: `plugin_version(paths)` = `1.<git rev-list --count HEAD -- paths>.0`.
- Mods are Claude Code only (hooks); Cowork never runs them: lfp-roundtable, lfp-inbox,
  lfp-compass, lfp-apex-book stay uninstalled in the desktop app on purpose.
