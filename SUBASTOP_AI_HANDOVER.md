<!-- last_updated: 2026-07-08 -->
# Subastop AI Team -- Toolkit Handover

Produced by `project-handover` skill. Covers the `subastop-ai` skill marketplace
(`subascorp/ai-toolkit`) handed to Julio Herrera, Aaron Coorahua, and Abraham
Huacchillo. This is a documentation + verification package, not just a doc -- Phase 2
below tells you exactly what's confirmed vs. what still needs a native check.

Scope note: this covers the **AI toolkit handover**, which is the piece with
concrete artifacts (a repo, a marketplace, an onboarding doc). If "the Subastop
project" also meant handing over application codebases (AVT, CarMatch, VMC, etc.),
that is a separate, larger handover this document does not cover -- flag if you want
that run too.

---

## 1. Project Overview

**What it is:** a curated, read-only Claude Code/Cowork skill marketplace built for
the Subastop AI team, so they get a working subset of the LFP ecosystem's skills
(oversight thinkers, git/audit discipline, design-system enforcement) without access
to LFP's personal-layer skills (agent-bridge, reentry, machine-bridge, etc.).

**Why it exists:** `lfp-skills` (the full marketplace) mixes personal infrastructure
with generically useful skills. `subastop-ai` is the curated, de-personalized subset
safe to hand to people outside LFP's own machines.

**Current state:** published and live. Repo `subascorp/ai-toolkit` created
2026-07-02, `subastop-design` (ds-enforcer) added 2026-07-03. No changes since.

**Outgoing owner:** LFP (pinz-byte), sole maintainer and publisher. Ongoing role:
still the only one who can rebuild/republish (see Access section -- this is a real
constraint, not a formality).

---

## 2. Architecture Map

```
SKILL MAKER (source of truth, /Users/lfp/Projects/SKILL MAKER, M2)
  |
  |-- build-team-toolkit.py  -- reads curated TEAM_GROUPS, writes team-toolkit/
  |
  v
team-toolkit/  (generated, gitignored in SKILL MAKER, has its OWN .git)
  |
  |-- git push
  v
github.com/subascorp/ai-toolkit  (private repo, org: subascorp)
  |
  |-- claude plugin marketplace add/update
  v
AI team's Claude Code / Cowork installs
```

- **Repo:** `github.com/subascorp/ai-toolkit`, private, org `subascorp`.
- **Marketplace name:** `subastop-ai` (three plugins: `subastop-thinkers`,
  `subastop-core`, `subastop-design`).
- **Build script:** `build-team-toolkit.py` in SKILL MAKER -- generates
  `team-toolkit/` from `TEAM_GROUPS`. Team-only skill sources (currently just
  `ds-enforcer`) live in `team-skills/`, not repo root.
- **No database, no hosting, no third-party API integration** -- this is a static
  git-based content pipeline. Lowest-complexity handover in the ecosystem by design.

**Shipped skills (16 total):**

| Plugin | Skills |
|---|---|
| `subastop-thinkers` | critical-thinker, creative-thinker, logic-thinker, loop-breaker, ceo-planner |
| `subastop-core` | git-ops, self-audit, continuity-seed, soul-builder, projectmd-auditor, projectmd-optimizer, offload, auditor-general, meta-no-bare-names, pwa-verify |
| `subastop-design` | ds-enforcer |

---

## 3. Access & Credentials Inventory

**GitHub org `subascorp`:**
- Owners (as of 2026-07-02 recon): `bcrr666`, `integraciones-subastop`, `subastin`
- pinz-byte (LFP): **Member**, not Owner
- Org base permission: **effectively READ** -- confirmed 2026-07-02 that a single
  team membership exposes all 22+ private repos to every member. This means
  `ai-toolkit` is already readable by all ~11 org members, not just the 3 named AI
  team engineers. "AI team only" is enforced by who gets the onboarding doc, not by
  ACL. This was an accepted tradeoff, not an oversight -- changing org base
  permission is owner-only and org-wide, judged not worth it for one repo.
