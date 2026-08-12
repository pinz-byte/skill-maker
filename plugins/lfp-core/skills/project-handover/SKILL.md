---
name: project-handover
description: >-
  Produces a full, verified project handover package for transferring a project to a new team
  or owner -- documentation plus an audit, for people who never touched the project before.
  Two phases: DOCUMENT (architecture map, access/credentials inventory, runbooks, known
  issues, decision log, contacts, glossary) and VERIFY (confirm every access grant,
  credential, and recurring job is actually current, not assumed -- catching stale roles,
  silently-broken automation, and duplicate or untracked state). Use whenever the user says
  handover this project, hand off to the team, transfer ownership, prepare handover docs,
  onboard the new team, or document this for handover. Also trigger before transferring any
  codebase or infra to a new owner. Distinct from continuity-seed (session resume) and
  soul-builder (persistent intention) -- this is a one-time transfer to people outside the
  room. NOT project-migrate (moves a project between machines): this transfers ownership to
  people.
metadata:
  intent: relay
---

# Project Handover

A handover fails silently, not loudly. The Subastop-to-AI-team handover didn't fail
because nobody wrote docs -- it failed because things that were *written down as true*
were not actually true: a launchd job "documented" as canonical had been silently
pointing at a decommissioned path for weeks, four ex-collaborators still held read
access to every private repo in the org, and two clones of the same repository had
quietly diverged. None of that shows up by writing a nice README. It shows up by
checking.

This skill has two phases. **DOCUMENT alone is not a handover.** A handover is
DOCUMENT + VERIFY together -- the second phase is what this skill adds over just
writing a good doc.

## Phase 1 -- DOCUMENT

Produce a single `HANDOVER.md` (or equivalent) with these sections. Skip a section
only if it is genuinely not applicable, and say so explicitly rather than leaving it
blank.

1. **Project Overview** -- what it is, why it exists, current state. Link to an
   existing SOUL.md/IB if the project has one ([[soul-builder]]) instead of
   re-deriving it.
2. **Architecture Map** -- repos (with URLs and default branch), hosting/cloud
   project IDs, data stores, key third-party integrations, and how they connect.
3. **Access & Credentials Inventory** -- every account, repo, cloud console, API key,
   and service account that touches this project, who currently has access, and at
   what level (owner vs member vs read-only matters -- see Edge Cases on implicit
   org-level access). Include an explicit action list: what must be revoked, rotated,
   or newly granted for the incoming team.
4. **Operational Runbooks** -- deploy process, monitoring/on-call, every recurring
   job (cron, launchd, cloud scheduler) with the command or config that actually runs
   it, not a paraphrase.
5. **Known Issues & Technical Debt** -- open bugs, workarounds, and specifically
   anything that *looks* finished but has a known gap. Name silent-failure risks
   explicitly rather than only listing open tickets.
6. **Decision Log** -- non-obvious architectural or business decisions and the
   reasoning behind them, so the incoming team doesn't reverse a decision made for a
   reason that isn't visible in the code.
7. **Contacts & Escalation** -- who to ask about what, on both the outgoing and
   incoming side, plus any external stakeholders.
8. **Glossary** -- project-specific terms, acronyms, and naming conventions a
   newcomer would otherwise have to reverse-engineer.

Read `references/handover-checklist.md` for the full item-by-item checklist behind
each section.

## Phase 2 -- VERIFY

For every claim in the Phase 1 document that can be checked, check it. Do not accept
"this should be the case" as equivalent to "this is confirmed." Produce a verdict per
item:

- **CONFIRMED** -- checked directly (ran the command, viewed the console, listed the
  members) and it matches the doc.
- **STALE** -- checked, and it does not match the doc (access that should have been
  revoked but wasn't, a path that no longer exists, a job pointing somewhere old).
- **BROKEN** -- checked, and it doesn't work at all (job not running, credential
  invalid, endpoint 404s).
- **UNKNOWN** -- could not be checked from here (needs the outgoing team's live
  credentials, or owner-only access this session doesn't have). Say so, and name
  exactly who needs to run the check.

Specifically probe for the three failure classes this skill exists because of:

- **Access drift** -- enumerate the actual current member/collaborator list against
  who the doc claims has access. Don't trust a prior access review's conclusion;
  re-check it (see [[subascorp-access-review]] pattern: revocations were requested
  but landing them still needed a follow-up verification pass).
- **Silent automation failure** -- for every recurring job listed in the runbooks
  section, confirm it actually fired recently (log output, last-run timestamp), not
  just that a plist/cron entry with the right name exists. A job can be "installed"
  and still be dead.
- **Duplicate/untracked state** -- check for more than one clone, environment, or
  config claiming to be canonical. If found, identify which one is actually live
  (reflog/commit history, not modification date) and flag the other for
  decommissioning -- don't silently assume the newer-looking one is correct.

Report the verdicts as a table, not prose. A handover with five BROKEN items and a
clean-sounding summary paragraph is worse than a handover that visibly says "5 of 40
items broken, here they are."

## Principles

- **Verify, don't just document.** A documented runbook nobody re-ran is a guess
  wearing the clothes of a fact.
- **Access review is not optional and not skippable by the outgoing team.**
  Enumerate who has access today, not who is supposed to.
- **Silent failures are the primary handover risk, not missing docs.** Actively hunt
  for "looks fine but isn't" states rather than only filling in a template.
- **The incoming team should be able to operate from this document alone**, without a
  live call to the outgoing team, for anything short of a genuine emergency.

## Edge Cases

- **Platform implicit-access models** -- some platforms grant broader access than
  the per-repo/per-resource view suggests (e.g. an org's base permission level can
  make every member a de facto reader of every private repo, regardless of explicit
  grants). Check the platform's base/default permission level before writing "access
  is scoped to X" in the doc.
- **Partial handovers** -- when only some responsibilities transfer, scope the
  package explicitly and mark what stays with the outgoing team, rather than
  producing a document that implies full transfer.
- **Cross-machine/cross-environment quirks** -- different machines or environments
  may reach the same resource through different auth paths (SSH vs HTTPS, different
  service accounts). Document these per-environment, don't assume uniformity.
- **Owner-only checks** -- some verifications (revoking org access, rotating certain
  credentials) require owner-level permissions the outgoing engineer may not have.
  Mark these UNKNOWN with a named owner to follow up, don't block the rest of the
  handover on them.

## Reference

-> `references/handover-checklist.md` -- full checklist behind each DOCUMENT section
and each VERIFY probe.
