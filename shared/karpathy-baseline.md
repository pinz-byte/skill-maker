# Behavior rules (Karpathy baseline)

Single source of the four-rule baseline. Both projectmd-auditor (detects its
presence) and projectmd-optimizer (inserts it) read THIS file. Edit here once;
the build copies it into each skill bundle as references/karpathy-baseline.md.
Never fork this content into a skill body -- they will drift.

Source: Andrej-Karpathy-inspired CLAUDE.md (Forrest Chang / multica-ai,
github.com/multica-ai/andrej-karpathy-skills). Condensed from the canonical
65-line file to a compact always-loaded block -- inserting the full file would
bloat the very context the optimizer is shrinking. Attribute, do not inflate.

## INSERT BLOCK (this is what the optimizer writes into a CLAUDE.md)

```
## Behavior rules

1. Think before coding. Don't assume -- state assumptions; if uncertain or
   the request is ambiguous, ask or present the options instead of picking
   silently. If something is unclear, stop and name it. Flag a simpler approach
   when one exists.
2. Simplicity first. Minimum code that solves the problem. No speculative
   features, no abstractions for single-use code, no unrequested flexibility or
   error handling for impossible cases.
3. Surgical changes. Touch only what the request requires. Don't refactor or
   reformat adjacent working code; remove only the orphans your own change
   created.
4. Goal-driven execution. Define a verifiable success criterion before coding,
   then loop until it passes (e.g. write the failing test first).

<!-- Add project-specific behavior rules below this line. -->
```

## DETECTION SIGNATURE (this is how the auditor decides "baseline present")

Count a CLAUDE.md as having the baseline if it contains EITHER:
- a heading matching /behaviou?r(al)? (rules|guidelines)/i, OR
- at least 3 of these 4 concept markers (case-insensitive):
  - assumptions / don't assume / surface tradeoffs
  - simplicity / minimum code / nothing speculative
  - surgical / touch only what / don't refactor
  - success criteria / verifiable goal / loop until

Partial match (1-2 markers, no heading) = "baseline weak" -> recommend refresh.
Zero markers = "no baseline" -> recommend add-baseline.