- 4 ex-collaborators flagged 2026-07-02 for removal: `sanchezGerman`,
  `afernandez-subas`, `santiago-ab`, `serialito74` -- revocation requested from
  Bruce (`bcrr666`, Slack `U03F81ZG5R6`), **not yet confirmed landed** (see Phase 2).
- Service accounts `integraciones-subastop` and `subastin` hold **Owner** role --
  flagged for downgrade to Member + per-repo grants, not yet done.
- Possible duplicate: `bcrodriguez-boop` may be Bruce's second account (his email is
  `bcrodriguez@subastop.com`) -- flagged for consolidation, not resolved.
- Team `ai` (GitHub Team, for membership semantics): **not created**. Not required
  for read access (base permission already grants it) -- only useful for future
  ACL tightening if the org ever moves off read-by-default.

**Credentials:** none beyond standard GitHub auth. No API keys, no service tokens, no
secrets in this repo -- it's skill markdown files only.

**Action list for the incoming/outgoing split:**
- [ ] Confirm the 4 ex-collaborator removals landed (owner-only: Bruce)
- [ ] Downgrade `integraciones-subastop` / `subastin` from Owner to Member (owner-only)
- [ ] Resolve `bcrodriguez-boop` vs `bcrr666` duplicate (owner-only)
- [ ] Decide whether AI team engineers (Julio, Aaron, Abraham) need explicit org
      membership, or whether onboarding-doc-only access is accepted long-term

---

## 4. Operational Runbooks

**Publish cycle (LFP only, native execution required -- M2):**
```bash
cd "/Users/lfp/Projects/SKILL MAKER"
python3 build-team-toolkit.py
cd team-toolkit && git add -A && git commit -m "chore: toolkit refresh" && git push
```

**Team refresh (AI team side, no action needed if they installed the marketplace):**
```bash
claude plugin marketplace update subastop-ai
```
No reinstall needed per the marketplace mechanism -- but see the CRITICAL caveat
below, inherited from a real incident on the parent `lfp-skills` marketplace.

**Recurring automation:** none specific to `subastop-ai` -- there is no scheduled
job that auto-publishes team-toolkit changes. Publishing is a manual, LFP-only
action every time a team-visible skill changes. This is a single point of failure:
if LFP is unavailable, the AI team's toolkit goes stale silently with no automated
retry.

**Rollback:** none needed in practice -- `team-toolkit/` is fully regenerated from
source each build, so a bad push is fixed by re-running the build with corrected
`TEAM_GROUPS`/sources and pushing again.

---

## 5. Known Issues & Technical Debt

- **No update-bump guarantee for the team marketplace.** The parent `lfp-skills`
  marketplace had a confirmed incident (2026-07-03, M3): `claude plugin marketplace
  update` refreshed metadata but did NOT bump already-installed plugins, which
  stayed pinned to a commit 52 versions / 5+ weeks stale, causing "Unknown skill"
  errors. `subastop-ai` uses the exact same Claude Code plugin mechanism, so **this
  same failure class almost certainly applies to the AI team's installs** and has
  not been separately verified there. `TEAM_ONBOARDING.md` currently tells the team
  to run `claude plugin marketplace update subastop-ai`, which is the same
  half-fix that caused the M3 incident -- it should tell them to also run `claude
  plugin update <plugin>@subastop-ai` per plugin, or better, an equivalent to
  `install-refresh.sh` scoped to their marketplace.
- **No scheduled refresh job for the AI team.** `install-refresh.sh` exists for
  LFP's own machines (M1/M2/M3) but nothing analogous was set up for the AI team's
  machines -- they're relying on manual `marketplace update` runs "whenever LFP
  announces an update," which is a manual trigger with no forcing function.
- **Access review incomplete** -- see Section 3 action list. Nothing here is
  urgent-severity (no secrets in this repo), but the org-wide read exposure and
  unrevoked ex-collaborators are open since 2026-07-02.

