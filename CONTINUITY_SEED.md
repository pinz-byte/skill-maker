# Continuity Seed -- SKILL MAKER
> Generated: 2026-10-14 21:13 (America/Lima)
> Session: shipped `five-steps` (Musk's algorithm as a skill), rewrote the `lfp-roundtable` mod
> to land ONE verdict message in the chat, rescued two orphan skills from M2 (`cost-gate`,
> `infra-audit`), consolidated M2 to ONE publisher folder, gave plugins history-derived
> versions, brought ALL THREE stores current (CLI on M1/M2/M3 + the Cowork account store),
> installed `lfp-pm` in the account store, turned OFF the 37 standalone duplicates, ran the
> first `/five-steps` pass on the publish chain and deleted everything it found ownerless.

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
Mount "SKILL MAKER". main is at 8a7b6d0 or later; PRs #1 to #7 are MERGED (if #7 is still
open, merge it from M2 with the usual fast-forward block). Nothing else is in flight. All three
stores were verified current on 2026-10-14 ~21:10 Lima: CLI pins on M2 at lfp-core 1.63.0 /
lfp-thinkers 1.43.0 (M1/M3 follow via launchd 08:00); account store shows Lfp core 49 skills, Lfp product 8,
Lfp pm installed; a fresh session lists `cost-gate` under `/cost` and `pm-live` (Lfp pm) under
`/pm`. The account SKILLS store (standalone uploads) is neutralized: 37 entries Disabled, not
deleted. Start at Next Steps; nothing to re-diagnose.

## Project Context
- **Repo:** https://github.com/pinz-byte/skill-maker.git (private; HTTPS on M1/M2, SSH on M3)
- **Branch:** main
- **Primary folder (picker name):** SKILL MAKER
- **Key files:** build-marketplace.py (plugin_version), publish.sh, skill-intent-audit.py,
  five-steps/SKILL.md, mods/lfp-roundtable/hooks/register.tsx, .claude/rules/deploy-target.md

## Current State

### Completed This Session
- `five-steps` skill (lfp-thinkers, REASON lot): Musk's five-step algorithm strictly in order,
  reverse-order detector, one-table verdict. A SKILL, not a hook/mod: mods and function hooks
  run in Claude Code only; the algorithm is judgment, not an invariant. VERIFIED live: `/five`
  on claude.ai lists it from Lfp thinkers.
- `lfp-roundtable` mod rewritten: pane deleted; `/roundtable [seat|todos] <foco>` forks the
  seats in parallel and lands ONE digest in the chat via $.prompt.submit; focus REQUIRED; no
  table state. 8 tests pass. Fixed: seats stuck "trabajando en el chat", focus dropped by
  "Otra vez"/"Mesa completa", one-by-one carry-over.
- M2 consolidated: `~/Projects/SKILL MAKER` (Cowork-mounted) is the ONLY publisher; its 22 dirty
  entries were REAL unpublished work (cost-gate, infra-audit, dependency-audit regrouped to
  lfp-core, 3 SKILL.md edits, APEX_BOOK_MOD_BRIEF), published as 401ab2e. Documents clone
  renamed in place to `_retired_skill-maker_2026-10-14` (iCloud-evicted; never hash it).
- Plugin versions: plugin.json/marketplace.json carry `1.N.0`, N = commits touching the plugin's
  sources (+ builder) PLUS one while a change is uncommitted (so the bump lands in the same
  publish); shallow clones keep the last published numbers. The CLI pins by this version.
- cost-gate had `intent: gate` (not a lot) and was silently absent from CATALOG.md; fixed to
  `audit`; the audit script now FAILS the build on an unknown lot.
- Stores: M1 (8 plugins), M2 (all), M3 (7) at the versioned pins. Account store refreshed via
  Update on Lfp core (46 -> 49), which pulled the whole snapshot (Lfp product 9 -> 8).
- `lfp-pm` installed in the account store from the web Discover (Add; 1.40.0, 1 skill). The
  desktop app showed it "Disabled" and inert; the web Add worked. Done by the Claude in Chrome
  panel from paste-ready prompts (this cloud session has no browser tools).
