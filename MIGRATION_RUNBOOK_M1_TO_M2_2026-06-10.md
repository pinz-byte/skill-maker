# Migration Runbook -- SKILL MAKER: M1 -> M2 (REHOME)
Updated: 2026-06-10. First live execution of the `project-migrate` skill.
Mode: REHOME. M2 becomes source of truth and sole publisher; M1 decommissioned.

## Already done (this session, on M1's working copy)
- [x] `project-migrate` skill authored + added to `lfp-core` in GROUPS
- [x] Build verified: 3 plugins / 29 skills, fail-loud guard passes
- [x] CLAUDE.md invariants flipped: M2 = source of truth + sole publisher
- [x] inbox-registry.md: SKILL MAKER host -> Cowork M2 (agent-bridge table regenerated)
- [x] workspace-plugin-audit checklist: SKILL MAKER -> M2
- [x] publish.sh comments updated
- [x] Continuity seed committed: SEED_SKILLMAKER_M2_REHOME_2026-06-10.md

## Step 1 -- On M2, BEFORE cloning: verify push access
TRANSPORT CORRECTION (2026-06-10): the remote is HTTPS + gh keyring auth, NOT
SSH. M1's `ssh -T` denial was a false alarm against the wrong protocol.
```bash
gh auth status               # must show: Logged in to github.com account pinz-byte
```
If gh is missing or not authed on M2:
```bash
brew install gh              # if needed
gh auth login                # github.com -> HTTPS -> login with browser -> pinz-byte
gh auth setup-git            # wire git to the keyring credential
```

## Step 2 -- On M1: final publish (M1's last act as publisher)
DONE 2026-06-10 16:17 -- the live auto-publish job shipped the migration commit
(b5b7149). Subsequent doc corrections ship the same way until Step 3 runs.

## Step 3 -- On M1: decommission (immediately after the push lands)
```bash
# kill the auto-publisher -- this is the split-brain guard
launchctl bootout "gui/$(id -u)/com.lfp.skillmaker.publish" 2>/dev/null || true
rm -f ~/Library/LaunchAgents/com.lfp.skillmaker.publish.plist
# keep com.lfp.skill-maker.refresh (consumer refresh) -- M1 still consumes skills
```
Then either delete M1's working copy of the repo, or stop mounting it as a
Cowork project. Do NOT leave it mounted as an editable workspace.

## Step 4 -- On M2: clone + mount
```bash
cd ~/Documents/Claude/Projects   # or M2's projects folder
git clone https://github.com/pinz-byte/skill-maker.git "SKILL MAKER"
```
Open Cowork on M2, add "SKILL MAKER" as a project folder.

## Step 5 -- On M2: first session
Load SEED_SKILLMAKER_M2_REHOME_2026-06-10.md and follow its checklist:
trivial commit + push, one full `./publish.sh`, recreate the github-account
memory, optionally install the publish automation.

## Step 6 -- Verify (do not skip)
- [ ] `./publish.sh` succeeds end-to-end from M2
- [ ] `claude plugin marketplace update lfp-skills` on M1 and M3 picks up a
      test change published from M2
- [ ] `launchctl list | grep skillmaker` on M1 shows NO publish job
- [ ] M2 agent answers "where does SKILL MAKER live?" correctly from the seed
- [ ] agent-bridge messages addressed to SKILL MAKER reference Cowork M2

## Rollback
Everything is one commit. `git revert <migration commit>` from M1, re-run
`./publish.sh` there, and M1 is canonical again. No state is destroyed until
Step 3's working-copy deletion -- do that last for exactly this reason.