---

## 6. Decision Log

- **Org-level repo, not a new org.** `subascorp` already existed (hosts
  `legacy-vmc-subastas` etc.) -- decided 2026-07-02 not to create a separate
  `subastop` org, to avoid fragmenting infra. Don't "fix" this by creating a second
  org later without knowing this was deliberate.
- **"AI team only" enforced by onboarding, not ACL.** Given the org's read-by-default
  base permission, achieving true per-repo isolation would require an owner-level,
  org-wide permission change. Judged not worth it for one repo. If the AI team's
  perception is that `ai-toolkit` is private-to-them, that perception is currently
  inaccurate -- worth being explicit with them about this rather than letting it
  surface as a surprise later.
- **`team-toolkit/` is a build artifact, never hand-edited.** It carries its own
  independent `.git` (pushed to `subascorp/ai-toolkit`) precisely so a wholesale
  `rmtree` during rebuild doesn't destroy that repo's remote link -- this already
  happened once during development and was patched in `build-team-toolkit.py`
  (skips `.git` on regen).
- **Curated subset, not the full marketplace.** Explicit exclusion list (apex-*,
  agent-bridge, inbox-triage, pm, reentry, machine-bridge, workspace-plugin-audit,
  skill-miner, toolbox, herald-*, carmatch-intel) -- these are personal-layer or
  LFP-machine-specific and would leak context or duplicate skill names if shipped.

---

## 7. Contacts & Escalation

**Outgoing (toolkit maintainer):** LFP (pinz-byte) -- sole publisher, remains the
only one who can rebuild/republish. No handoff of publishing rights has happened;
this is worth deciding explicitly if "handover" is meant to include publishing
ownership, not just usage.

**Incoming (AI team, per team-toolkit.md):**
- Julio Herrera -- jherrera@subastop.com
- Aaron Coorahua -- rcoorahua@subastop.com
- Abraham Huacchillo -- ahuacchillo@subastop.com

None of the three were confirmed in the `subascorp` GitHub org as of 2026-07-02;
org invites were requested from Bruce (owner-only action) and were **pending** as of
that date -- status not reconfirmed since (see Phase 2).

**Org ownership (GitHub, for any access-change requests):** Bruce (`bcrr666`,
Slack `U03F81ZG5R6`).

---

## 8. Glossary

