# Team Toolkit — Publish Runbook (LFP, run natively on M2)

Updated: 2026-07-02

One-time setup, then a 3-command refresh cycle. The team repo is a BUILD
ARTIFACT — skill sources stay in SKILL MAKER (single source of truth).

## One-time: private repo in the EXISTING org

DECIDED 2026-07-02: org-level, in the company's existing org **`subascorp`**
(do NOT create a new org; subascorp already hosts legacy-vmc-subastas etc.).

RECON 2026-07-02 (verified in browser, logged in as pinz-byte):
- pinz-byte is a MEMBER of subascorp, not Owner. Owners: bcrr666,
  integraciones-subastop, subastin.
- Members CAN create org repos (subascorp shows in the /new owner dropdown).
- Members CANNOT create teams (new-team 404s). Teams: administrators (secret),
  only-legacy-vmc, vmc-core-dev. No AI team exists.
- Org base permission is effectively READ: pinz-byte sees all 22+ private repos
  from a single team membership. Therefore ANY private repo in subascorp,
  including ai-toolkit, is readable by all 11 org members.

ACCEPTED CONSEQUENCE: "AI team only" is enforced at onboarding level (who gets
the runbook + marketplace command), not by repo ACL. Changing org base
permission is an owner-level, org-wide action -- not worth it for this repo.

1. Create the private repo and push (LFP alone, no owner needed):

```bash
cd "/Users/lfp/Projects/SKILL MAKER"
python3 build-team-toolkit.py
cd team-toolkit
git init -b main && git add -A && git commit -m "feat: subastop-ai team toolkit v1"
gh repo create subascorp/ai-toolkit --private --source . --push
```

2. Optional (needs an owner, e.g. bcrr666): create team `ai` for membership
   semantics and future tightening. Not required for access -- org members
   already read the repo via base permission:

```bash
# owner runs:
gh api -X POST orgs/subascorp/teams -f name=ai -f privacy=closed
gh api -X PUT orgs/subascorp/teams/ai/repos/subascorp/ai-toolkit -f permission=pull
gh api -X PUT orgs/subascorp/teams/ai/memberships/<github-username>
```

3. Onboard the AI team members with TEAM_ONBOARDING.md (repo README). Anyone
   already in the org needs no access step at all.

## Refresh cycle (after editing any included skill)

```bash
cd "/Users/lfp/Projects/SKILL MAKER"
python3 build-team-toolkit.py
cd team-toolkit && git add -A && git commit -m "chore: toolkit refresh" && git push
```

Team picks it up via `claude plugin marketplace update subastop-ai`.

## Invariants

- team-toolkit/ is generated — never hand-edit it; edit sources + rebuild.
- Curated list lives in TEAM_GROUPS (build-team-toolkit.py). Adding a skill to
  the team = add it there, audit its SKILL.md for personal references first
  (M1/M2/M3, Notion UUIDs, POPs/Symbios, iCloud paths), rebuild, push.
- Team-ONLY skill sources (not distributed via lfp-skills) live in
  `team-skills/<name>/` — NOT repo root, or build-marketplace.py fails loud on
  an ungrouped skill. skill_src() resolves root first, then team-skills/.
  Current team-only source: ds-enforcer (copied from plugin cache 2026-07-03,
  "approved by LFP" de-personalized).
- Skills whose content NEEDS non-ASCII glyphs (ds-enforcer: DS separators,
  UI glyphs) go in KEEP_UTF8 — the ASCII strip would corrupt the spec. The
  marketplace channel tolerates UTF-8; the strict ASCII rule was the legacy
  .plugin zip channel.
- NEVER add: apex-*, agent-bridge, inbox-triage, pm, reentry, machine-bridge,
  workspace-plugin-audit, skill-miner, toolbox, herald-*, carmatch-intel.
- team-toolkit/ is gitignored in the SKILL MAKER repo (it has its own git).
