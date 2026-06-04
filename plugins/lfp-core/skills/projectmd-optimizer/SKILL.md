---
name: projectmd-optimizer
description: >
  Takes one CLAUDE.md (named directly or surfaced by projectmd-auditor) and
  produces an optimized version -- compressed, tiered, baseline-aware -- with a
  reviewable diff and nothing deleted silently. Use whenever the user says
  "optimize this CLAUDE.md", "compress this context file", "claudemd optimize",
  "reduce tokens in CLAUDE.md", "split this CLAUDE.md", "slim my context file",
  "tier this CLAUDE.md", or wants a single context file made leaner without
  losing meaning. Runs three passes: compression (prose to imperative one-
  liners), tiering (ALWAYS / ON-DEMAND / ARCHIVE), and baseline (insert the
  Karpathy behavior block if absent). Outputs a lean root CLAUDE.md plus one
  docs/*.md per on-demand section referenced by plain-path pointers (not
  @import, which loads every session), and a token-delta summary. Never
  deletes content without showing it first; never rewrites
  custom-marked sections; never paraphrases build commands.
---

# projectmd-optimizer -- Compress, Tier, and Baseline One CLAUDE.md

## What this is

Operates on a SINGLE CLAUDE.md. Reads it fully, then runs three passes and
emits an optimized file plus split-out on-demand files and a diff. Pairs with
projectmd-auditor (which picks the target). One file at a time -- never batch.

## Pass 1 -- Compression

Rewrite prose instructions as imperative one-liners. No meaning lost; 50-70%
token reduction is typical on prose-heavy files. "When you are about to deploy,
make sure you first run the tests and then..." becomes "Before deploy: run
tests, then ...". Keep every distinct instruction; drop only filler words.

## Pass 2 -- Tiering

LOAD SEMANTICS FIRST -- this is where tiering is won or faked. `@import` is
EAGER: a CLAUDE.md `@file` loads that file every session, deferring nothing. And
Cowork AUTO-LOADS `.claude/` (including `.claude/rules/`). So neither `@import`
nor `.claude/` defers tokens. Real deferral = move content to a folder the
runtime does NOT auto-load (default `docs/`) and reference it from root with a
PLAIN-PATH POINTER the agent reads only when the task needs it. Verify which
folders the target runtime auto-loads before trusting the saving.

Classify each section:
- ALWAYS -- needed every session (project identity, core build commands, the
  behavior baseline). Stays in root CLAUDE.md.
- ON-DEMAND -- task-specific (deploy playbook, one subsystem's details, rare
  workflows). Move to `docs/[section-name].md` and add a plain-path pointer in
  root (e.g. "Build steps: docs/build-pattern.md"). NOT `@import`, NOT
  `.claude/` -- both load every session.
- ARCHIVE -- historical / no longer operative (past migrations, resolved
  incidents). Move to `docs/archive/` or MEMORY.md. Never discard, never put it
  in an auto-loaded folder.

Target: the optimized root holds ALWAYS-tier only. The behavior baseline (~100
tokens) is additive, so a root that lacked it lands above a bare 300 -- that is
expected, not a failure.

## Pass 3 -- Baseline

Check for the behavior baseline using references/karpathy-baseline.md (the
DETECTION SIGNATURE). If absent or weak, insert the INSERT BLOCK from that file.

Placement matters: put `## Behavior rules` HIGH -- immediately after the project
overview / identity section, NOT buried mid-file. These are always-loaded
high-priority directives; low placement reduces salience. (This corrects the
projectmd-gen draft, which placed it between Code conventions and Testing.)

## Outputs

1. Optimized root CLAUDE.md (ALWAYS tier, baseline high).
2. One `docs/[section-name].md` per ON-DEMAND section, with a plain-path pointer
   added to root. Never use `@import` (eager) or `.claude/` (auto-loaded) for
   deferred content -- both load every session and fake the saving.
3. Anything moved to ARCHIVE, written to the archive file.
4. A diff summary: original tokens -> optimized tokens, sections compressed,
   sections moved (to where), sections archived. Show it before the user
   accepts.

## Hard rules (from the brief -- do not violate)

- Never delete content without showing POPs first. Moving to an archive file is
  allowed; discarding is not.
- Never rewrite sections marked `<!-- custom -->`. Compress only auto-generable
  sections; leave custom blocks byte-for-byte.
- Always preserve exact build commands. Never paraphrase a script name, flag, or
  path -- copy them verbatim.

## Principles

- Meaning-preserving, not lossy. Compression removes words, never instructions.
  If you cannot shorten a line without losing a directive, leave it.
- Diff before commit. The user reviews the token-delta and the moves before the
  optimized file replaces the original. Compression is model judgment, not
  deterministic -- it must be inspectable.
- Single baseline source. Insert from references/karpathy-baseline.md; do not
  hardcode the four rules here (keeps parity with projectmd-auditor and
  projectmd-gen).
- One file per run. Never optimize a batch -- the auditor ranks, you execute the
  top one, then the next.

## Edge cases

- Runtime auto-loads the chosen folder: then tiering saves nothing there.
  Verify what the runtime auto-loads; if even `docs/` loads, keep ON-DEMAND
  inline and report that only compression + baseline applied.
- File already lean (<300 tokens, baseline present): say so and stop -- do not
  manufacture changes.
- Build commands embedded in prose: extract them verbatim into an ALWAYS block;
  never reword them during the compression pass.
- Mixed custom + auto content in one section: split it -- compress the auto part,
  leave the `<!-- custom -->` part untouched.
- Destructive request ("just delete the old stuff"): still archive rather than
  discard, and show what was moved.