- **`lfp-skills`** -- the full personal marketplace (LFP's own machines only).
- **`subastop-ai`** -- the curated team marketplace covered by this document.
- **`TEAM_GROUPS`** -- the curated skill list in `build-team-toolkit.py` (distinct
  from `GROUPS` in `build-marketplace.py`, which defines the full marketplace).
- **M1/M2/M3** -- LFP's three working machines; M2 is the sole publisher for both
  marketplaces.
- **Team-skills sources** -- skill source files that ship ONLY to the team
  marketplace, living in `team-skills/` (not repo root, to avoid `build-marketplace.py`
  picking them up for the personal marketplace).

---

## Phase 2 -- VERIFY

Checked from this session (sandbox, no native `gh`/`launchctl` access, no
authenticated GitHub API calls possible):

| Item | Section | Verdict | Detail |
|---|---|---|---|
| `subascorp` org exists, public metadata | 2/3 | CONFIRMED | `api.github.com/orgs/subascorp` resolves: name "Subastop", 1 public repo, Lima, Peru. Checked live this session. |
| Public org member list | 3 | CONFIRMED (as: none exposed) | `api.github.com/orgs/subascorp/members` returns empty to an unauthenticated call -- consistent with no publicized members, not evidence either way on private membership. |
| team-toolkit/ has its own .git, correct remote | 2 | CONFIRMED | Checked directly this session: `team-toolkit/.git` exists, `origin` = `https://github.com/subascorp/ai-toolkit.git`, log shows 2 commits (`650412f` toolkit v1, `2184884` design plugin) matching the doc's history. |
| build-team-toolkit.py TEAM_GROUPS matches what's documented in TEAM_ONBOARDING.md | 2 | CONFIRMED | Read both files directly this session: 5 thinkers, 10 core, 1 design skill -- matches. |
| 4 ex-collaborator removals landed | 3 | **UNKNOWN** | Requires owner-level GitHub access. Native check: `gh api orgs/subascorp/members --paginate \| grep -E "sanchezGerman\|afernandez-subas\|santiago-ab\|serialito74"` (empty output = confirmed removed). Owner: Bruce. |
| Service account role downgrade (integraciones-subastop, subastin) | 3 | **UNKNOWN** | Native check: `gh api orgs/subascorp/memberships/integraciones-subastop` and same for `subastin` -- look for `"role": "member"` vs `"admin"`. Owner-only to change. |
| AI team (Julio/Aaron/Abraham) org membership | 3/7 | **UNKNOWN** | Native check: `gh api orgs/subascorp/members --paginate` and grep each username (need their GitHub handles, not just emails -- not on file anywhere in this repo, a real gap). |
| AI team actually onboarded (installed the marketplace, using it) | 7 | **UNKNOWN** | No usage telemetry exists for this marketplace. Only way to check: ask them directly, or check GitHub repo traffic/clone stats (needs push access to view). |
| `bcrodriguez-boop` vs `bcrr666` duplicate resolved | 3 | **UNKNOWN** | Native check: `gh api users/bcrodriguez-boop` and compare org role; needs Bruce to confirm identity either way. |
| AI team's installed plugins actually current (not pinned stale, per the M3 failure class) | 5 | **UNKNOWN, high suspicion of STALE** | This exact failure class was confirmed on LFP's own M3 for the parallel `lfp-skills` marketplace. Nothing distinguishes `subastop-ai` installs as immune. Native check on an AI team member's machine: `claude plugin list \| grep subastop-ai` and compare the pinned commit hash to `git -C <clone-of-ai-toolkit> log -1 --format=%h` (or just re-run `claude plugin update <plugin>@subastop-ai` for all three plugins, which is safe/idempotent either way). |
| Scheduled/automated refresh exists for AI team machines | 4 | **BROKEN (by design gap, not by decay)** | Confirmed by reading `install-refresh.sh` and `TEAM_ONBOARDING.md` directly: the onboarding doc only tells the team to run `marketplace update` manually "whenever LFP announces," with no equivalent to LFP's own `install-refresh.sh` daily job ever being handed to them. This isn't a job that broke -- it never existed for them. |

### Net assessment

Nothing here is a security emergency (no live secrets in this repo) and the
architecture is about as simple as a handover gets (a static content pipeline, no
running services). The real gaps are process gaps, not code gaps: an incomplete
access review from six days ago that was never re-checked, and a known failure
class (plugin version pinning) that was fixed for LFP's own machines on 2026-07-03
but never propagated to the onboarding instructions the AI team is actually
following. Both are cheap to close and both require either Bruce (owner-level
GitHub actions) or five minutes rewriting `TEAM_ONBOARDING.md`'s refresh
instructions -- neither requires re-architecting anything.

### Recommended next actions, in order

1. Get the AI team's actual GitHub handles (not just emails) -- can't verify their
   org access or track adoption without this, and it's currently not recorded
   anywhere in this repo.
2. Ping Bruce for a straight yes/no on the four pending items in Section 3 (he's the
   only one who can answer them).
3. Patch `TEAM_ONBOARDING.md`'s "Staying current" section to include
   `claude plugin update <plugin>@subastop-ai` per plugin, matching the fix already
   applied to `install-refresh.sh` for LFP's own machines -- this is a five-minute
   edit that closes the highest-likelihood silent-failure gap on this list.
4. Decide, explicitly, whether "AI team only" being enforced by onboarding-not-ACL is
   an acceptable permanent state or a placeholder -- and if it's a surprise to the
   team that ~11 org members can technically read the repo, tell them now rather
   than let it surface later.
