---
name: builder-identity-check
description: >
  Shared pre-flight check for cross-tool audit skills -- confirms which
  tool (Claude or Codex) actually built a piece of work before an audit or
  audit-handoff proceeds, so a wrongly-routed audit never becomes a
  self-audit wearing a disguise. Invoked by name from audit-codex-build
  and codex-audit-handoff as their first step -- both depend on this file
  as the single source of truth instead of each carrying their own copy.
  Use directly when the user asks "who built this", "which tool made this
  change", "was this Claude or Codex", or "confirm the builder before
  auditing". Also trigger proactively whenever an audit is about to run
  and the builder's identity is stated ambiguously or not at all.
metadata:
  intent: audit
---

# Builder Identity Check -- Shared Pre-Flight for Cross-Tool Audits

## Why this exists as its own skill
`audit-codex-build` and `codex-audit-handoff` both need to answer the same
question before doing anything else: which tool actually built this? That
question used to be answered with the same paragraph duplicated in both
files. Duplication drifts -- if the answer changes, only one copy might
get updated. This skill is the one place that paragraph lives; the other
two invoke it by name instead of restating it, the same way they invoke
`auditor-general` by name instead of reimplementing its report contract.

## The check
Never assume. Confirm from an explicit source before letting the calling
skill proceed:
- An explicit user statement ("Codex wrote this", "I built this in Claude
  Code"), or -- for Claude-built work specifically -- the fact that the
  work was produced earlier in this same session, is the only source of
  truth this check relies on.
- Do not infer builder identity from git author/committer fields. Checked
  2026-08-06 against SKILL MAKER's full history: every commit -- 25+,
  spanning hook additions and marketplace rebuilds -- is authored as
  `Fernando Pinzon <pinzon@subastop.com>` regardless of which tool did the
  work. Git leaves no distinguishing trail here. Re-verify this specific
  finding if Codex is ever configured with its own git identity -- until
  then, git is not a usable signal.
- If genuinely unstated and unclear, stop and ask which tool built the
  work. Do not guess -- a wrong guess here means the calling skill
  proceeds believing it has independence when it doesn't, which defeats
  the entire point of either calling skill.

## What it returns to the calling skill
CONFIRMED-CODEX, CONFIRMED-CLAUDE, or UNCONFIRMED. On UNCONFIRMED, the
calling skill stops and asks -- it does not pick a branch on a guess.

## Never do this
- Never let a calling skill skip this check because the request
  "obviously" implies one direction.
- Never treat silence or ambiguity as CONFIRMED for either side.
