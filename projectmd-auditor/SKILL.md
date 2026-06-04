---
name: projectmd-auditor
description: >
  Read-only scanner that finds every CLAUDE.md across the ecosystem and ranks
  which ones need optimization -- before anything is touched. Use whenever the
  user says "audit my CLAUDE.md files", "which CLAUDE.md files are bloated",
  "claudemd audit", "which projects need optimization", "scan for bloated
  context files", "are my context files stale", "which CLAUDE.md should I
  compress", or wants a map of context-file health before editing. Measures
  per file: approximate token count, prose vs imperative density, stale markers
  (old dates, dead infra, unresolved TODOs), @import usage, and Karpathy
  baseline presence. Outputs a ranked table worst-first with the primary issue
  and a recommended action. Never modifies anything. Pairs with
  projectmd-optimizer (this maps; optimizer executes one file at a time).
---

# projectmd-auditor -- Rank CLAUDE.md Files by Optimization Need

## What this is

A read-only audit. It surveys every CLAUDE.md under a root and tells you which
ones are bloated, stale, or missing the behavior baseline -- so you optimize the
worst offenders deliberately instead of guessing. It changes nothing; it
produces a ranked report. Run it before projectmd-optimizer.

## Scope

Default root: `~/Documents/Claude/Projects/`. Accept a different root if the
user names one. Find CLAUDE.md files recursively. Include `.claude/*.md`
context files too if asked, but rank root CLAUDE.md files first -- those load
every session and cost the most.

## Per-file measurements

For each CLAUDE.md, compute:

1. Token count -- approximate as `characters / 4`. Good enough for ranking; do
   not call a tokenizer.
2. Prose density -- ratio of full-sentence prose lines to imperative
   one-liners. High prose = strong optimization candidate (prose compresses 50-
   70%). Flag files that are mostly paragraphs.
3. Stale markers --
   - dates older than 90 days from today (verify today's date with the shell),
   - references to dead/deprecated infra (e.g. Railway, retired tools, old
     hostnames), legacy paths,
   - unresolved TODO / FIXME / XXX.
4. @import usage -- note `@filename` includes. @import is EAGER (loads every
   session), so it is not deferral. Flag large inlined OR heavily-@imported
   files as tiering candidates (move to docs/ + plain-path pointer).
5. Baseline presence -- apply the DETECTION SIGNATURE in
   references/karpathy-baseline.md (heading match OR >=3 of 4 concept markers).
   Classify present / weak / none.

## Output

A ranked table, worst first, plus a summary. Use this shape:

```
CLAUDE.md AUDIT -- [today's date]

| File | Tokens | Primary Issue | Action |
|---|---|---|---|
| Projects/AVT/.../CLAUDE.md | 847 | Prose-heavy, no baseline | Compress + add baseline |
| Projects/Symbios/CLAUDE.md | 612 | Stale infra refs (Railway) | Update |
| Projects/APEX/.../CLAUDE.md | 203 | Clean | -- |

FILES NEEDING ACTION: X of Y
TOTAL TOKEN WASTE (estimated): ~N tokens/session
```

Ranking key: a file is worse the higher its token count AND the more issues it
carries. Surface the single most important issue per file in "Primary Issue",
and one of: Compress / Split / Update / Add-baseline / -- (clean) in "Action".

"TOTAL TOKEN WASTE" = sum of estimated reducible tokens across files needing
action (rough: prose-heavy files lose ~50%, stale sections their full size).

## Principles

- Read-only, always. The auditor never edits, never deletes, never reorders.
  Optimization is projectmd-optimizer's job, one file at a time, with a diff.
- Rank by cost, not just size. A 200-token file loaded every session can matter
  more than a 900-token one loaded rarely -- weight root CLAUDE.md files first.
- One primary issue per file. Do not dump every nit; name the load-bearing
  problem so the user knows the next move.
- Baseline detection is shared. Use references/karpathy-baseline.md as the only
  source of what "baseline" means -- do not hardcode the rules here.

## Edge cases

- No CLAUDE.md found: say so and confirm the root path rather than assuming none
  exist (the path may be wrong or unmounted).
- Huge monorepo with many files: cap the table to the worst ~20 and note how
  many more need action.
- A file marked entirely `<!-- custom -->`: report its size but mark Action as
  "review (custom)" -- the optimizer will not auto-rewrite it.
- Date math: get today's date from the shell before computing the 90-day
  staleness window; do not assume.
