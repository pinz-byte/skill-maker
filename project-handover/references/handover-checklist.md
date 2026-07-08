# Handover Checklist by Section

Reference file for `project-handover/SKILL.md`. Phase 1 items build the document.
Phase 2 items are the verification probes -- run them against Phase 1's claims, don't
skip straight to writing them up as confirmed.

---

## Phase 1 -- DOCUMENT

### 1. Project Overview

- [ ] One paragraph: what this project is and why it exists (business purpose, not just tech stack)
- [ ] Current state: shipped/live, in progress, paused -- and since when
- [ ] Link to existing SOUL.md, IB, or intention doc instead of re-deriving the model from scratch
- [ ] Who the outgoing owner/team was, and their role going forward (fully off, on-call for questions, etc.)

### 2. Architecture Map

- [ ] Every repo: URL, default branch, what it deploys, who can push
- [ ] Hosting/cloud project IDs (GCP project, AWS account, Vercel/Netlify org, etc.)
- [ ] Every data store (DB, bucket, cache) and what lives in it
- [ ] Every third-party integration (payment, auth, analytics, email) with which account owns it
- [ ] A simple diagram or list of how the pieces connect -- doesn't need to be fancy, needs to be accurate

### 3. Access & Credentials Inventory

- [ ] Every GitHub/GitLab org and repo, current member list, and each member's role (owner vs member vs collaborator)
- [ ] Every cloud console (GCP/AWS/Azure) with current IAM bindings for people (not just service accounts)
- [ ] Every API key / secret in use, where it's stored (Secret Manager, .env, vault), and who can read it
- [ ] Every service account and its role -- flag any service account holding Owner/Admin that should be scoped down
- [ ] Explicit action list: "revoke X", "rotate Y", "grant Z to incoming team" -- not just a snapshot, a to-do
- [ ] Domain registrars, DNS providers, SSL certs -- often forgotten and single-point-of-failure when forgotten

### 4. Operational Runbooks

- [ ] Deploy process: exact commands, not "run the deploy script" without naming it and where it lives
- [ ] Every recurring job (cron, launchd, Cloud Scheduler, GitHub Actions schedule) -- what it does, how often, and the exact command/config
- [ ] Monitoring/alerting: what's watched, where alerts go, who's on-call if anyone
- [ ] Rollback procedure if a deploy goes bad
- [ ] Local dev setup: can a new engineer get this running from the README alone?

### 5. Known Issues & Technical Debt

- [ ] Open bugs with severity and current workaround (if any)
- [ ] Anything that "looks done" but has a known gap -- name these explicitly, they're the highest-risk items
- [ ] Deferred decisions ("we chose X for now, should revisit when Y")
- [ ] Anything flagged in past audits/retrospectives that was never actually fixed

### 6. Decision Log

- [ ] Non-obvious architecture choices and why (e.g. "we use X instead of the obvious Y because...")
- [ ] Business/product decisions that shaped technical constraints
- [ ] Anything a new team is likely to want to "fix" that was actually a deliberate tradeoff -- name it before they rediscover it the hard way

### 7. Contacts & Escalation

- [ ] Outgoing team: names, roles, contact method, and how long they're reachable post-handover
- [ ] Incoming team: names, roles, contact method
- [ ] External stakeholders (vendors, clients, contractors) relevant to ongoing operation
- [ ] Who owns the relationship with each third-party service (billing contact, admin login)

### 8. Glossary

- [ ] Project-specific acronyms and internal names spelled out
- [ ] Naming conventions (branch names, environment names, ticket prefixes) explained

---

## Phase 2 -- VERIFY

Run these against the Phase 1 document. Each item gets a verdict: CONFIRMED / STALE /
BROKEN / UNKNOWN.

### Access Drift

- [ ] Pull the ACTUAL current member/collaborator list for every repo and org named in Section 3 -- diff against the doc
- [ ] Confirm any "should be revoked" item from a prior access review actually landed (don't trust the request, check the result)
- [ ] Check the platform's base/default permission level (org-wide read, project-wide viewer role) -- explicit per-resource grants can be meaningless if the base level already grants broad access
- [ ] Confirm service accounts hold the role documented, not a broader one nobody downgraded

### Silent Automation Failure

- [ ] For every recurring job in Section 4, find its last actual run (log timestamp, execution history) -- not just that the schedule/plist/cron entry exists
- [ ] Confirm the job points at a path/URL/credential that currently exists and is current, not a decommissioned or renamed one
- [ ] If a job failed silently in the past, confirm the underlying cause was fixed, not just that someone re-ran it once

### Duplicate / Untracked State

- [ ] Search for more than one clone, environment, or config claiming to be canonical
- [ ] If duplicates exist, determine which is actually live using commit/reflog history -- not file modification dates, not which one "looks newer"
- [ ] Flag the non-canonical copy for explicit decommissioning (don't delete without the user's sign-off, per the project's own file-safety norms)

### Doc Staleness

- [ ] Every file path, URL, and command referenced in the handover doc: does it currently resolve?
- [ ] Every named contact: still reachable at that contact method?
- [ ] Every credential referenced: still valid (not expired, not rotated since the doc was written)?

---

## Verdict Table Format

```
| Item | Section | Verdict | Detail |
|---|---|---|---|
| github.com/org/repo access | 3 | STALE | 2 ex-collaborators still listed, revoke requested 2026-0X-XX, not yet confirmed landed |
| nightly-sync launchd job | 4 | BROKEN | plist points at a path removed 3 weeks ago; job has not run since |
| skill-maker clone (~/Documents) | -- | STALE | abandoned clone, diverged from canonical; flag for decommission |
```

## Scoring Guidance

- **All CONFIRMED** -- handover is ready to close out. Say so plainly.
- **Any STALE or BROKEN** -- handover is NOT complete. List them as blockers, not footnotes.
- **Any UNKNOWN** -- name exactly who (by role, not just "someone") needs to run the check, and don't let it silently disappear from the handover.
