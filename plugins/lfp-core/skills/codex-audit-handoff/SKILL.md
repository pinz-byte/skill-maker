---
name: codex-audit-handoff
description: >
  Prepares a handoff package so Codex can independently audit work Claude
  built -- this skill does not itself perform an audit, because Claude
  auditing its own build would defeat the purpose of independent review.
  Writes an AUDIT_HANDOFF file (what was built, the original brief, and
  instructions to use auditor-general's exact report skeleton) plus a
  paste-ready kickoff message for the user to run in a native Codex
  session. Use when the user asks to "have Codex check my work", "get an
  outside audit of what Claude built", "don't let Claude grade its own
  homework", "cross-check this with Codex", or names Claude specifically
  as the builder of something that needs independent review. Confirm
  Claude actually built the work before proceeding -- if that is unstated
  or unclear, ask rather than assume. Do not use this for work Codex
  built -- that is a different skill (audit-codex-build) and runs
  directly instead of via handoff.
---

# Codex Audit Handoff -- Preparing an Independent Review of Claude's Build

## The rule this enforces
Whoever builds it does not audit it. This skill covers exactly one
direction: Claude built something -- including this session's own work --
and the audit must come from Codex, a separate tool, not from Claude
reviewing itself. Claude cannot invoke Codex the way it invokes a skill or
subagent: Codex is a separate native CLI the user runs themselves. So this
skill never produces an audit. It produces a handoff, and the actual audit
happens later, externally, when the user runs it.

State this plainly at the start of the response: this action prepares a
request for Codex to audit. It does not complete an audit.

## Step 1 -- confirm Claude built it
Run `builder-identity-check` first. Proceed to Step 2 only on
CONFIRMED-CLAUDE. On UNCONFIRMED, stop and ask which tool built the work --
do not guess. On CONFIRMED-CODEX, this is the wrong skill: route to
`audit-codex-build` instead.

## Step 2 -- write the AUDIT_HANDOFF file
Include:
1. What was built -- files touched, commit range or diff.
2. The original brief or contract it was built against.
3. An explicit instruction to produce the report using auditor-general's
   exact skeleton (Verdict summary / Claims audited / Evidence chains /
   Findings by severity / Repair path / Not verified), so the verdict is
   comparable regardless of which tool produced it. Codex does not have
   the auditor-general skill installed, so the handoff must carry the
   full instruction, not just a pointer to a skill name.

Save it where the user will find it -- project root or alongside the work
under review -- named `AUDIT_HANDOFF_[target]_[date].md`.

## Step 3 -- write the kickoff message
A short, paste-ready message for the user to open in a Codex session,
pointing at the handoff file and telling Codex to produce the report per
the file's instructions.

## Step 4 -- say what has and has not happened
State explicitly: the handoff is written, no audit has occurred yet, and
the verdict is pending until the user runs it in Codex and reports back.
Do not mark the underlying task as audited, closed, or verified based on
this skill alone.

## Never do this
- Never produce the AUDIT REPORT yourself for Claude-built work, even
  "just this once" or "just a quick check" -- that is self-audit wearing
  this skill's name. If the user actually wants a same-tool check, that
  is self-audit's job explicitly, not this one.
- Never decide "close enough, skip the handoff" because Codex is not
  available right now -- say the audit is blocked or pending, do not
  quietly downgrade to a self-check.
- Never use this skill to audit Codex's own work -- that runs directly,
  without a handoff, via `audit-codex-build`.

## Known gap, flagged not fixed
The same AGENTS.md corruption noted in `audit-codex-build` applies here
with more force: Codex will read the handoff using its own corrupted
understanding of this repo's build and publish mechanics if the audit
touches that territory. Fix AGENTS.md before sending a handoff whose
subject matter is SKILL MAKER's own distribution mechanics.
