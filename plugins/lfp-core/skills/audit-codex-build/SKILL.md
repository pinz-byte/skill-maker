---
name: audit-codex-build
description: >
  Audits work that Codex (the CLI tool) built, applying auditor-general's
  verdict contract for the specific case where Codex is the builder and a
  different tool must be the auditor. Runs directly, in-session: reads
  Codex's actual commits, diff, or files and applies auditor-general's
  BUILD REVIEW, FIX VALIDATION, or SYSTEM OVERSIGHT mode. Use when the user
  asks to "audit what Codex built", "did Codex actually deliver", "check
  Codex's commit", "review Codex's work", "verify what Codex did", or
  names Codex specifically as the builder of something that needs
  checking. Confirm Codex actually built the work before proceeding -- if
  that is unstated or unclear, ask rather than assume. Do not use this for
  work built in this Claude session or by Claude generally -- that is a
  different skill (codex-audit-handoff), because Claude cannot audit its
  own build.
metadata:
  intent: audit
---

# Audit Codex's Build

## The rule this enforces
Whoever builds it does not audit it. This skill covers exactly one
direction: Codex built something, Claude is the independent auditor. This
is a real audit -- it runs now, in this session, and ends in a verdict.
The reverse direction -- Claude built it, Codex must audit -- is a
different skill, `codex-audit-handoff`, because Claude cannot invoke Codex
directly. Do not use this skill for that case; routing it here would be
Claude auditing itself under a borrowed name.

## Step 1 -- confirm Codex built it
Run `builder-identity-check` first. Proceed to Step 2 only on
CONFIRMED-CODEX. On UNCONFIRMED, stop and ask which tool built the work --
do not guess. On CONFIRMED-CLAUDE, this is the wrong skill: route to
`codex-audit-handoff` instead.

## Step 2 -- run the actual audit
Read the real commits, files, or diff Codex produced. Run
`auditor-general` directly, selecting BUILD REVIEW, FIX VALIDATION, or
SYSTEM OVERSIGHT per its own mode-selection table. Do not reimplement
auditor-general's report contract here -- invoke it, and use its AUDIT
REPORT skeleton verbatim (Verdict summary / Claims audited / Evidence
chains / Findings by severity / Repair path / Not verified).

## Never do this
- Never skip Step 1 because the request "obviously" means Codex -- state
  the confirmation explicitly, even briefly.
- Never soften a FAIL because Codex is not in the room to defend the
  work. auditor-general's contract is verdict-only; this skill does not
  get to be gentler than that contract.
- Never use this skill to audit Claude's own work, including work from an
  earlier session or a different Claude instance -- same-tool is
  disqualifying no matter which side is asking. Route to
  `codex-audit-handoff` instead.

## Known gap, flagged not fixed
`AGENTS.md` (Codex's equivalent of CLAUDE.md in this repo) is currently
corrupted -- it reads as CLAUDE.md run through a blind find-replace
(claims `.Codex-plugin/marketplace.json` exists; the real path is
`.claude-plugin`; claims skill names must not contain "Codex" when the
real reserved word, per build-marketplace.py, is "claude"). This does not
block auditing Codex's output -- but if the audit concerns SKILL MAKER's
own build or publish mechanics, know that Codex was likely working from
this corrupted picture when it built whatever is now under audit. Fix
AGENTS.md before trusting either the build or an audit of anything
touching this repo's own distribution mechanics.