- Third store (account SKILLS store, standalone uploads) neutralized: `pm`, `pm-live`,
  `astrodiary-ds-enforcer`, "Lfp design (Local uploads)" and 34 more standalone skills turned
  OFF (37 Disabled). The `/` menu now resolves each name to its marketplace plugin only
  (`/pm` -> pm-live from Lfp pm; `/council` -> 7 entries, all Lfp apex). NOT deleted: the
  Chrome agent refuses permanent deletions and deletion is the human's call.
- First `/five-steps` pass on the publish chain (22 parts, one table). Verdict: the live chain
  is correct and short; the debris around it had no owner. PR #6 deleted 23 files (-3663
  lines): CATALOG.html + generator, plugin-packaging.md (dead zip channel, loaded every
  session), pre-commit.sh (never installed), 16 one-shot migration scripts from 2026-08,
  three committed backups; dropped publish.sh's `--scope project` loop (resolves against CWD,
  never reached the AVT / Carta natal pins); CATALOG.md no longer @-imported into CLAUDE.md.
  Kept: dedupe-check.py (workspace-plugin-audit runs it). PR #7: Kiro mirror deleted (see
  Decisions), catalog header without a date, seed.
- All three stores current again after PR #6: M2 CLI pins at lfp-core 1.63.0 / lfp-thinkers
  1.43.0 (nine groups +1 because the builder changed); M1/M3 via launchd 08:00.

### In Progress
- (none)

### Blocked / Deferred
- Desktop app 2.37337.1: marketplace-level "Check for updates" fails every time ("Couldn't
  check for updates. Try again."); "Add marketplace" answers "already added"; web UI has no
  update control. Workaround that works: Update on any installed plugin pulls the whole
  snapshot. Documented in deploy-target.md. Report to Anthropic if it persists.
- 37 standalone skills sit Disabled in the account skills store (duplication debt). Permanent
  deletion is the user's decision; when taken, do it in bulk from Customize -> Plugins/Skills
  -> Disabled. Until then they cost nothing and shadow nothing.
- M3's repo clone sits inside iCloud Documents (mirrored on M2 as "Documents - LFP-M3"); M3 is a
  consumer and needs no clone. Retire it when on M3.
- Three Carta natal OS worktrees pin lfp-core/lfp-thinkers at project scope; one got updated by
  M2's publish, the rest only update from their folders. Delete those project-scope pins.
- M3 fetches the marketplace via SSH while the invariant says HTTPS; works, rotate-risk.
- M2's `~` is itself a git repo with no remote: every stray folder under it looks like "a repo on
  main" and swallowed two command blocks today. Decide if ~/.git is intentional (dotfiles).

## Decisions Made
- Decision: Musk's algorithm ships as a skill, not a hook/mod -- Reason: coverage (mods/hooks
  are Claude Code only) and shape (judgment, not a checkable invariant).
- Decision: roundtable pane deleted, one digest to chat -- Reason: the pane killed the value;
  each call is one task, nothing to close.
- Decision: ONE publisher folder on M2 = the Cowork-mounted one -- Reason: authoring and
  publishing in different folders left two skills unpublished for weeks.
- Decision: account plugin store is per-ACCOUNT -- Reason: proven again: web, desktop and a
  cloud session read the same snapshot. One refresh, any machine.
- Decision: history-derived plugin versions, never hand-bumped -- Reason: Cowork sync keys on a
  version bump; the CLI, once a version exists, pins by it, so it must bump with the content.
- Decision: Kiro channel = `install-kiro-skills.sh` ONLY (clones the repo, copies canonical
  `<skill>/` dirs); the hand-copied `team-skills/.kiro/` mirror is deleted -- Reason: Kiro is
  alive (user, 2026-10-14) and the mirror had already drifted (dependency-audit 7 weeks
  behind). Same failure class the marketplace was built to kill.
- Decision: team toolkit channel stays (build-team-toolkit.py, generated from canonical) --
  Reason: user wants consumers for it; it costs nothing until someone runs
  `marketplace add subascorp/ai-toolkit`. Onboarding people is the missing part, not code.
- Decision: builder path stays in every group's version paths -- Reason: builder changes alter
  output. Known cost: any builder tweak bumps all nine groups (nine harmless re-downloads).

