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

## Step 1 -- On M2, BEFORE publishing anything: verify push access
```bash
ssh -T git@github.com        # must greet pinz-byte
```
If this fails, STOP. Fix M2's SSH key for pinz-byte first. Nothing below works
without it, and publishing the flip from M1 first would strand the repo.

## Step 2 -- On M1: final publish (M1's last act as publisher)
Check whether the auto-publish job is live:
```bash
launchctl list | grep skillmaker
```
- If `com.lfp.skillmaker.publish` is listed: it will ship this migration commit
  automatically within 5 minutes. Wait for it (check `git log`), or run
  `./publish.sh` yourself to not wait.
- If not listed: run `./publish.sh` manually from the repo root.

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
git clone git@github.com:pinz-byte/skill-maker.git "SKILL MAKER"
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
