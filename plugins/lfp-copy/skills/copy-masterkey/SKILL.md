---
name: copy-masterkey
description: >
  Cascading copywriting pipeline -- creative/ideation, drafting, and validation as one
  automatic sequence, modeled on masterkey's staged-refinement pattern but specialized
  for commercial/sales copy. Extracts facts, audience, and objective once, drafts via
  patel-tone-converter (same plugin group, always installed together), then runs a
  mandatory validation gate (fact-traceability, no NP-copy plagiarism,
  human-operator-voice check) before delivering -- the checks that caught a real
  production rejection this system is built around. Use whenever the user asks for
  full end-to-end commercial copy instead of a single conversion: "necesito el copy
  completo", "corre el proceso completo de copy", "de la idea al copy final", "full
  copywriting workflow", "copy cascade", "copy masterkey", "like masterkey but for
  copywriting", or any request that means manually chaining several copy skills. Also
  trigger when a draft exists and only validation is needed -- skip straight to the
  gate.
---
# Copy Masterkey -- Cascading Copywriting Workflow

## What this skill does
One structured pipeline -- ideation, drafting, validation -- for commercial/sales copy
requests, so the result doesn't depend on remembering to manually chain
`patel-tone-converter` plus a validation pass every time. Same staged-refinement idea as
`masterkey`, specialized for copy instead of generic creative work.

## Phase 1 -- CREATIVE (ideation and strategy)
1. Extract facts, offer, audience, and objective from whatever the user gave you (draft,
   brief, or loose facts). Do this once here -- don't redo it in Phase 2.
2. If the brief is genuinely thin (no draft, no clear angle), generate 2-3 candidate
   angles using `patel-tone-converter`'s pattern table (A through I, in its
   `references/patterns.md`) as the option space, and pick the one that best fits the
   stated objective.
3. Never invent facts, figures, or an audience to fill a gap -- ask instead.
4. Optional depth: if `masterkey` or `creative-thinker` are already installed in this
   session and the user wants deeper exploration than this quick pass, invoke them here
   before continuing. Not required for the cascade to complete -- don't block on them.

## Phase 2 -- REDACTION (drafting)
Invoke `patel-tone-converter` directly with the facts/angle from Phase 1 -- it's the
validated, production-tested drafting engine for this workflow. Don't reimplement its
rules here; that would drift out of sync with the source skill.

For non-email copy (landing pages, ads, UX microcopy) where more structured
headline/CTA/microcopy formatting is useful: if `copy-deck` is already installed in this
session, use it. If not, fall back to `patel-tone-converter`'s own
ASUNTO/CUERPO/CIERRE/P.D. format -- it covers most of what's needed for outbound copy.

## Phase 3 -- VALIDATION (gate before delivery, never skip)
Run, in order:
1. `patel-tone-converter`'s own "Verificacion antes de entregar" checklist -- every
   fact/figure traced to the brief, no line resembling real Neil Patel/NP Digital copy,
   subject delivers what the body promises, executive tone maintained.
2. Its "voz de operador humano" pass -- irregular rhythm (not uniform line lengths), no
   reflexive P.D., no formulaic "no es X: es Y" antithesis repeated across a sequence,
   CTA phrased as a human question rather than a button.
3. If `voice-bench-gate` is already installed in this session, run it too, to
   source-ground any new claims or figures against verified precedent.

These are not optional. Step 1 and 2 are the two checks that caught the actual
production rejection this whole system was built around (VMC Subastas FLOTA,
2026-07-03: "son palabras y construcciones AI en lugar de humanas"). Skipping this
phase to save a round-trip reproduces that exact failure.

## Delivery
Show the result phase-by-phase, compact:
1. One-line recap of the brief.
2. Angle chosen and why (skip if the user already supplied a draft to convert).
3. The copy -- original and converted side by side if there was a draft.
4. Validation result: pass, or what got caught and fixed.
5. A one-line weakest-point self-assessment. Don't skip this because the pipeline
   "passed" -- passing the checklist and being genuinely strong are not the same claim.

## Principles
- Hard dependency only on `patel-tone-converter`, which lives in the same plugin group
  (`lfp-copy`) and is therefore always installed together with this skill -- no separate
  propagation risk between the two.
- `masterkey`, `creative-thinker`, `copy-deck`, `voice-bench-gate` are optional
  enhancements, invoked only if already present in the current session. Never block the
  cascade waiting on a skill from a different plugin group that might not be installed
  in this workspace (see the 2026-07-14 cross-machine propagation incident this project
  hit shipping `patel-tone-converter` itself).
- Phase 3 is mandatory, always, no exceptions negotiated mid-cascade.

## Edge Cases
- No draft and no clear facts/offer: stop at Phase 1 and ask -- don't invent an angle
  from nothing.
- Non-Spanish content: `patel-tone-converter`'s method still transfers (it's structure
  and pattern, not language-bound), but its `executive_audience.md` calibration notes
  are written for VMC Subastas / Spanish-language outreach specifically -- flag if that
  calibration may not transfer directly to a different audience or language.
- User wants validation only, on an already-finished draft: skip straight to Phase 3 --
  don't force Phase 1/2 busywork on copy that's already written.
