<!-- last_updated: 2026-07-02 -->
# Subastop AI Toolkit — Onboarding

Curated skill marketplace for the Subastop AI team. Private — access by invitation only.

## What you get

**subastop-thinkers** — oversight roundtable:

- `critical-thinker` — blunt scrutiny of plans, theses, and arguments
- `creative-thinker` — value-oriented solution generation with adversarial review
- `logic-thinker` — explicit reasoning chains, premise-by-premise
- `loop-breaker` — escape recurring failures by reframing the problem
- `ceo-planner` — pressure-test a plan before it goes to a builder

**subastop-core** — working discipline:

- `git-ops` — full git lifecycle: clean commits, squash, branches, conflicts
- `self-audit` — pre-delivery quality check on any task
- `auditor-general` — independent post-hoc verification of builds and fixes
- `continuity-seed` — session handoff documents for cross-session continuity
- `soul-builder` — persistent project intention (SOUL.md)
- `projectmd-auditor` / `projectmd-optimizer` — CLAUDE.md health and compression
- `offload` — delegate heavy work to cheaper subagents
- `meta-no-bare-names` — context-file hygiene gate for git operations

**subastop-design** — product UI discipline:

- `ds-enforcer` — Subastop Design System v3 enforcement: pre-build gate + post-build
  audit for every dashboard, cockpit, or landing UI (VMC, MAF, CarMatch, AVT)

## Prerequisites (one-time)

1. A GitHub account that is a member of the `subascorp` org (ask LFP if you
   are not in the org yet).
2. Git authenticated over HTTPS: install GitHub CLI and run `gh auth login`
   (choose HTTPS + browser login).
3. Claude Code (`npm install -g @anthropic-ai/claude-code`) and/or the Claude
   desktop app with Cowork.

## Install

```bash
claude plugin marketplace add subascorp/ai-toolkit
claude plugin install subastop-thinkers@subastop-ai
claude plugin install subastop-core@subastop-ai
claude plugin install subastop-design@subastop-ai
```

In Cowork: Settings -> Capabilities -> add the marketplace, then enable both plugins.

## Staying current

`claude plugin marketplace update` only refreshes the list of available versions --
it does NOT update plugins you already installed. Confirmed 2026-07-03: plugins can
stay pinned to their install-time version for weeks after this command reports
success. Run all four lines, not just the first:

```bash
claude plugin marketplace update subastop-ai
claude plugin update subastop-thinkers@subastop-ai
claude plugin update subastop-core@subastop-ai
claude plugin update subastop-design@subastop-ai
```

Run this whenever LFP announces an update. Running only the first line will report
success while leaving your skills silently out of date.

## Using the skills

Skills fire on their trigger phrases (each skill's description lists them).
Fast start: "challenge this plan" (critical-thinker), "commit this" (git-ops),
"seed" at end of session (continuity-seed), "audit this build" (auditor-general).

## Rules

- Do not fork, copy, or redistribute outside the Subastop AI team.
- Report friction or skill ideas to LFP — the toolkit evolves from real usage.