## Gotchas Discovered
- Gotcha: `*.plugin` zombies are gitignored, survive fast-forwards, and the dead-channel guard
  halts publish.sh BEFORE commit -- Fix: `find . -maxdepth 1 -name '*.plugin' -delete`.
- Gotcha: `git status` on an iCloud-evicted clone hangs (321 dataless files) -- Fix: never hash
  it; `git ls-files --others --exclude-standard`; rename in place.
- Gotcha: "HEAD is an ancestor of main" proves commits, NOT uncommitted edits -- Fix: diff
  before retiring a clone (a Sep-17 projectmd-optimizer pass lived only in the retired one).
- Gotcha: `metadata.intent` outside LOTS silently dropped the skill from CATALOG.md -- Fix: the
  check now fails loud.
- Gotcha: the CLI pins by plugin.json `version` once present ("updated from <sha> to 1.62.0");
  a version computed from HEAD alone lags content by one publish -- Fix: count the pending
  change (38d4cd6). A shallow clone (cloud, depth 50) undercounts -- Fix: keep prior (56bb194).
- Gotcha: desktop app "v5 / updated N hours ago" is the store's own counter; marketplace
  "Check for updates" is broken; a plugin's Update pulls the whole snapshot.
- Gotcha: $.prompt.submit from a mod lands as "The lfp-roundtable plugin sent a message"; if
  Claude reads but does not integrate the digest, set `asUser: true`.
- Gotcha: zsh aborts a pasted line on an unmatched glob; a polluted clipboard prepends junk to
  `claude`; a `~/.git` makes any subfolder answer "Already on main" with no remote.
- Gotcha: the claude.ai `/` menu omits the plugin label when a name resolves to ONE entry
  (`cost-gate` looked "standalone"; it exists only as lfp-core:cost-gate). A missing label is
  uniqueness, not a stray upload. Check GROUPS in build-marketplace.py before believing a
  "duplicate" flag (the Chrome agent also flagged `human-reactor`; it ships in lfp-copy).
- Gotcha: desktop app rows that read "Disabled" for lfp-pm / inbox / compass / apex-book are
  inert (click does nothing); install from the WEB Discover instead. Hooks-only mods stay
  uninstalled there on purpose.
- Gotcha: `claude plugin update --scope project` reads the `enabledPlugins` entry in the
  folder's `.claude/settings.local.json` and reports the cached version; `uninstall --scope
  project` finds no installation and suggests `--scope user` -- NEVER run that, it removes the
  plugin from the machine. The entry is inert; delete the line by hand if wanted.
- Gotcha: a dated "Generated <date>" header in a generated file makes two machines (or two
  timezones) commit a content-free rebuild -- Fix: no date in CATALOG.md's header (PR #7).

## Uncommitted Changes
- None.

## Next Steps (Ordered)
1. Verify `/roundtable todos <foco>` in a fresh Claude Code session on M1; flip `asUser` if needed.
2. Decide on permanently deleting the 37 Disabled standalone skills (bulk, user's call).
3. Toolkit consumers: onboard the first team member (`claude plugin marketplace add
   subascorp/ai-toolkit`); until then the channel is idle by design.
4. On M3: retire the iCloud clone; consumer refresh only. On M2: decide about `~/.git`.
5. Delete the Carta natal OS project-scope plugin pins (from THEIR folders, not from here).
6. Debt, not urgent: `CORE_SKILLS` in install-kiro-skills.sh and `TEAM_GROUPS` in
   build-team-toolkit.py are two hand-curated "team-safe" lists that can drift apart.

## Key Code / Config
- Consumer refresh (any machine): `claude plugin marketplace update lfp-skills && claude plugin list 2>&1 | grep -oE '[A-Za-z0-9_-]+@lfp-skills' | sort -u | while read -r p; do claude plugin update "$p"; done`
- Account store refresh: desktop app, Customize -> Plugins -> Yours -> any installed lfp-* -> Update.
- Builder version rule: `plugin_version(paths, prior)` = `1.<committed + pending>.0`; shallow -> prior.
- Mods are Claude Code only: lfp-roundtable, lfp-inbox, lfp-compass, lfp-apex-book stay
  uninstalled in the desktop app on purpose.
